"""Constraints do catálogo e reversão isolada preservando usuários."""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.categories.models import Category
from app.modules.skills.models import Skill


def test_catalog_migration(migrated_database):
    engine, alembic = migrated_database
    with Session(engine) as session:
        category = Category(name="Languages", slug="languages")
        session.add(category)
        session.flush()
        category_id = category.id
        skill = Skill(category_id=category_id, name="Python", slug="python")
        session.add(skill)
        session.commit()
        assert skill.is_active is True
        assert category.description is None and skill.description is None
        skill.is_active = False
        session.commit()
        assert skill.is_active is False

    def rejected(statement, parameters, constraint):
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(statement), parameters)
        assert error.value.orig.diag.constraint_name == constraint

    rejected("INSERT INTO categories (name,slug) VALUES ('Other','languages')", {}, "uq_categories_slug")
    for slug in ("Python", "", "two words", "-python", "python-", "py--thon", "ação", "python\n"):
        rejected("INSERT INTO categories (name,slug) VALUES ('Invalid',:slug)", {"slug": slug}, "ck_categories_slug_format")
        rejected("INSERT INTO skills (category_id,name,slug) VALUES (:id,'Invalid',:slug)",
                 {"id": category_id, "slug": slug}, "ck_skills_slug_format")
    rejected("INSERT INTO skills (category_id,name,slug) VALUES (:id,'Other','python')",
             {"id": category_id}, "uq_skills_slug")
    rejected("INSERT INTO skills (category_id,name,slug) VALUES (2147483647,'Orphan','orphan')", {}, "fk_skills_category_id")
    rejected("DELETE FROM categories WHERE id=:id", {"id": category_id}, "fk_skills_category_id")
    for column in ("category_id", "is_active"):
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(f"INSERT INTO skills (category_id,name,slug,is_active) VALUES (:id,'Null','null-field',:active)"),
                                   {"id": None if column == "category_id" else category_id,
                                    "active": None if column == "is_active" else True})
        assert error.value.orig.sqlstate == "23502"
    with engine.begin() as connection:
        assert connection.execute(text("INSERT INTO skills (category_id,name,slug) VALUES (:id,'SQL','sql') RETURNING is_active"), {"id": category_id}).scalar_one() is True
        user_id = connection.execute(text("INSERT INTO users (name,email,password_hash) VALUES ('Preserved','preserved@example.com','test-hash') RETURNING id")).scalar_one()
    assert any(index["name"] == "ix_skills_category_id" for index in inspect(engine).get_indexes("skills"))
    alembic("check")
    engine.dispose()
    alembic("downgrade", "0001_create_users")
    assert "categories" not in inspect(engine).get_table_names()
    assert "skills" not in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.execute(text("SELECT id FROM users WHERE id=:id"), {"id": user_id}).scalar_one() == user_id
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
