"""Catálogo e aplicação da política de progresso por habilidade."""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal
from app.modules.attempts.models import ChallengeAttempt
from app.modules.attempts.schemas import ChallengeSnapshot
from app.modules.evaluation.models import AttemptEvaluation
from app.modules.evaluation.schemas import EvaluationCreate
from app.modules.skills.progress_repository import ProgressRepository
from app.modules.skills.progress_models import UserSkill, SkillEvidence
from app.modules.skills.progress_schemas import ProgressState, ProgressQuery, UserSkillPage, UserSkillRead
from app.modules.skills.policy import INITIAL_SCORE, POLICY_VERSION, EvidenceTotals, calculate_change
from sqlalchemy.exc import IntegrityError
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.service import CategoryNotFound
from app.modules.skills.schemas import SkillCreate, SkillUpdate
from app.modules.skills.repository import SkillRepository
from app.modules.skills.schemas import SkillListQuery, SkillPage, SkillRead
from app.modules.users.models import UserRole
from app.modules.users.auth_service import PermissionDenied


class SkillNotFound(Exception):
    pass


class SkillSlugConflict(Exception):
    pass


class SkillService:
    def list_owned_progress(self, user_id: int, query: ProgressQuery) -> UserSkillPage:
        items, total = ProgressRepository(self.session).list_owned(user_id, query.limit, query.offset)
        return UserSkillPage(items=[UserSkillRead.model_validate(item) for item in items],
                             total=total, limit=query.limit, offset=query.offset)

    def apply_evaluation(self, attempt: ChallengeAttempt, evaluation: AttemptEvaluation,
                         data: EvaluationCreate) -> None:
        """Chamado somente para avaliação nova, dentro da transação do coordenador."""
        if evaluation.attempt_id != attempt.id or attempt.status != "SUBMITTED" or attempt.submitted_at is None:
            raise ValueError("Avaliação incompatível com a tentativa.")
        snapshot = ChallengeSnapshot.model_validate(attempt.challenge_snapshot)
        weights = {item.skill_id: item.weight for item in snapshot.skills}
        if set(weights) != {item.skill_id for item in data.skills}:
            raise ValueError("Skills incompatíveis com o contexto histórico.")
        repository = ProgressRepository(self.session)
        repository.lock_user(attempt.user_id)
        for item in data.skills:
            evidence = SkillEvidence(user_id=attempt.user_id, skill_id=item.skill_id,
                evaluation_id=evaluation.id, policy_version=POLICY_VERSION, applied=False)
            if item.classification == "INSUFFICIENT_EVIDENCE":
                repository.save(None, evidence)
                continue
            progress = repository.get(attempt.user_id, item.skill_id)
            if progress is None:
                initial = repository.initial_result(attempt.user_id, item.skill_id, attempt.started_at)
                score = initial.score if initial else INITIAL_SCORE
                progress = UserSkill(user_id=attempt.user_id, skill_id=item.skill_id,
                    score=score, initial_score=score, initial_assessment_id=initial.assessment_id if initial else None,
                    confidence=Decimal(0), attempts=0, successful_attempts=0,
                    mass=Decimal(0), residual_sum=Decimal(0), squared_residual_sum=Decimal(0),
                    last_practiced_at=attempt.submitted_at)
            before = ProgressState.model_validate(progress)
            change = calculate_change(progress.score, snapshot.difficulty_score, weights[item.skill_id],
                attempt.attempt_number, item.classification,
                EvidenceTotals(progress.mass, progress.residual_sum, progress.squared_residual_sum))
            progress.score, progress.confidence = change.score, change.confidence
            progress.mass = change.totals.mass
            progress.residual_sum = change.totals.residual_sum
            progress.squared_residual_sum = change.totals.squared_residual_sum
            progress.attempts += 1
            progress.successful_attempts += int(change.successful)
            progress.last_practiced_at = max(progress.last_practiced_at, attempt.submitted_at)
            progress.updated_at = datetime.now(timezone.utc)
            evidence.applied = True
            evidence.before_state = before.model_dump(mode="json")
            evidence.after_state = ProgressState.model_validate(progress).model_dump(mode="json")
            repository.save(progress, evidence)

    def __init__(self, session: Session) -> None:
        self.repository = SkillRepository(session)
        self.session = session

    def create(self, data: SkillCreate) -> SkillRead:
        return self._write(data)

    def update(self, skill_id: int, data: SkillUpdate) -> SkillRead:
        return self._write(data, skill_id)

    def _write(self, data: SkillCreate | SkillUpdate, skill_id: int | None = None) -> SkillRead:
        try:
            skill = None
            if isinstance(data, SkillUpdate):
                assert skill_id is not None
                skill = self.repository.get_by_id(skill_id)
                if skill is None:
                    raise SkillNotFound()
            if data.category_id is not None and CategoryRepository(self.session).get_by_id(data.category_id) is None:
                raise CategoryNotFound()
            if isinstance(data, SkillCreate):
                skill = self.repository.create(data)
            else:
                assert skill is not None
                skill = self.repository.update(skill, data)
            result = SkillRead.model_validate(skill)
            self.session.commit()
            return result
        except IntegrityError as exc:
            self.session.rollback()
            constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            if getattr(exc.orig, "sqlstate", None) == "23505" and constraint == "uq_skills_slug":
                raise SkillSlugConflict() from None
            if getattr(exc.orig, "sqlstate", None) == "23503" and constraint == "fk_skills_category_id":
                raise CategoryNotFound() from None
            raise
        except Exception:
            self.session.rollback()
            raise

    def get(self, skill_id: int, role: UserRole) -> SkillRead:
        skill = self.repository.get_by_id(skill_id)
        if skill is None or (role != UserRole.ADMIN and not skill.is_active):
            raise SkillNotFound()
        return SkillRead.model_validate(skill)

    def list_page(self, query: SkillListQuery, role: UserRole) -> SkillPage:
        active = query.is_active
        if role != UserRole.ADMIN:
            if active is False:
                raise PermissionDenied()
            active = True
        items, total = self.repository.list_page(limit=query.limit, offset=query.offset,
                                                 category_id=query.category_id, is_active=active)
        return SkillPage(items=[SkillRead.model_validate(item) for item in items],
                         total=total, limit=query.limit, offset=query.offset)
