from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Identity, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class StudyContent(Base):
    __tablename__ = "study_contents"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"))
    challenge_id: Mapped[int | None] = mapped_column(ForeignKey("challenges.id", name="fk_study_practice", ondelete="RESTRICT"))
    study_order: Mapped[int | None]
    title: Mapped[str] = mapped_column(String(200))
    explanation: Mapped[str] = mapped_column(String(12000))
    code_example: Mapped[str] = mapped_column(String(12000))
    common_mistakes: Mapped[str] = mapped_column(String(6000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        CheckConstraint('study_order BETWEEN 1 AND 10000', name='ck_study_order'),
        Index("ix_study_contents_skill_id", "skill_id"),
        CheckConstraint("char_length(btrim(title)) BETWEEN 1 AND 200", name="ck_study_title"),
        CheckConstraint("char_length(btrim(explanation)) BETWEEN 1 AND 12000", name="ck_study_explanation"),
        CheckConstraint("char_length(btrim(code_example)) BETWEEN 1 AND 12000", name="ck_study_example"),
        CheckConstraint("char_length(btrim(common_mistakes)) BETWEEN 1 AND 6000", name="ck_study_mistakes"),
    )


class StudyCompletion(Base):
    __tablename__ = "study_completions"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("study_contents.id", ondelete="RESTRICT"), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
