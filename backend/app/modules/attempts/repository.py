"""Persistência por dono; transações e transições são coordenadas pelo service."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.attempts.models import ChallengeAttempt
from app.modules.attempts.schemas import ChallengeSnapshot
from app.modules.challenges.models import Challenge
from app.modules.users.models import User


class AttemptRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_locked(self, user_id: int) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id).with_for_update()
                                   .execution_options(populate_existing=True))

    def get_challenge_locked(self, challenge_id: int) -> Challenge | None:
        return self.session.scalar(select(Challenge).where(Challenge.id == challenge_id).with_for_update(read=True)
                                   .execution_options(populate_existing=True))

    def get_owned(self, attempt_id: int, user_id: int, *, lock: bool = False) -> ChallengeAttempt | None:
        statement = select(ChallengeAttempt).where(ChallengeAttempt.id == attempt_id, ChallengeAttempt.user_id == user_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement.execution_options(populate_existing=True))

    def get_open_locked(self, user_id: int, challenge_id: int) -> ChallengeAttempt | None:
        return self.session.scalar(select(ChallengeAttempt).where(
            ChallengeAttempt.user_id == user_id, ChallengeAttempt.challenge_id == challenge_id,
            ChallengeAttempt.status == "IN_PROGRESS").with_for_update().execution_options(populate_existing=True))

    def last_number(self, user_id: int, challenge_id: int) -> int:
        return self.session.scalar(select(func.max(ChallengeAttempt.attempt_number)).where(
            ChallengeAttempt.user_id == user_id, ChallengeAttempt.challenge_id == challenge_id)) or 0

    def create(self, user_id: int, challenge_id: int, number: int, snapshot: ChallengeSnapshot,
               started_at: datetime) -> ChallengeAttempt:
        attempt = ChallengeAttempt(user_id=user_id, challenge_id=challenge_id, attempt_number=number,
            challenge_snapshot=snapshot.model_dump(), started_at=started_at, last_activity_at=started_at)
        self.session.add(attempt)
        self.session.flush()
        return attempt

    def save_draft(self, attempt: ChallengeAttempt, answer: str, activity_at: datetime) -> None:
        attempt.draft_answer = answer
        attempt.last_activity_at = activity_at
        self.session.flush()

    def submit(self, attempt: ChallengeAttempt, submitted_at: datetime) -> None:
        attempt.status = "SUBMITTED"
        attempt.submitted_at = submitted_at
        attempt.last_activity_at = submitted_at
        self.session.flush()
