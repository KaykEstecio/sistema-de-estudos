"""Validação de criação, PATCH e paginação do catálogo."""

import pytest
from pydantic import ValidationError

from app.modules.categories.schemas import CategoryCreate, CategoryUpdate, CategoryListQuery
from app.modules.skills.schemas import SkillCreate, SkillUpdate, SkillListQuery


def test_normalization_and_patch_semantics():
    data = SkillCreate(name=" Python ", slug=" PYTHON-3 ", category_id=1, description="  ")
    assert data.name == "Python" and data.slug == "python-3"
    assert data.description is None and data.is_active is True
    assert CategoryUpdate(description=None).model_dump(exclude_unset=True) == {"description": None}
    assert SkillUpdate(is_active=False).model_dump(exclude_unset=True) == {"is_active": False}
    assert CategoryUpdate(name="New").model_dump(exclude_unset=True) == {"name": "New"}
    assert len(CategoryCreate(name="x" * 120, slug="x" * 120, description="x" * 2000).description) == 2000


@pytest.mark.parametrize("changes", [
    {"name": " "}, {"name": 12}, {"name": True}, {"name": "x" * 121},
    {"slug": ""}, {"slug": "a--b"}, {"slug": "ação"}, {"slug": "x" * 121},
    {"description": "x" * 2001}, {"description": 12}, {"id": 1},
    {"category_id": None}, {"category_id": True}, {"category_id": "1"},
    {"category_id": 0}, {"category_id": 2147483648}, {"is_active": "true"}, {"is_active": 1},
])
def test_invalid_create(changes):
    with pytest.raises(ValidationError):
        SkillCreate.model_validate({"name": "Python", "slug": "python", "category_id": 1, **changes})


@pytest.mark.parametrize("changes", [{}, {"name": None}, {"slug": None}, {"category_id": None},
                                     {"is_active": None}, {"id": 1}, {"unexpected": "x"}])
def test_invalid_patch(changes):
    with pytest.raises(ValidationError):
        SkillUpdate.model_validate(changes)


@pytest.mark.parametrize("query", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"search": "x"},
                                  {"category_id": 0}, {"is_active": "invalid"}])
def test_invalid_query(query):
    with pytest.raises(ValidationError):
        SkillListQuery.model_validate(query)


def test_query_defaults_and_url_strings():
    assert CategoryListQuery().model_dump() == {"limit": 20, "offset": 0}
    result = SkillListQuery(limit="100", offset="2", category_id="1", is_active="false")
    assert (result.limit, result.offset, result.category_id, result.is_active) == (100, 2, 1, False)
