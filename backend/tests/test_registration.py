"""Cadastro HTTP e concorrência usam PostgreSQL isolado."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import Mock

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.modules.users.service import EmailAlreadyRegistered, UserService


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_registration_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    monkeypatch.setenv("CODETRACK_DEBUG", "false")
    from app.database.connection import get_session
    from app.main import app

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    password = "  Uma senha longa  "
    payload = {"name": " Ana ", "email": " ANA@EXAMPLE.COM ", "password": password}
    try:
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/api/v1/auth/register", json=payload)
                assert response.status_code == 201
                data = response.json()
                assert set(data) == {"id", "name", "email", "role", "onboarding_completed", "created_at", "updated_at"}
                assert data["name"] == "Ana" and data["email"] == "ana@example.com"
                assert data["role"] == "STUDENT" and data["onboarding_completed"] is False
                with Session(engine) as session:
                    user = session.get(User, data["id"])
                    assert user.password_hash != password
                    assert verify_password(password, user.password_hash)
                    assert user.password_hash not in response.text
                duplicate = await client.post("/api/v1/auth/register", json={**payload, "email": "ana@example.com"})
                assert duplicate.status_code == 409
                for changes in ({"role": "ADMIN"}, {"password_hash": "private"}, {"onboarding_completed": True},
                                {"password": "short-secret"}, {"password": "x" * 129}, {"email": "invalid"}, {"name": " "}):
                    invalid = await client.post("/api/v1/auth/register", json={**payload, **changes})
                    assert invalid.status_code == 422
                    assert password not in invalid.text and "short-secret" not in invalid.text
                    assert all("input" not in error and "ctx" not in error for error in invalid.json()["detail"])
                for body in ([payload], {"password": {"secret": password}}):
                    invalid = await client.post("/api/v1/auth/register", json=body)
                    assert invalid.status_code == 422 and password not in invalid.text
                invalid_key = await client.post("/api/v1/auth/register", json={**payload, password: "extra"})
                assert invalid_key.status_code == 422 and password not in invalid_key.text
                malformed = await client.post("/api/v1/auth/register", content='{"password":"private-secret",', headers={"Content-Type": "application/json"})
                assert malformed.status_code == 422 and "private-secret" not in malformed.text
                with Session(engine) as session:
                    assert session.scalar(select(func.count()).select_from(User)) == 1
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_concurrent_registration_has_one_winner(migrated_database):
    engine, _ = migrated_database
    barrier = Barrier(2)

    def register(email):
        with Session(engine) as session:
            service = UserService(session)
            create = service.repository.create

            def synchronized_create(**kwargs):
                barrier.wait(timeout=15)
                return create(**kwargs)

            service.repository.create = synchronized_create
            try:
                service.register(UserCreate(name="Ana", email=email, password="Uma senha longa!"))
                return "created"
            except EmailAlreadyRegistered:
                assert session.is_active
                assert service.repository.get_by_email(email) is not None
                return "duplicate"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(register, ["race@example.com", "RACE@example.com"]))
    assert sorted(results) == ["created", "duplicate"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(User)) == 1


def test_unrelated_integrity_error_is_not_duplicate():
    session = Mock(spec=Session)
    service = UserService(session)
    error = IntegrityError("statement", {}, Exception("unrelated constraint"))
    service.repository.create = Mock(side_effect=error)
    with pytest.raises(IntegrityError):
        service.register(UserCreate(name="Ana", email="ana@example.com", password="Uma senha longa!"))
    session.rollback.assert_called_once()
    session.commit.assert_not_called()
