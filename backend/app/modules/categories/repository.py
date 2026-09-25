"""Persistência de categorias; commit e autorização ficam no service."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.categories.models import Category
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def list_page(self, *, limit: int, offset: int) -> tuple[list[Category], int]:
        total = self.session.scalar(select(func.count()).select_from(Category)) or 0
        items = list(self.session.scalars(select(Category).order_by(Category.id).limit(limit).offset(offset)))
        return items, total

    def create(self, data: CategoryCreate) -> Category:
        category = Category(**data.model_dump())
        self.session.add(category)
        self.session.flush()
        return category

    def update(self, category: Category, data: CategoryUpdate) -> Category:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        self.session.flush()
        return category
