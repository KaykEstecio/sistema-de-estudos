"""Interesses e objetivo do usuário; regras do fluxo pertencem ao service."""

from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Identity, Index, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class UserInterest(Base):
    __tablename__ = "user_interests"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_user_interests_user", ondelete="RESTRICT"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", name="fk_user_interests_category", ondelete="RESTRICT"))
    priority: Mapped[int] = mapped_column(default=1, server_default=text("1"))
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_user_interests_user_category"),
        CheckConstraint("priority >= 1", name="ck_user_interests_priority"),
        Index("ix_user_interests_category_id", "category_id"),
    )


class UserGoal(Base):
    __tablename__ = "user_goals"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_user_goals_user", ondelete="RESTRICT"))
    goal_type: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(2000))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("ix_user_goals_user_id", "user_id"),
        Index("uq_user_goals_primary", "user_id", unique=True, postgresql_where=text("is_primary")),
    )
