"""Valida migration e persistência em PostgreSQL descartável."""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository

def test_user_migration_round_trip(migrated_database) -> None:
    engine, alembic = migrated_database
    assert "users" in inspect(engine).get_table_names()

    with Session(engine) as session:
        user = User(name="Aluno", email="aluno@example.test", password_hash="hash-fixture")
        session.add(user)
        session.commit()
        assert user.id > 0
        assert user.role == UserRole.STUDENT
        assert user.onboarding_completed is False
        assert user.created_at.tzinfo is not None
        old_updated_at = user.updated_at
        user.name = "Aluno atualizado"
        session.commit()
        assert user.updated_at >= old_updated_at

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO users (name, email, password_hash) "
                "VALUES ('Duplicado', 'ALUNO@example.test', 'hash-fixture')"
            ))

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO users (name, email, password_hash, role) "
                "VALUES ('Inválido', 'outro@example.test', 'hash-fixture', 'OWNER')"
            ))

    with engine.begin() as connection:
        row = connection.execute(text(
            "INSERT INTO users (name, email, password_hash) "
            "VALUES ('SQL', 'sql@example.test', 'hash-fixture') "
            "RETURNING role, onboarding_completed, created_at, updated_at"
        )).one()
        assert row.role == "STUDENT" and row.onboarding_completed is False
        assert row.created_at is not None and row.updated_at is not None

    with Session(engine) as session:
        repository = UserRepository(session)
        user = repository.create(name="Repo", email="repo@example.com", password_hash="hash-fixture")
        user_id = user.id
        assert repository.get_by_id(user_id) is user
        assert repository.get_by_email(" REPO@EXAMPLE.COM ") is user
        assert repository.get_by_email("absent@example.com") is None
        assert repository.get_by_id(-1) is None
        session.rollback()
        assert repository.get_by_id(user_id) is None
        repository.create(name="Repo", email="repo@example.com", password_hash="hash-fixture")
        session.commit()
        with pytest.raises(IntegrityError):
            repository.create(name="Duplicate", email="REPO@example.com", password_hash="hash-fixture")
        session.rollback()
        assert repository.get_by_email("repo@example.com") is not None

    alembic("check")
    engine.dispose()
    alembic("downgrade", "base")
    assert "users" not in inspect(engine).get_table_names()
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
