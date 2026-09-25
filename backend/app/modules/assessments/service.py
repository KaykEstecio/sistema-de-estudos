"""Ciclo de vida do diagnóstico; não calcula resultados ou domínio."""

from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from app.modules.assessments.evaluation import evaluate
from app.modules.assessments.models import AssessmentResult
from sqlalchemy.orm import Session
from app.modules.assessments.models import Assessment
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.schemas import AssessmentCreate, AssessmentRead, AssessmentItemRead, AssessmentResultRead, AnswerCreate
from app.modules.users.auth_service import InvalidCredentials

QUESTIONS_PER_SKILL = 3


class AssessmentNotFound(Exception):
    pass


class AssessmentConflict(Exception):
    pass


class AssessmentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AssessmentRepository(session)

    def _read(self, assessment: Assessment) -> AssessmentRead:
        return AssessmentRead(id=assessment.id, assessment_type=assessment.assessment_type,
            started_at=assessment.started_at, completed_at=assessment.completed_at,
            items=[AssessmentItemRead.model_validate(item) for item in self.repository.get_items(assessment.id)],
            results=[AssessmentResultRead.model_validate(result) for result in self.repository.get_results(assessment.id)]
                    if assessment.completed_at is not None else [])

    def get(self, user_id: int, assessment_id: int) -> AssessmentRead:
        assessment = self.repository.get_owned_locked(assessment_id, user_id, read=True)
        if assessment is None:
            raise AssessmentNotFound("Diagnóstico não encontrado.")
        return self._read(assessment)

    def create(self, user_id: int, data: AssessmentCreate) -> AssessmentRead:
        try:
            user = self.repository.get_user_locked(user_id)
            if user is None:
                raise InvalidCredentials()
            if not user.onboarding_completed:
                raise AssessmentConflict("Conclua o onboarding antes do diagnóstico.")
            if self.repository.get_open(user_id) is not None:
                raise AssessmentConflict("Já existe um diagnóstico aberto.")
            if self.repository.eligible_skill_ids(user_id, data.skill_ids) != set(data.skill_ids):
                raise AssessmentNotFound("Skill indisponível para diagnóstico.")
            questions = []
            for skill_id in sorted(data.skill_ids):
                selected = self.repository.get_questions(skill_id, limit=QUESTIONS_PER_SKILL)
                if len(selected) != QUESTIONS_PER_SKILL:
                    raise AssessmentConflict("Conteúdo insuficiente para diagnóstico.")
                questions.extend(selected)
            assessment = self.repository.create(user_id, questions)
            result = self._read(assessment)
            self.session.commit()
            return result
        except IntegrityError as exc:
            self.session.rollback()
            if (getattr(exc.orig, "sqlstate", None) == "23505" and
                getattr(getattr(exc.orig, "diag", None), "constraint_name", None) == "uq_assessments_open_user"):
                raise AssessmentConflict("Já existe um diagnóstico aberto.") from None
            raise
        except Exception:
            self.session.rollback()
            raise

    def answer(self, user_id: int, assessment_id: int, data: AnswerCreate) -> AssessmentItemRead:
        try:
            assessment = self.repository.get_owned_locked(assessment_id, user_id)
            if assessment is None:
                raise AssessmentNotFound("Diagnóstico não encontrado.")
            if assessment.completed_at is not None:
                raise AssessmentConflict("Diagnóstico já concluído.")
            item = self.repository.get_item(assessment_id, data.item_id)
            if item is None:
                raise AssessmentNotFound("Item não encontrado neste diagnóstico.")
            self.repository.save_answer(item, data.selected_option)
            result = AssessmentItemRead.model_validate(item)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise

    def finish(self, user_id: int, assessment_id: int) -> AssessmentRead:
        try:
            assessment = self.repository.get_owned_locked(assessment_id, user_id)
            if assessment is None:
                raise AssessmentNotFound("Diagnóstico não encontrado.")
            if assessment.completed_at is not None:
                result = self._read(assessment)
                self.session.commit()
                return result
            items = self.repository.get_items(assessment.id)
            if not items or any(item.selected_option is None for item in items):
                raise AssessmentConflict("Responda todos os itens antes de finalizar.")
            results = [AssessmentResult(assessment_id=assessment.id, skill_id=value.skill_id,
                score=value.score, confidence=value.confidence, correct_count=value.correct_count,
                question_count=value.question_count) for value in evaluate(items)]
            self.repository.finish(assessment, results, datetime.now(timezone.utc))
            result = self._read(assessment)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise
