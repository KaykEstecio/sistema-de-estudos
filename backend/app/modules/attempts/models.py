"""Persistência de tentativas; transições e ownership pertencem ao service."""

from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Identity, Index, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_attempts_user", ondelete="RESTRICT"))
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", name="fk_attempts_challenge", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS", server_default="IN_PROGRESS")
    draft_answer: Mapped[str] = mapped_column(String(20000), default="", server_default="")
    attempt_number: Mapped[int]
    challenge_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('IN_PROGRESS','SUBMITTED')", name="ck_attempts_status"),
        CheckConstraint("attempt_number > 0", name="ck_attempts_number"),
        CheckConstraint("jsonb_typeof(challenge_snapshot) = 'object'", name="ck_attempts_snapshot"),
        CheckConstraint("(status = 'IN_PROGRESS' AND submitted_at IS NULL) OR (status = 'SUBMITTED' AND submitted_at IS NOT NULL)", name="ck_attempts_submission"),
        CheckConstraint("last_activity_at >= started_at AND (submitted_at IS NULL OR submitted_at >= started_at)", name="ck_attempts_dates"),
        UniqueConstraint("user_id", "challenge_id", "attempt_number", name="uq_attempts_number"),
        Index("uq_attempts_open", "user_id", "challenge_id", unique=True, postgresql_where=text("status = 'IN_PROGRESS'")),
        Index("ix_attempts_challenge_id", "challenge_id"),
    )
