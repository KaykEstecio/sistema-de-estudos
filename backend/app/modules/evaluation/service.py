"""Revisão manual e progresso atômicos, preservando a tentativa original."""

from sqlalchemy.orm import Session
from app.modules.skills.service import SkillService
from app.modules.users.auth_service import AuthService, InvalidCredentials, PermissionDenied
from app.modules.attempts.schemas import AttemptRead, ChallengeSnapshot
from app.modules.attempts.models import ChallengeAttempt
from app.modules.evaluation.models import AttemptEvaluation
from app.modules.evaluation.repository import EvaluationRepository
from app.modules.evaluation.schemas import EvaluationCreate, EvaluationRead, EvaluationSkillInput, ReviewRead


class EvaluationNotFound(Exception):
    """Recurso indisponível para esta identidade."""


class EvaluationConflict(Exception):
    """Estado incompatível com a operação."""


class EvaluationSkillsMismatch(Exception):
    """Resultados não correspondem às skills históricas da tentativa."""


class EvaluationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = EvaluationRepository(session)

    def _review_attempt(self, reviewer_id: int, attempt_id: int, *, lock: bool = False) -> ChallengeAttempt:
        reviewer = self.repository.get_user(reviewer_id)
        if reviewer is None:
            raise InvalidCredentials()
        AuthService.require_admin(reviewer)
        attempt = self.repository.get_attempt(attempt_id, lock=lock)
        if attempt is None:
            raise EvaluationNotFound()
        if attempt.user_id == reviewer_id:
            raise PermissionDenied()
        if attempt.status != "SUBMITTED":
            raise EvaluationConflict("Tentativa ainda não submetida.")
        return attempt

    def _read(self, evaluation: AttemptEvaluation) -> EvaluationRead:
        return EvaluationRead(id=evaluation.id, attempt_id=evaluation.attempt_id,
            rubric_version=evaluation.rubric_version, feedback=evaluation.feedback,
            skills=[EvaluationSkillInput.model_validate(item) for item in self.repository.get_skills(evaluation.id)],
            created_at=evaluation.created_at)

    def review(self, reviewer_id: int, attempt_id: int) -> ReviewRead:
        attempt = self._review_attempt(reviewer_id, attempt_id)
        evaluation = self.repository.get_evaluation(attempt_id)
        return ReviewRead(attempt=AttemptRead.model_validate(attempt), evaluation=self._read(evaluation) if evaluation else None)

    def get_owned(self, user_id: int, attempt_id: int) -> EvaluationRead:
        if self.repository.get_attempt(attempt_id, owner_id=user_id) is None:
            raise EvaluationNotFound()
        evaluation = self.repository.get_evaluation(attempt_id)
        if evaluation is None:
            raise EvaluationNotFound()
        return self._read(evaluation)

    def evaluate(self, reviewer_id: int, attempt_id: int, data: EvaluationCreate) -> tuple[EvaluationRead, bool]:
        try:
            attempt = self._review_attempt(reviewer_id, attempt_id, lock=True)
            snapshot = ChallengeSnapshot.model_validate(attempt.challenge_snapshot)
            if {item.skill_id for item in data.skills} != {item.skill_id for item in snapshot.skills}:
                raise EvaluationSkillsMismatch()
            existing = self.repository.get_evaluation(attempt_id)
            if existing is not None:
                result = self._read(existing)
                if existing.reviewer_id != reviewer_id or result.feedback != data.feedback or result.skills != data.skills:
                    raise EvaluationConflict("Esta tentativa já possui uma avaliação diferente ou de outro revisor.")
                self.session.commit()
                return result, False
            evaluation = self.repository.create(attempt_id, reviewer_id, data)
            SkillService(self.session).apply_evaluation(attempt, evaluation, data)
            result = self._read(evaluation)
            self.session.commit()
            return result, True
        except Exception:
            self.session.rollback()
            raise
