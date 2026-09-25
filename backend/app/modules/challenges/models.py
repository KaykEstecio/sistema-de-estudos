"""Persistência de conteúdo; pesos totais e publicação pertencem ao service."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Identity, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(20000))
    challenge_type: Mapped[str] = mapped_column(String(20))
    difficulty: Mapped[str] = mapped_column(String(20))
    difficulty_score: Mapped[int]
    estimated_minutes: Mapped[int]
    starter_code: Mapped[str | None] = mapped_column(String(20000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("char_length(btrim(title)) BETWEEN 1 AND 200", name="ck_challenges_title"),
        CheckConstraint("char_length(btrim(description)) BETWEEN 1 AND 20000", name="ck_challenges_description"),
        CheckConstraint("challenge_type IN ('QUIZ','CODE','BUG_FIX','CODE_READING','REFACTORING','SQL','API','ARCHITECTURE','PROJECT')", name="ck_challenges_type"),
        CheckConstraint("difficulty IN ('VERY_EASY','EASY','MEDIUM','HARD','VERY_HARD')", name="ck_challenges_difficulty"),
        CheckConstraint("difficulty_score BETWEEN 0 AND 1000", name="ck_challenges_score"),
        CheckConstraint("estimated_minutes BETWEEN 1 AND 1440", name="ck_challenges_minutes"),
        Index("ix_challenges_active_id", "is_active", "id"),
    )


class ChallengeSkill(Base):
    __tablename__ = "challenge_skills"

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", name="fk_challenge_skills_challenge", ondelete="RESTRICT"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", name="fk_challenge_skills_skill", ondelete="RESTRICT"), primary_key=True
    )
    weight: Mapped[int]

    __table_args__ = (
        CheckConstraint("weight BETWEEN 1 AND 100", name="ck_challenge_skills_weight"),
        Index("ix_challenge_skills_skill_id", "skill_id"),
    )
