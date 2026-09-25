"""Persistência de competências, sem desempenho individual."""

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Identity, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", name="fk_skills_category_id", ondelete="RESTRICT")
    )
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(2000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    __table_args__ = (
        UniqueConstraint("slug", name="uq_skills_slug"),
        CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="ck_skills_slug_format"),
        Index("ix_skills_category_id", "category_id"),
    )
