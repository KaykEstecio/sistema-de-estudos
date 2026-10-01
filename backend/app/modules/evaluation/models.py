"""Avaliações manuais; autorização e rubrica são responsabilidade do service."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Identity, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AttemptEvaluation(Base):
    __tablename__ = "attempt_evaluations"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("challenge_attempts.id", name="fk_evaluations_attempt", ondelete="RESTRICT"))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_evaluations_reviewer", ondelete="RESTRICT"))
    rubric_version: Mapped[str] = mapped_column(String(30), default="manual-v1", server_default="manual-v1")
    feedback: Mapped[str] = mapped_column(String(4000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("attempt_id", name="uq_evaluations_attempt"),
        CheckConstraint("rubric_version = 'manual-v1'", name="ck_evaluations_rubric"),
        CheckConstraint("feedback ~ '[^[:space:]]'", name="ck_evaluations_feedback"),
        Index("ix_evaluations_reviewer", "reviewer_id"),
    )


class AttemptEvaluationSkill(Base):
    __tablename__ = "attempt_evaluation_skills"

    evaluation_id: Mapped[int] = mapped_column(ForeignKey("attempt_evaluations.id", name="fk_evaluation_skills_evaluation", ondelete="RESTRICT"), primary_key=True)
    # Referência histórica validada contra o snapshot, sem FK ao catálogo mutável.
    skill_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    classification: Mapped[str] = mapped_column(String(30))
    justification: Mapped[str] = mapped_column(String(2000))

    __table_args__ = (
        CheckConstraint("skill_id > 0", name="ck_evaluation_skills_id"),
        CheckConstraint("classification IN ('NOT_MET','PARTIALLY_MET','MET','INSUFFICIENT_EVIDENCE')", name="ck_evaluation_skills_classification"),
        CheckConstraint("justification ~ '[^[:space:]]'", name="ck_evaluation_skills_justification"),
    )
