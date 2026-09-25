"""Consulta HTTP com identidade real e catálogo em PostgreSQL isolado."""

import secrets
import httpx
import pytest
from sqlalchemy.orm import Session
from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.users.models import User, UserRole


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_catalog_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    monkeypatch.setenv("CODETRACK_DEBUG", "false")
    from app.main import app
    from app.database.connection import get_session
    from app.modules.users.dependencies import get_jwt_settings

    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
    def session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    with Session(engine) as session:
        user = User(name="Student", email="student@example.com", password_hash="unused")
        session.add(user)
        session.commit()
        user_id = user.id
    headers = {"Authorization": "Bearer " + create_access_token(user_id, settings)}
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for url in ("/categories", "/skills", "/categories/1", "/skills/1", "/skills?limit=0"):
                response = await client.get("/api/v1" + url)
                assert response.status_code == 401
            for path in ("categories", "skills"):
                assert (await client.post(f"/api/v1/{path}", json={})).status_code == 401
                assert (await client.post(f"/api/v1/{path}", json={}, headers=headers)).status_code == 403
                assert (await client.patch(f"/api/v1/{path}/1", json={}, headers=headers)).status_code == 403
                response = await client.get(f"/api/v1/{path}", headers=headers)
                assert response.json() == {"items": [], "limit": 20, "offset": 0, "total": 0}
            with Session(engine) as session:
                category = Category(name="Languages", slug="languages")
                empty = Category(name="Empty", slug="empty")
                session.add_all([category, empty])
                session.flush()
                category_id, empty_id = category.id, empty.id
                active = Skill(name="Python", slug="python", category_id=category_id)
                inactive = Skill(name="Java", slug="java", category_id=category_id, is_active=False)
                session.add_all([active, inactive])
                session.commit()
                active_id, inactive_id = active.id, inactive.id
            listed = (await client.get("/api/v1/skills", headers=headers)).json()
            assert listed["total"] == 1 and [item["id"] for item in listed["items"]] == [active_id]
            assert set(listed["items"][0]) == {"id", "name", "slug", "description", "category_id", "is_active"}
            assert (await client.get(f"/api/v1/skills/{active_id}", headers=headers)).json() == listed["items"][0]
            assert (await client.get(f"/api/v1/categories/{empty_id}", headers=headers)).status_code == 200
            page = (await client.get("/api/v1/categories?limit=1&offset=1", headers=headers)).json()
            assert page["total"] == 2 and page["items"][0]["id"] == empty_id
            for url in (f"/skills/{inactive_id}", "/skills/2147483647", "/categories/2147483647"):
                assert (await client.get("/api/v1" + url, headers=headers)).status_code == 404
            assert (await client.get("/api/v1/skills?is_active=false", headers=headers)).status_code == 403
            for query in ("category_id=2147483647", "offset=99"):
                assert (await client.get("/api/v1/skills?" + query, headers=headers)).json()["items"] == []
            for url in ("/skills?limit=101", "/skills?offset=-1", "/skills?category_id=0", "/skills?is_active=bad",
                        "/skills?unknown=1", "/categories?unknown=1", "/skills/0", "/categories/nope"):
                assert (await client.get("/api/v1" + url, headers=headers)).status_code == 422
            with Session(engine) as session:
                session.get(User, user_id).role = UserRole.ADMIN
                session.commit()
            page = (await client.get("/api/v1/skills?limit=1&offset=1", headers=headers)).json()
            assert page["total"] == 2 and page["items"][0]["id"] == inactive_id
            filtered = (await client.get(f"/api/v1/skills?category_id={category_id}&is_active=false", headers=headers)).json()
            assert filtered["total"] == 1 and filtered["items"][0]["id"] == inactive_id
            assert (await client.get(f"/api/v1/skills/{inactive_id}", headers=headers)).status_code == 200
            created = await client.post("/api/v1/categories", json={"name": "Web", "slug": " WEB "}, headers=headers)
            assert created.status_code == 201 and created.json()["slug"] == "web"
            web_id = created.json()["id"]
            assert (await client.post("/api/v1/categories", json={"name": "Other", "slug": "web"}, headers=headers)).status_code == 409
            created_skill = await client.post("/api/v1/skills", json={"name": "HTTP", "slug": "http", "category_id": web_id}, headers=headers)
            assert created_skill.status_code == 201 and created_skill.json()["is_active"] is True
            http_id = created_skill.json()["id"]
            duplicate = await client.patch(f"/api/v1/skills/{http_id}", json={"name": "Should rollback", "slug": "python"}, headers=headers)
            assert duplicate.status_code == 409
            assert (await client.get(f"/api/v1/skills/{http_id}", headers=headers)).json()["name"] == "HTTP"
            assert (await client.patch(f"/api/v1/skills/{http_id}", json={"category_id": 2147483647}, headers=headers)).status_code == 404
            assert (await client.patch("/api/v1/skills/2147483647", json={"category_id": 2147483647}, headers=headers)).json() == {"detail": "Skill não encontrada."}
            updated = await client.patch(f"/api/v1/skills/{http_id}", json={"category_id": category_id, "description": "Text", "is_active": False}, headers=headers)
            assert updated.status_code == 200 and updated.json()["category_id"] == category_id
            assert (await client.patch(f"/api/v1/skills/{http_id}", json={"description": None}, headers=headers)).json()["description"] is None
            assert (await client.patch(f"/api/v1/categories/{web_id}", json={"name": "Renamed"}, headers=headers)).json()["name"] == "Renamed"
            assert (await client.patch(f"/api/v1/categories/{web_id}", json={"slug": "languages"}, headers=headers)).status_code == 409
            for path in (f"categories/{web_id}", f"skills/{http_id}"):
                assert (await client.patch("/api/v1/" + path, json={}, headers=headers)).status_code == 422
            with Session(engine) as session:
                session.get(User, user_id).role = UserRole.STUDENT
                session.commit()
            assert (await client.patch(f"/api/v1/skills/{http_id}", json={"is_active": True}, headers=headers)).status_code == 403
            assert (await client.get(f"/api/v1/skills/{http_id}", headers=headers)).status_code == 404
            with Session(engine) as session:
                session.get(User, user_id).role = UserRole.ADMIN
                session.commit()
            reactivated = await client.patch(f"/api/v1/skills/{http_id}", json={"is_active": True}, headers=headers)
            assert reactivated.status_code == 200 and reactivated.json()["is_active"] is True
            with Session(engine) as session:
                session.get(User, user_id).role = UserRole.STUDENT
                session.commit()
            assert (await client.get(f"/api/v1/skills/{http_id}", headers=headers)).status_code == 200
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)
