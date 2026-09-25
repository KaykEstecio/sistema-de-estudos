"""Contratos de competências; não incluem desempenho do usuário."""

from pydantic import BaseModel, ConfigDict, Field, StrictBool

from app.modules.categories.schemas import CatalogId, CategoryCreate, CategoryListQuery, CategoryUpdate


class SkillCreate(CategoryCreate):
    category_id: CatalogId
    is_active: StrictBool = True


class SkillUpdate(CategoryUpdate):
    category_id: CatalogId | None = None
    is_active: StrictBool | None = None


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    slug: str
    description: str | None
    is_active: bool


class SkillListQuery(CategoryListQuery):
    category_id: int | None = Field(default=None, ge=1, le=2147483647)
    is_active: bool | None = None


class SkillPage(BaseModel):
    items: list[SkillRead]
    limit: int
    offset: int
    total: int
