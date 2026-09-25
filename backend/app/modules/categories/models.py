"""Persistência de categorias."""

from sqlalchemy import CheckConstraint, Identity, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(2000))

    __table_args__ = (
        UniqueConstraint("slug", name="uq_categories_slug"),
        CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="ck_categories_slug_format"),
    )
