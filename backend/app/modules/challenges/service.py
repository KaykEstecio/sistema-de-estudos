"""Regras do catálogo; não avalia tentativas nem atualiza habilidades."""

from sqlalchemy.orm import Session

from app.modules.challenges.models import Challenge, ChallengeSkill
from app.modules.challenges.repository import ChallengeRepository
from app.modules.challenges.schemas import ChallengeCreate, ChallengeUpdate, ChallengeRead, ChallengeSkillRead, ChallengeListQuery, ChallengePage
from app.modules.skills.service import SkillNotFound
from app.modules.users.auth_service import PermissionDenied
from app.modules.users.models import UserRole


class ChallengeNotFound(Exception):
    pass


class ChallengeConflict(Exception):
    pass


class ChallengeService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ChallengeRepository(session)

    def _read(self, item: Challenge, links: list[ChallengeSkill]) -> ChallengeRead:
        fields = {name: getattr(item, name) for name in ChallengeRead.model_fields if name != "skills"}
        return ChallengeRead(**fields, skills=[ChallengeSkillRead.model_validate(link) for link in links])

    def get(self, challenge_id: int, role: UserRole) -> ChallengeRead:
        item = self.repository.get_by_id(challenge_id, visible_only=role != UserRole.ADMIN)
        if item is None:
            raise ChallengeNotFound()
        return self._read(item, self.repository.get_links([item.id])[item.id])

    def list_page(self, query: ChallengeListQuery, role: UserRole) -> ChallengePage:
        if role != UserRole.ADMIN and query.is_active is False:
            raise PermissionDenied()
        items, total = self.repository.list_page(**query.model_dump(), visible_only=role != UserRole.ADMIN)
        links = self.repository.get_links([item.id for item in items])
        return ChallengePage(items=[self._read(item, links[item.id]) for item in items],
                             total=total, limit=query.limit, offset=query.offset)

    def create(self, data: ChallengeCreate) -> ChallengeRead:
        return self._write(data)

    def update(self, challenge_id: int, data: ChallengeUpdate) -> ChallengeRead:
        return self._write(data, challenge_id)

    def _write(self, data: ChallengeCreate | ChallengeUpdate, challenge_id: int | None = None) -> ChallengeRead:
        try:
            item = None
            if isinstance(data, ChallengeUpdate):
                assert challenge_id is not None
                item = self.repository.get_locked(challenge_id)
                if item is None:
                    raise ChallengeNotFound()
                links = data.skills if data.skills is not None else self.repository.get_links([item.id])[item.id]
                active = data.is_active if data.is_active is not None else item.is_active
            else:
                links, active = data.skills, data.is_active
            if not links or sum(link.weight for link in links) != 100:
                raise ChallengeConflict("Os pesos devem somar 100%.")
            ids = [link.skill_id for link in links]
            skills = self.repository.get_skills_locked(ids)
            if {skill.id for skill in skills} != set(ids):
                raise SkillNotFound()
            if active and any(not skill.is_active for skill in skills):
                raise ChallengeConflict("Publicação exige skills ativas.")
            if isinstance(data, ChallengeCreate):
                item = self.repository.create(data)
            else:
                assert item is not None
                self.repository.update(item, data)
            result = self._read(item, self.repository.get_links([item.id])[item.id])
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise
