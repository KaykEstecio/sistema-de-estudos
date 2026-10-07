from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.auth_service import AuthService
from app.modules.study.repository import StudyRepository
from app.modules.study.schemas import StudyCreate, StudyQuery, StudyRead, StudyPage, StudySummary
from app.modules.challenges.repository import ChallengeRepository
from app.modules.challenges.service import ChallengeService, ChallengeConflict
from app.modules.challenges.schemas import ChallengeRead
from app.modules.users.models import UserRole


class StudyNotFound(Exception):
    pass


class StudyService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = StudyRepository(session)

    def list_page(self, user: User, query: StudyQuery) -> StudyPage:
        rows, total = self.repository.list_page(user.id, query)
        has_sequence, next_row = self.repository.guidance(user.id, query.skill_id) if query.skill_id is not None else (False, None)
        return StudyPage(items=[StudySummary.model_validate(row) for row in rows], total=total, limit=query.limit, offset=query.offset,
                         has_sequence=has_sequence, next_content=StudySummary.model_validate(next_row) if next_row is not None else None)

    def set_order(self, user: User, content_id: int, study_order: int | None) -> StudyRead:
        AuthService.require_admin(user)
        try:
            content = self.repository.content(content_id, lock=True)
            if content is None or self.repository.active_skill(content.skill_id) is None:
                raise StudyNotFound()
            self.repository.set_order(content, study_order)
            result = self.get(user, content_id)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback(); raise

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

    def practice(self, user: User, content_id: int) -> ChallengeRead | None:
        self.get(user, content_id)
        content = self.repository.content(content_id)
        if content is None or content.challenge_id is None:
            return None
        repository = ChallengeRepository(self.session)
        challenge = repository.get_by_id(content.challenge_id, visible_only=True)
        if challenge is None:
            return None
        links = repository.get_links([challenge.id])[challenge.id]
        if not any(link.skill_id == content.skill_id for link in links):
            return None
        return ChallengeService(self.session).get(challenge.id, UserRole.STUDENT)

    def set_practice(self, user: User, content_id: int, challenge_id: int | None) -> ChallengeRead | None:
        AuthService.require_admin(user)
        try:
            content = self.repository.content(content_id, lock=True)
            if content is None:
                raise StudyNotFound()
            if challenge_id is not None:
                repository = ChallengeRepository(self.session)
                challenge = repository.get_locked(challenge_id)
                if challenge is None or not challenge.is_active:
                    raise ChallengeConflict('Prática indisponível para esta aula.')
                links = repository.get_links([challenge_id])[challenge_id]
                skills = repository.get_skills_locked([link.skill_id for link in links])
                if not any(link.skill_id == content.skill_id for link in links) or any(not skill.is_active for skill in skills):
                    raise ChallengeConflict('Prática indisponível para esta aula.')
            if self.repository.active_skill(content.skill_id) is None:
                raise StudyNotFound()
            self.repository.set_practice(content, challenge_id)
            result = self.practice(user, content_id)
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
