from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.auth_service import AuthService
from app.modules.study.repository import StudyRepository
from app.modules.study.schemas import StudyCreate, StudyQuery, StudyRead, StudyPage, StudySummary


class StudyNotFound(Exception):
    pass


class StudyService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = StudyRepository(session)

    def list_page(self, user: User, query: StudyQuery) -> StudyPage:
        rows, total = self.repository.list_page(user.id, query)
        return StudyPage(items=[StudySummary.model_validate(row) for row in rows], total=total, limit=query.limit, offset=query.offset)

    def get(self, user: User, content_id: int) -> StudyRead:
        row = self.repository.get(user.id, content_id)
        if row is None:
            raise StudyNotFound()
        return StudyRead.model_validate(row)

    def create(self, user: User, data: StudyCreate) -> StudyRead:
        AuthService.require_admin(user)
        try:
            if self.repository.active_skill(data.skill_id) is None:
                raise StudyNotFound()
            content = self.repository.create(data)
            result = self.get(user, content.id)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback(); raise

    def complete(self, user: User, content_id: int) -> StudyRead:
        try:
            content = self.get(user, content_id)
            if self.repository.active_skill(content.skill_id) is None:
                raise StudyNotFound()
            self.repository.complete(user.id, content_id)
            result = self.get(user, content_id)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback(); raise
