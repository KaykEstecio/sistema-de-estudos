"""Visibilidade do catálogo conforme a role autenticada."""

from sqlalchemy.orm import Session
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
