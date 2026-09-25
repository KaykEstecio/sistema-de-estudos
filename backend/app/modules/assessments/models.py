"""Provas, conteúdo privado e resultados; sem atualização de UserSkill."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Identity, Index, Numeric, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_assessments_user", ondelete="RESTRICT"))
    assessment_type: Mapped[str] = mapped_column(String(20), default="INITIAL", server_default="INITIAL")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint("assessment_type = 'INITIAL'", name="ck_assessments_type"),
        Index("ix_assessments_user_id", "user_id"),
        Index("uq_assessments_open_user", "user_id", unique=True, postgresql_where=text("completed_at IS NULL")),
    )


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    code: Mapped[str] = mapped_column(String(120))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", name="fk_assessment_questions_skill", ondelete="RESTRICT"))
    prompt: Mapped[str] = mapped_column(String(4000))
    options: Mapped[dict[str, str]] = mapped_column(JSONB)
    correct_option: Mapped[str] = mapped_column(String(1))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    __table_args__ = (
        UniqueConstraint("code", name="uq_assessment_questions_code"),
        CheckConstraint("code ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="ck_assessment_questions_code"),
        CheckConstraint("correct_option IN ('A','B','C','D')", name="ck_assessment_questions_correct"),
        Index("ix_assessment_questions_skill_id", "skill_id"),
    )


class AssessmentItem(Base):
    __tablename__ = "assessment_items"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id", name="fk_assessment_items_assessment", ondelete="RESTRICT"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", name="fk_assessment_items_skill", ondelete="RESTRICT"))
    position: Mapped[int]
    prompt: Mapped[str] = mapped_column(String(4000))
    options: Mapped[dict[str, str]] = mapped_column(JSONB)
    correct_option: Mapped[str] = mapped_column(String(1))
    selected_option: Mapped[str | None] = mapped_column(String(1))
    __table_args__ = (
        UniqueConstraint("assessment_id", "position", name="uq_assessment_items_position"),
        CheckConstraint("position > 0", name="ck_assessment_items_position"),
        CheckConstraint("correct_option IN ('A','B','C','D')", name="ck_assessment_items_correct"),
        CheckConstraint("selected_option IN ('A','B','C','D')", name="ck_assessment_items_selected"),
        Index("ix_assessment_items_skill_id", "skill_id"),
    )


class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id", name="fk_assessment_results_assessment", ondelete="RESTRICT"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", name="fk_assessment_results_skill", ondelete="RESTRICT"))
    score: Mapped[int]
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3))
    correct_count: Mapped[int]
    question_count: Mapped[int]
    __table_args__ = (
        UniqueConstraint("assessment_id", "skill_id", name="uq_assessment_results_skill"),
        CheckConstraint("score BETWEEN 0 AND 1000", name="ck_assessment_results_score"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_assessment_results_confidence"),
        CheckConstraint("question_count > 0 AND correct_count >= 0 AND correct_count <= question_count", name="ck_assessment_results_counts"),
        Index("ix_assessment_results_skill_id", "skill_id"),
    )
