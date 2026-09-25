"""Consultas e gravações sem commit; o service escolhe acesso e valida domínio."""

from collections.abc import Sequence

from sqlalchemy import Select, delete, func, select
from sqlalchemy.orm import Session

from app.modules.challenges.models import Challenge, ChallengeSkill
from app.modules.challenges.schemas import ChallengeCreate, ChallengeUpdate, ChallengeSkillInput
from app.modules.skills.models import Skill


class ChallengeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _visible(self, statement: Select[tuple[Challenge]]) -> Select[tuple[Challenge]]:
        has_skills = select(ChallengeSkill.challenge_id).where(ChallengeSkill.challenge_id == Challenge.id).exists()
        has_inactive = select(ChallengeSkill.challenge_id).join(Skill, Skill.id == ChallengeSkill.skill_id).where(
            ChallengeSkill.challenge_id == Challenge.id, Skill.is_active.is_(False)
        ).exists()
        return statement.where(Challenge.is_active.is_(True), has_skills, ~has_inactive)

    def get_by_id(self, challenge_id: int, *, visible_only: bool = False) -> Challenge | None:
        statement = select(Challenge).where(Challenge.id == challenge_id)
        if visible_only:
            statement = self._visible(statement)
        return self.session.scalar(statement.execution_options(populate_existing=True))

    def get_locked(self, challenge_id: int) -> Challenge | None:
        return self.session.scalar(select(Challenge).where(Challenge.id == challenge_id)
                                   .with_for_update().execution_options(populate_existing=True))

    def get_skills_locked(self, skill_ids: Sequence[int]) -> list[Skill]:
        return list(self.session.scalars(select(Skill).where(Skill.id.in_(skill_ids)).order_by(Skill.id)
                                        .with_for_update(read=True).execution_options(populate_existing=True)))

    def list_page(self, *, limit: int, offset: int, visible_only: bool = False,
                  skill: int | None = None, difficulty: str | None = None,
                  challenge_type: str | None = None, is_active: bool | None = None) -> tuple[list[Challenge], int]:
        statement = select(Challenge)
        if visible_only:
            statement = self._visible(statement)
        if skill is not None:
            statement = statement.where(select(ChallengeSkill.challenge_id).where(
                ChallengeSkill.challenge_id == Challenge.id, ChallengeSkill.skill_id == skill).exists())
        if difficulty is not None:
            statement = statement.where(Challenge.difficulty == difficulty)
        if challenge_type is not None:
            statement = statement.where(Challenge.challenge_type == challenge_type)
        if is_active is not None:
            statement = statement.where(Challenge.is_active == is_active)
        total = self.session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        items = list(self.session.scalars(statement.order_by(Challenge.id).limit(limit).offset(offset)
                                         .execution_options(populate_existing=True)))
        return items, total

    def get_links(self, challenge_ids: Sequence[int]) -> dict[int, list[ChallengeSkill]]:
        grouped: dict[int, list[ChallengeSkill]] = {key: [] for key in challenge_ids}
        if not challenge_ids:
            return grouped
        links = self.session.scalars(select(ChallengeSkill).where(ChallengeSkill.challenge_id.in_(challenge_ids))
            .order_by(ChallengeSkill.challenge_id, ChallengeSkill.skill_id).execution_options(populate_existing=True))
        for link in links:
            grouped[link.challenge_id].append(link)
        return grouped

    def _replace_links(self, challenge_id: int, skills: Sequence[ChallengeSkillInput]) -> None:
        self.session.execute(delete(ChallengeSkill).where(ChallengeSkill.challenge_id == challenge_id))
        self.session.add_all([ChallengeSkill(challenge_id=challenge_id, skill_id=item.skill_id, weight=item.weight)
                              for item in skills])

    def create(self, data: ChallengeCreate) -> Challenge:
        challenge = Challenge(**data.model_dump(exclude={"skills"}))
        self.session.add(challenge)
        self.session.flush()
        self._replace_links(challenge.id, data.skills)
        self.session.flush()
        return challenge

    def update(self, challenge: Challenge, data: ChallengeUpdate) -> Challenge:
        for field, value in data.model_dump(exclude_unset=True, exclude={"skills"}).items():
            setattr(challenge, field, value)
        if data.skills is not None:
            self._replace_links(challenge.id, data.skills)
        challenge.updated_at = func.now()
        self.session.flush()
        return challenge
