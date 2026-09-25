"""Publicação, autorização, rollback e concorrência em banco isolado."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
import secrets

import httpx
import pytest
from sqlalchemy.orm import Session

from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.users.models import User, UserRole
from app.modules.challenges.schemas import ChallengeCreate, ChallengeUpdate
from app.modules.challenges.service import ChallengeService, ChallengeConflict


def seed(engine):
    with Session(engine) as session:
        category = Category(name="Test", slug="test")
        session.add(category)
        session.flush()
        skill = Skill(name="Test", slug="test", category_id=category.id)
        session.add(skill)
        session.commit()
        return skill.id


def payload(sid):
    return dict(title="Fixture", description="Synthetic content", challenge_type="CODE", difficulty="EASY",
                difficulty_score=100, estimated_minutes=10, skills=[dict(skill_id=sid, weight=100)])


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_challenge_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    sid = seed(engine)
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
        users = [User(name="Test", email=f"{role.value}@example.com", password_hash="unused", role=role)
                 for role in (UserRole.ADMIN, UserRole.STUDENT)]
        session.add_all(users)
        session.commit()
        admin, student = [{"Authorization": "Bearer " + create_access_token(user.id, settings)} for user in users]
    base = "/api/v1/challenges"
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get(base)).status_code == 401
            assert (await client.post(base, json=payload(sid))).status_code == 401
            assert (await client.post(base, json=payload(sid), headers=student)).status_code == 403
            created = await client.post(base, json=payload(sid), headers=admin)
            assert created.status_code == 201
            cid = created.json()["id"]
            url = f"{base}/{cid}"
            assert created.json()["is_active"] is False
            assert (await client.get(url, headers=student)).status_code == 404
            assert (await client.patch(url, json={"is_active": True}, headers=student)).status_code == 403
            for weights in ([99], [100, 1]):
                body = {"skills": [dict(skill_id=sid+i, weight=w) for i, w in enumerate(weights)]}
                assert (await client.patch(url, json=body, headers=admin)).status_code == 409
            assert (await client.patch(url, json={"skills": [dict(skill_id=2147483647, weight=100)]}, headers=admin)).status_code == 404
            assert (await client.patch(url, json={"is_active": True}, headers=admin)).status_code == 200
            page = await client.get(base+f"?type=CODE&skill={sid}&difficulty=EASY", headers=student)
            assert page.status_code == 200 and page.json()["total"] == 1
            assert page.headers["cache-control"] == "no-store"
            assert (await client.get(base+"?type=SQL", headers=student)).json()["total"] == 0
            assert (await client.get(base+"?is_active=false", headers=student)).status_code == 403
            with Session(engine) as session:
                session.get(Skill, sid).is_active = False
                session.commit()
            assert (await client.get(url, headers=student)).status_code == 404
            assert (await client.get(base, headers=student)).json()["total"] == 0
            assert (await client.patch(url, json={"title": "Invalid update"}, headers=admin)).status_code == 409
            assert (await client.get(url, headers=admin)).json()["title"] == "Fixture"
            assert (await client.patch(url, json={"is_active": False}, headers=admin)).status_code == 200
            assert (await client.patch(url, json={"is_active": True}, headers=admin)).status_code == 409
            with Session(engine) as session:
                session.get(Skill, sid).is_active = True
                session.commit()
            assert (await client.patch(url, json={"is_active": True, "starter_code": None}, headers=admin)).status_code == 200
            assert (await client.get(url, headers=student)).status_code == 200
            for path in (base+"?completed=true", url+"?extra=1", base+"/0"):
                assert (await client.get(path, headers=admin)).status_code == 422
            assert (await client.post(base+"?extra=1", json=payload(sid), headers=admin)).status_code == 422
            assert (await client.patch(url, json={}, headers=admin)).status_code == 422
            assert (await client.patch(base+"/2147483647", json={"title": "X"}, headers=admin)).status_code == 404
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)


def test_challenge_rollback_and_concurrent_patch(migrated_database):
    engine, _ = migrated_database
    sid = seed(engine)
    with Session(engine) as session:
        service = ChallengeService(session)
        cid = service.create(ChallengeCreate(**payload(sid))).id
        original = service.repository.update
        def fail(item, data):
            original(item, data)
            raise RuntimeError("simulated after flush")
        service.repository.update = fail
        with pytest.raises(RuntimeError):
            service.update(cid, ChallengeUpdate(title="Rollback", skills=[dict(skill_id=sid, weight=100)]))
        assert service.get(cid, UserRole.ADMIN).title == "Fixture"
        assert service.get(cid, UserRole.ADMIN).skills[0].weight == 100
    barrier = Barrier(2)
    def update(body):
        with Session(engine) as session:
            service = ChallengeService(session)
            # Ambos leem o valor anterior antes de disputar o lock.
            service.get(cid, UserRole.ADMIN)
            barrier.wait(timeout=15)
            service.update(cid, ChallengeUpdate(**body))
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(update, ({"title": "Updated"}, {"description": "Updated description"})))
    with Session(engine) as session:
        item = ChallengeService(session).get(cid, UserRole.ADMIN)
        assert item.title == "Updated" and item.description == "Updated description"


def test_challenge_publication_waits_for_skill_update(migrated_database):
    engine, _ = migrated_database
    sid = seed(engine)
    with Session(engine) as session:
        cid = ChallengeService(session).create(ChallengeCreate(**payload(sid))).id
    entered = Event()
    def publish():
        with Session(engine) as session:
            service = ChallengeService(session)
            original = service.repository.get_skills_locked
            def notify(ids):
                entered.set()
                return original(ids)
            service.repository.get_skills_locked = notify
            with pytest.raises(ChallengeConflict):
                service.update(cid, ChallengeUpdate(is_active=True))
    with ThreadPoolExecutor(max_workers=1) as pool:
        with Session(engine) as session:
            session.get(Skill, sid).is_active = False
            session.flush()
            future = pool.submit(publish)
            assert entered.wait(timeout=15)
            session.commit()
        future.result(timeout=15)
    with Session(engine) as session:
        assert not ChallengeService(session).get(cid, UserRole.ADMIN).is_active
