"""Persistência do progresso; sem commit próprio."""

from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.assessments.models import Assessment, AssessmentResult
from app.modules.skills.progress_models import UserSkill, SkillEvidence


class ProgressRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_owned(self, user_id: int, limit: int, offset: int) -> tuple[list[UserSkill], int]:
        query = select(UserSkill).where(UserSkill.user_id == user_id)
        total = self.session.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = list(self.session.scalars(query.order_by(UserSkill.skill_id).limit(limit).offset(offset)))
        return items, total

    def lock_user(self, user_id: int) -> None:
        # NO KEY UPDATE serializa progresso sem bloquear referências FK ao usuário.
        self.session.execute(select(User.id).where(User.id == user_id)
                             .with_for_update(key_share=True)).scalar_one()

    def get(self, user_id: int, skill_id: int) -> UserSkill | None:
        return self.session.scalar(select(UserSkill).where(
            UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
            .execution_options(populate_existing=True))

    def initial_result(self, user_id: int, skill_id: int, started_at: datetime) -> AssessmentResult | None:
        return self.session.scalar(select(AssessmentResult).join(Assessment).where(
            Assessment.user_id == user_id, Assessment.completed_at < started_at,
            AssessmentResult.skill_id == skill_id).order_by(
                Assessment.completed_at.desc(), Assessment.id.desc()).limit(1))

    def save(self, progress: UserSkill | None, evidence: SkillEvidence) -> None:
        if progress is not None:
            self.session.add(progress)
        self.session.add(evidence)
        self.session.flush()
