"""Consultas do catálogo de categorias."""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import CategoryListQuery, CategoryPage, CategoryRead


class CategoryNotFound(Exception):
    pass


class CategorySlugConflict(Exception):
    pass


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.repository = CategoryRepository(session)
        self.session = session

    def create(self, data: CategoryCreate) -> CategoryRead:
        return self._write(data)

    def update(self, category_id: int, data: CategoryUpdate) -> CategoryRead:
        return self._write(data, category_id)

    def _write(self, data: CategoryCreate | CategoryUpdate, category_id: int | None = None) -> CategoryRead:
        try:
            if isinstance(data, CategoryCreate):
                category = self.repository.create(data)
            else:
                assert category_id is not None
                category = self.repository.get_by_id(category_id)
                if category is None:
                    raise CategoryNotFound()
                category = self.repository.update(category, data)
            result = CategoryRead.model_validate(category)
            self.session.commit()
            return result
        except IntegrityError as exc:
            self.session.rollback()
            if (getattr(exc.orig, "sqlstate", None) == "23505"
                    and getattr(getattr(exc.orig, "diag", None), "constraint_name", None) == "uq_categories_slug"):
                raise CategorySlugConflict() from None
            raise
        except Exception:
            self.session.rollback()
            raise

    def get(self, category_id: int) -> CategoryRead:
        category = self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFound()
        return CategoryRead.model_validate(category)

    def list_page(self, query: CategoryListQuery) -> CategoryPage:
        items, total = self.repository.list_page(limit=query.limit, offset=query.offset)
        return CategoryPage(items=[CategoryRead.model_validate(item) for item in items],
                            total=total, limit=query.limit, offset=query.offset)
