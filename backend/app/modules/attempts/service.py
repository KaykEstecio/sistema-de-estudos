"""Tentativas com contexto estável e acesso exclusivo do dono, sem avaliação."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.attempts.repository import AttemptRepository
from app.modules.attempts.schemas import AttemptDraft, AttemptRead, ChallengeSnapshot, AttemptPage, AttemptQuery, AttemptSummary
from app.modules.challenges.repository import ChallengeRepository
from app.modules.users.auth_service import InvalidCredentials


class AttemptNotFound(Exception):
    pass


class AttemptConflict(Exception):
    pass


class AttemptService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AttemptRepository(session)
        self.challenges = ChallengeRepository(session)

    def list_owned(self, user_id: int, query: AttemptQuery) -> AttemptPage:
        rows, total = self.repository.list_owned(user_id, query.limit, query.offset)
        return AttemptPage(items=[AttemptSummary.model_validate(row) for row in rows],
                           total=total, limit=query.limit, offset=query.offset)

    def start(self, user_id: int, challenge_id: int) -> tuple[AttemptRead, bool]:
        try:
            if self.repository.get_user_locked(user_id) is None:
                raise InvalidCredentials()
            attempt = self.repository.get_open_locked(user_id, challenge_id)
            created = attempt is None
            if attempt is None:
                challenge = self.repository.get_challenge_locked(challenge_id)
                if challenge is None or not challenge.is_active:
                    raise AttemptNotFound()
                links = self.challenges.get_links([challenge_id])[challenge_id]
                skills = self.challenges.get_skills_locked([link.skill_id for link in links])
                if not links or len(skills) != len(links) or any(not skill.is_active for skill in skills):
                    raise AttemptNotFound()
                number = self.repository.last_number(user_id, challenge_id) + 1
                if number > 2147483647:
                    raise AttemptConflict("Limite de tentativas atingido.")
                fields = {name: getattr(challenge, name) for name in ChallengeSnapshot.model_fields if name != "skills"}
                snapshot = ChallengeSnapshot(**fields, skills=[dict(skill_id=link.skill_id, weight=link.weight) for link in links])
                attempt = self.repository.create(user_id, challenge_id, number, snapshot, datetime.now(timezone.utc))
            result = AttemptRead.model_validate(attempt)
            self.session.commit()
            return result, created
        except Exception:
            self.session.rollback()
            raise

    def get(self, user_id: int, attempt_id: int) -> AttemptRead:
        attempt = self.repository.get_owned(attempt_id, user_id)
        if attempt is None:
            raise AttemptNotFound()
        return AttemptRead.model_validate(attempt)

    def save_draft(self, user_id: int, attempt_id: int, data: AttemptDraft) -> AttemptRead:
        try:
            attempt = self.repository.get_owned(attempt_id, user_id, lock=True)
            if attempt is None:
                raise AttemptNotFound()
            if attempt.status != "IN_PROGRESS":
                raise AttemptConflict("Tentativa já submetida.")
            if attempt.draft_answer != data.draft_answer:
                self.repository.save_draft(attempt, data.draft_answer, datetime.now(timezone.utc))
            result = AttemptRead.model_validate(attempt)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise

    def submit(self, user_id: int, attempt_id: int) -> AttemptRead:
        try:
            attempt = self.repository.get_owned(attempt_id, user_id, lock=True)
            if attempt is None:
                raise AttemptNotFound()
            if attempt.status == "IN_PROGRESS":
                if not attempt.draft_answer.strip():
                    raise AttemptConflict("Salve uma resposta antes de submeter.")
                self.repository.submit(attempt, datetime.now(timezone.utc))
            result = AttemptRead.model_validate(attempt)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise
