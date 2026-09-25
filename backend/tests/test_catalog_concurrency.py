"""Unicidade concorrente e recuperação da transação nos services."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy.orm import Session
from app.modules.categories.schemas import CategoryCreate
from app.modules.categories.service import CategoryService, CategorySlugConflict
from app.modules.skills.schemas import SkillCreate
from app.modules.skills.service import SkillService, SkillSlugConflict


@pytest.mark.parametrize("resource", ["category", "skill"])
def test_concurrent_catalog_create(migrated_database, resource):
    engine, _ = migrated_database
    with Session(engine) as session:
        category_id = CategoryService(session).create(CategoryCreate(name="Parent", slug="parent")).id
    barrier = Barrier(2)
    def create():
        with Session(engine) as session:
            service = CategoryService(session) if resource == "category" else SkillService(session)
            original = service.repository.create
            def synchronized(data):
                barrier.wait(timeout=15)
                return original(data)
            service.repository.create = synchronized
            data = CategoryCreate(name="Race", slug="race") if resource == "category" else SkillCreate(name="Race", slug="race", category_id=category_id)
            try:
                service.create(data)
                return "created"
            except (CategorySlugConflict, SkillSlugConflict):
                assert session.is_active
                assert CategoryService(session).get(category_id).id == category_id
                return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: create(), range(2)))
    assert sorted(results) == ["conflict", "created"]
