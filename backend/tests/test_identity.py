"""Identidade e permissões verificadas com persistência PostgreSQL real."""

from datetime import datetime, timezone
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI
import httpx
import jwt
import pytest
from sqlalchemy.orm import Session

from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.users.models import User, UserRole


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_identity_and_permissions(migrated_database, monkeypatch):
    engine, _ = migrated_database
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    monkeypatch.setenv("CODETRACK_DEBUG", "false")
    from app.main import app
    from app.database.connection import get_session
    from app.modules.users.dependencies import get_jwt_settings, require_admin

    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))

    def session_override():
        with Session(engine) as session:
            yield session

    # Rota apenas no app de teste: não publica funcionalidade administrativa.
    probe = FastAPI()

    @probe.get("/admin-check")
    def admin_check(user: Annotated[User, Depends(require_admin)]):
        return {"id": user.id}

    for application in (app, probe):
        application.dependency_overrides[get_session] = session_override
        application.dependency_overrides[get_jwt_settings] = lambda: settings
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            registered = await client.post("/api/v1/auth/register", json={
                "name": "Ana", "email": "ana@example.com", "password": "Minha senha longa!"})
            assert registered.status_code == 201
            user_id = registered.json()["id"]
            login = await client.post("/api/v1/auth/login", json={
                "email": "ana@example.com", "password": "Minha senha longa!"})
            assert login.status_code == 200
            token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            identity = await client.get("/api/v1/auth/me?user_id=999", headers=headers)
            assert identity.status_code == 200 and identity.json() == registered.json()
            assert identity.headers["Cache-Control"] == "no-store"
            assert "password_hash" not in identity.text and token not in identity.text
            second = await client.post("/api/v1/auth/register", json={
                "name": "Bruno", "email": "bruno@example.com", "password": "Outra senha longa!"})
            assert second.status_code == 201
            other_login = await client.post("/api/v1/auth/login", json={
                "email": "bruno@example.com", "password": "Outra senha longa!"})
            assert other_login.status_code == 200
            other_identity = await client.get("/api/v1/auth/me", headers={
                "Authorization": "Bearer " + other_login.json()["access_token"]})
            assert other_identity.json() == second.json()
            assert other_identity.json()["id"] != user_id
            now = int(datetime.now(timezone.utc).timestamp())
            expired = jwt.encode({"sub": str(user_id), "iat": now - 120, "exp": now - 60,
                                  "iss": "codetrack", "aud": "codetrack-api", "token_type": "access"},
                                 settings.jwt_secret_key.get_secret_value(), algorithm="HS256")
            wrong_settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
            for header in (None, "Basic abc", "Bearer", "Bearer invalid", f"Bearer {expired}",
                           f"Bearer {create_access_token(user_id, wrong_settings)}",
                           f"Bearer {create_access_token(2147483647, settings)}"):
                denied = await client.get("/api/v1/auth/me", headers={} if header is None else {"Authorization": header})
                assert denied.status_code == 401
                assert denied.json() == {"detail": "Autenticação inválida ou ausente."}
                assert denied.headers["WWW-Authenticate"] == "Bearer"
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=probe), base_url="http://test") as admin:
                assert (await admin.get("/admin-check")).status_code == 401
                assert (await admin.get("/admin-check", headers=headers)).status_code == 403
                with Session(engine) as session:
                    user = session.get(User, user_id)
                    user.role = UserRole.ADMIN
                    session.commit()
                # Mesmo token: a role vem do banco, não de claims antigos.
                assert (await admin.get("/admin-check", headers=headers)).status_code == 200
                assert (await client.get("/api/v1/auth/me", headers=headers)).json()["role"] == "ADMIN"
                with Session(engine) as session:
                    user = session.get(User, user_id)
                    user.role = UserRole.STUDENT
                    session.commit()
                assert (await admin.get("/admin-check", headers=headers)).status_code == 403
            with Session(engine) as session:
                session.delete(session.get(User, user_id))
                session.commit()
            assert (await client.get("/api/v1/auth/me", headers=headers)).status_code == 401
    finally:
        for application in (app, probe):
            application.dependency_overrides.pop(get_session, None)
            application.dependency_overrides.pop(get_jwt_settings, None)
