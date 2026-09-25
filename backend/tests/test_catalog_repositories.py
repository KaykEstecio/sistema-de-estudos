"""Paginação, filtros, alterações parciais e transações reais."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate, CategoryRead
from app.modules.skills.repository import SkillRepository
from app.modules.skills.schemas import SkillCreate, SkillUpdate, SkillRead


def test_catalog_repositories(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        categories = CategoryRepository(session)
        skills = SkillRepository(session)
        assert categories.list_page(limit=20, offset=0) == ([], 0)
        first = categories.create(CategoryCreate(name="Languages", slug="languages", description="Text"))
        second = categories.create(CategoryCreate(name="Database", slug="database"))
        first_id, second_id = first.id, second.id
        active = skills.create(SkillCreate(name="Python", slug="python", category_id=first_id))
        inactive = skills.create(SkillCreate(name="Java", slug="java", category_id=first_id, is_active=False))
        other = skills.create(SkillCreate(name="SQL", slug="sql", category_id=second_id))
        active_id = active.id
        session.commit()
        assert categories.get_by_id(first_id) is first
        assert skills.get_by_id(active_id) is active
        assert categories.get_by_id(2147483647) is None and skills.get_by_id(2147483647) is None
        assert categories.list_page(limit=1, offset=1) == ([second], 2)
        assert skills.list_page(limit=1, offset=1) == ([inactive], 3)
        assert skills.list_page(limit=20, offset=0, category_id=first_id, is_active=True) == ([active], 1)
        assert skills.list_page(limit=20, offset=0, is_active=False) == ([inactive], 1)
        assert skills.list_page(limit=20, offset=99, is_active=True) == ([], 2)
        assert skills.list_page(limit=20, offset=0, category_id=2147483647) == ([], 0)
        assert set(CategoryRead.model_validate(first).model_dump()) == {"id", "name", "slug", "description"}
        assert set(SkillRead.model_validate(active).model_dump()) == {"id", "category_id", "name", "slug", "description", "is_active"}
        categories.update(first, CategoryUpdate(description=None))
        skills.update(active, SkillUpdate(category_id=second_id, is_active=False))
        assert first.description is None and active.category_id == second_id and not active.is_active
        session.rollback()
        assert first.description == "Text" and active.category_id == first_id and active.is_active
        temporary = categories.create(CategoryCreate(name="Temporary", slug="temporary"))
        temporary_id = temporary.id
        session.rollback()
        assert categories.get_by_id(temporary_id) is None
        with pytest.raises(IntegrityError):
            skills.update(other, SkillUpdate(slug="python"))
        session.rollback()
        assert other.slug == "sql"
        categories.update(first, CategoryUpdate(name="Renamed"))
        skills.update(active, SkillUpdate(description="New description"))
        session.commit()
    with Session(engine) as session:
        assert CategoryRepository(session).get_by_id(first_id).name == "Renamed"
        assert SkillRepository(session).get_by_id(active_id).description == "New description"
