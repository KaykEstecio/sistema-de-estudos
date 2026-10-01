"""Estado individual e trilha de aplicação de evidências."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Identity, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class UserSkill(Base):
    __tablename__ = "user_skills"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_user_skills_user", ondelete="RESTRICT"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", name="fk_user_skills_skill", ondelete="RESTRICT"))
    score: Mapped[int]
    confidence: Mapped[Decimal] = mapped_column(Numeric(7, 6))
    attempts: Mapped[int]
    successful_attempts: Mapped[int]
    initial_score: Mapped[int]
    initial_assessment_id: Mapped[int | None]
    mass: Mapped[Decimal] = mapped_column(Numeric())
    residual_sum: Mapped[Decimal] = mapped_column(Numeric())
    squared_residual_sum: Mapped[Decimal] = mapped_column(Numeric())
    last_practiced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skills_user_skill"),
        ForeignKeyConstraint(["initial_assessment_id", "skill_id"], ["assessment_results.assessment_id", "assessment_results.skill_id"], name="fk_user_skills_initial_result", ondelete="RESTRICT"),
        CheckConstraint("score BETWEEN 0 AND 1000 AND initial_score BETWEEN 0 AND 1000", name="ck_user_skills_scores"),
        CheckConstraint("confidence BETWEEN 0 AND 0.95", name="ck_user_skills_confidence"),
        CheckConstraint("attempts > 0 AND successful_attempts BETWEEN 0 AND attempts", name="ck_user_skills_counts"),
        CheckConstraint("initial_assessment_id IS NOT NULL OR initial_score = 500", name="ck_user_skills_initial"),
        CheckConstraint("mass > 0 AND mass < 'Infinity'::numeric AND residual_sum BETWEEN -mass AND mass AND squared_residual_sum BETWEEN 0 AND mass", name="ck_user_skills_totals"),
        Index("ix_user_skills_skill", "skill_id"),
        Index("ix_user_skills_initial_result", "initial_assessment_id", "skill_id"),
    )


class SkillEvidence(Base):
    __tablename__ = "skill_evidence"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_skill_evidence_user", ondelete="RESTRICT"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", name="fk_skill_evidence_skill", ondelete="RESTRICT"))
    evaluation_id: Mapped[int]
    policy_version: Mapped[str] = mapped_column(String(30))
    applied: Mapped[bool] = mapped_column(Boolean)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB(none_as_null=True))
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB(none_as_null=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("evaluation_id", "skill_id", name="uq_skill_evidence_evaluation_skill"),
        ForeignKeyConstraint(["evaluation_id", "skill_id"], ["attempt_evaluation_skills.evaluation_id", "attempt_evaluation_skills.skill_id"], name="fk_skill_evidence_result", ondelete="RESTRICT"),
        CheckConstraint("policy_version = 'manual-skill-v1'", name="ck_skill_evidence_policy"),
        CheckConstraint("(applied AND before_state IS NOT NULL AND after_state IS NOT NULL AND jsonb_typeof(before_state) = 'object' AND jsonb_typeof(after_state) = 'object') OR (NOT applied AND before_state IS NULL AND after_state IS NULL)", name="ck_skill_evidence_states"),
        Index("ix_skill_evidence_user_skill_order", "user_id", "skill_id", "id"),
        Index("ix_skill_evidence_skill", "skill_id"),
    )
