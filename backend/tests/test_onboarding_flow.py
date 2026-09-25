"""HTTP, disputa de conclusão e falha parcial do onboarding."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import secrets
import httpx
import pytest
from sqlalchemy.orm import Session
from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.categories.models import Category
from app.modules.users.models import User
from app.modules.onboarding.schemas import OnboardingCreate, OnboardingUpdate
from app.modules.onboarding.service import OnboardingService, OnboardingAlreadyCompleted


def seed(engine):
    with Session(engine) as session:
        user = User(name="User", email="onboarding@example.com", password_hash="unused")
        category = Category(name="Logic", slug="logic")
        session.add_all([user, category])
        session.commit()
        return user.id, category.id


def payload(category_id):
    return {"declared_experience": "BEGINNER", "interest_category_ids": [category_id],
            "primary_goal": {"goal_type": "Learn", "description": "Text"}}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_onboarding_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    uid, cid = seed(engine)
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
    headers = {"Authorization": "Bearer " + create_access_token(uid, settings)}
    url = "/api/v1/onboarding"
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for method in ("GET", "POST", "PATCH"):
                assert (await client.request(method, url)).status_code == 401
            before = await client.get(url, headers=headers)
            assert before.json() == {"onboarding_completed": False, "declared_experience": None,
                                     "interest_category_ids": [], "primary_goal": None}
            assert (await client.patch(url, headers=headers, json={"declared_experience": "BASIC"})).status_code == 409
            assert (await client.post(url, headers=headers, json=payload(2147483647))).status_code == 404
            assert (await client.get(url, headers=headers)).json() == before.json()
            created = await client.post(url, headers=headers, json=payload(cid))
            assert created.status_code == 201 and created.json()["onboarding_completed"] is True
            assert created.headers["Cache-Control"] == "no-store"
            assert (await client.get("/api/v1/auth/me", headers=headers)).json()["onboarding_completed"] is True
            assert (await client.post(url, headers=headers, json=payload(cid))).status_code == 409
            assert (await client.get(url + "?user_id=2", headers=headers)).status_code == 422
            for changes in ({}, {"user_id": 2}, {"interest_category_ids": []}, {"primary_goal": None}):
                assert (await client.patch(url, headers=headers, json=changes)).status_code == 422
            updated = await client.patch(url, headers=headers, json={"primary_goal": {"goal_type": "New"}})
            assert updated.status_code == 200
            assert updated.json()["primary_goal"] == {"goal_type": "New", "description": None}
            assert updated.json()["interest_category_ids"] == [cid]
            assert (await client.get(url, headers=headers)).json() == updated.json()
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)


def test_concurrent_completion_and_partial_failure(migrated_database):
    engine, _ = migrated_database
    uid, cid = seed(engine)
    barrier = Barrier(2)
    def complete():
        with Session(engine) as session:
            # Reproduz User previamente carregado pela autenticação.
            cached = session.get(User, uid)
            assert not cached.onboarding_completed
            barrier.wait(timeout=15)
            try:
                OnboardingService(session).create(uid, OnboardingCreate(**payload(cid)))
                return "created"
            except OnboardingAlreadyCompleted:
                return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: complete(), range(2)))
    assert sorted(results) == ["conflict", "created"]
    with Session(engine) as session:
        service = OnboardingService(session)
        before = service.get(uid)
        session.rollback()
        def fail_goal(*args):
            raise RuntimeError("simulated failure")
        service.repository.set_primary_goal = fail_goal
        with pytest.raises(RuntimeError):
            service.update(uid, OnboardingUpdate(interest_category_ids=[cid], primary_goal={"goal_type": "New"}))
        assert service.get(uid) == before
