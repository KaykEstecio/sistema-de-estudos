"""Consultas filtradas no banco; visibilidade é decidida pelo service."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.skills.models import Skill
from app.modules.skills.schemas import SkillCreate, SkillUpdate


class SkillRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, skill_id: int) -> Skill | None:
        return self.session.get(Skill, skill_id)

    def list_page(self, *, limit: int, offset: int, category_id: int | None = None,
                  is_active: bool | None = None) -> tuple[list[Skill], int]:
        statement = select(Skill)
        if category_id is not None:
            statement = statement.where(Skill.category_id == category_id)
        if is_active is not None:
            statement = statement.where(Skill.is_active == is_active)
        total = self.session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        items = list(self.session.scalars(statement.order_by(Skill.id).limit(limit).offset(offset)))
        return items, total

    def create(self, data: SkillCreate) -> Skill:
        skill = Skill(**data.model_dump())
        self.session.add(skill)
        self.session.flush()
        return skill

    def update(self, skill: Skill, data: SkillUpdate) -> Skill:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(skill, field, value)
        self.session.flush()
        return skill
