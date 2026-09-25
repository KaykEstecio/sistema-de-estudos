"""Contratos do catálogo e validação dos campos compartilhados."""

from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints, model_validator


def normalize_slug(value: object) -> object:
    return value.strip().lower() if isinstance(value, str) else value


def normalize_description(value: object) -> object:
    return (value.strip() or None) if isinstance(value, str) else value


Name = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=120)]
Slug = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=120,
                                      pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$"), BeforeValidator(normalize_slug)]
Description = Annotated[str | None, Field(max_length=2000), BeforeValidator(normalize_description)]
CatalogId = Annotated[int, Field(strict=True, ge=1, le=2147483647)]


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    name: Name
    slug: Slug
    description: Description = None


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    name: Name | None = None
    slug: Slug | None = None
    description: Description = None

    @model_validator(mode="after")
    def validate_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo editável.")
        for field in self.model_fields_set - {"description"}:
            if getattr(self, field) is None:
                raise ValueError("Somente description aceita null.")
        return self


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: str | None


class CategoryListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class CategoryPage(BaseModel):
    items: list[CategoryRead]
    limit: int
    offset: int
    total: int
