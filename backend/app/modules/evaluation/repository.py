"""Consultas e flush; o service coordena a transação."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.attempts.models import ChallengeAttempt
from app.modules.users.models import User
from app.modules.evaluation.models import AttemptEvaluation, AttemptEvaluationSkill
from app.modules.evaluation.schemas import EvaluationCreate


class EvaluationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(self, user_id: int) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id).execution_options(populate_existing=True))

    def get_attempt(self, attempt_id: int, *, owner_id: int | None = None, lock: bool = False) -> ChallengeAttempt | None:
        query = select(ChallengeAttempt).where(ChallengeAttempt.id == attempt_id)
        if owner_id is not None:
            query = query.where(ChallengeAttempt.user_id == owner_id)
        if lock:
            query = query.with_for_update()
        return self.session.scalar(query.execution_options(populate_existing=True))

    def get_evaluation(self, attempt_id: int) -> AttemptEvaluation | None:
        return self.session.scalar(select(AttemptEvaluation).where(AttemptEvaluation.attempt_id == attempt_id).execution_options(populate_existing=True))

    def get_skills(self, evaluation_id: int) -> list[AttemptEvaluationSkill]:
        return list(self.session.scalars(select(AttemptEvaluationSkill).where(AttemptEvaluationSkill.evaluation_id == evaluation_id).order_by(AttemptEvaluationSkill.skill_id)))

    def create(self, attempt_id: int, reviewer_id: int, data: EvaluationCreate) -> AttemptEvaluation:
        evaluation = AttemptEvaluation(attempt_id=attempt_id, reviewer_id=reviewer_id, feedback=data.feedback)
        self.session.add(evaluation)
        self.session.flush()
        self.session.add_all([AttemptEvaluationSkill(evaluation_id=evaluation.id, **item.model_dump()) for item in data.skills])
        self.session.flush()
        return evaluation
