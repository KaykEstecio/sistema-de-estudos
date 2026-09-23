"""Fluxo cadastro/login em PostgreSQL isolado, com chave JWT efêmera."""

import secrets
from unittest.mock import Mock, patch

import httpx
import pytest
from sqlalchemy.orm import Session

from app.core.config import JWTSettings
from app.core.tokens import decode_access_token
from app.modules.users.auth_service import AuthService, InvalidCredentials
from app.modules.users.schemas import LoginRequest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_login_http(migrated_database, monkeypatch, caplog):
    engine, _ = migrated_database
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    monkeypatch.setenv("CODETRACK_DEBUG", "false")
    from app.database.connection import get_session
    from app.main import app
    from app.modules.users.router import get_jwt_settings

    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32), jwt_access_token_minutes=5)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    password = "  Minha senha longa!  "
    try:
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                registered = await client.post("/api/v1/auth/register", json={
                    "name": "Ana", "email": "ana@example.com", "password": password})
                assert registered.status_code == 201
                response = await client.post("/api/v1/auth/login", json={
                    "email": " ANA@EXAMPLE.COM ", "password": password})
                assert response.status_code == 200
                result = response.json()
                assert set(result) == {"access_token", "token_type", "expires_in"}
                assert result["token_type"] == "bearer" and result["expires_in"] == 300
                assert decode_access_token(result["access_token"], settings) == registered.json()["id"]
                assert response.headers["Cache-Control"] == "no-store"
                for email, attempted in [("absent@example.com", password), ("ana@example.com", "wrong"),
                                          ("ana@example.com", password.strip()), ("ana@example.com", password.upper())]:
                    denied = await client.post("/api/v1/auth/login", json={"email": email, "password": attempted})
                    assert denied.status_code == 401
                    assert denied.json() == {"detail": "E-mail ou senha inválidos."}
                    assert denied.headers["WWW-Authenticate"] == "Bearer"
                for changes in ({"email": "invalid"}, {"password": ""}, {"password": "x" * 129}, {"role": "ADMIN"}):
                    invalid = await client.post("/api/v1/auth/login", json={
                        "email": "ana@example.com", "password": password, **changes})
                    assert invalid.status_code == 422 and password not in invalid.text
                assert password not in response.text
                assert password not in caplog.text and result["access_token"] not in caplog.text
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)


def test_missing_user_still_verifies_password():
    session = Mock(spec=Session)
    session.scalar.return_value = None
    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
    with patch("app.modules.users.auth_service.verify_password", return_value=True) as verify:
        with pytest.raises(InvalidCredentials):
            AuthService(session, settings).login(LoginRequest(email="absent@example.com", password="attempt"))
    verify.assert_called_once()
    session.commit.assert_not_called()
