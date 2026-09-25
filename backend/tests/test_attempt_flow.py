"""Retomada, isolamento e concorrência de tentativas em banco real."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import secrets

import httpx
import pytest
from sqlalchemy.orm import Session

from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.users.models import User, UserRole
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.challenges.models import Challenge, ChallengeSkill
from app.modules.attempts.schemas import AttemptDraft
from app.modules.attempts.service import AttemptService, AttemptConflict


def seed(engine):
    with Session(engine) as session:
        users = [User(name="Test", email=f"flow{i}@example.com", password_hash="unused", role=role)
                 for i, role in enumerate((UserRole.STUDENT, UserRole.ADMIN))]
        category = Category(name="Test", slug="test")
        challenge = Challenge(title="Original", description="Fixture", challenge_type="CODE", difficulty="EASY",
                              difficulty_score=100, estimated_minutes=10, is_active=True)
        session.add_all([*users, category, challenge])
        session.flush()
        skill = Skill(name="Test", slug="test", category_id=category.id)
        session.add(skill)
        session.flush()
        session.add(ChallengeSkill(challenge_id=challenge.id, skill_id=skill.id, weight=100))
        session.commit()
        return users[0].id, users[1].id, challenge.id, skill.id


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_attempt_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    uid, other, cid, sid = seed(engine)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    from app.main import app
    from app.database.connection import get_session
    from app.modules.users.dependencies import get_jwt_settings
    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
    def sessions():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = sessions
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    owner, admin = [{"Authorization": "Bearer " + create_access_token(i, settings)} for i in (uid, other)]
    start = f"/api/v1/challenges/{cid}/attempts"
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.post(start)).status_code == 401
            assert (await client.post(start, json={}, headers=owner)).status_code == 422
            assert (await client.post(start+"?extra=1", headers=owner)).status_code == 422
            first = await client.post(start, headers=owner)
            assert first.status_code == 201 and first.json()["attempt_number"] == 1
            assert first.headers["cache-control"] == "no-store"
            url = f"/api/v1/attempts/{first.json()['id']}"
            resumed = await client.post(start, headers=owner)
            assert resumed.status_code == 200 and resumed.json() == first.json()
            assert (await client.get(url, headers=admin)).status_code == 404
            assert (await client.patch(url, json={"draft_answer": "stolen"}, headers=admin)).status_code == 404
            saved = await client.patch(url, json={"draft_answer": "  answer\n"}, headers=owner)
            assert saved.status_code == 200 and saved.json()["draft_answer"] == "  answer\n"
            assert (await client.patch(url, json={"draft_answer": "  answer\n"}, headers=owner)).json() == saved.json()
            assert (await client.get(url, headers=owner)).json() == saved.json()
            for body in ({}, {"draft_answer": None}, {"draft_answer": "x", "user_id": other}):
                assert (await client.patch(url, json=body, headers=owner)).status_code == 422
            with Session(engine) as session:
                session.get(Challenge, cid).title = "Changed"
                session.get(Challenge, cid).is_active = False
                session.get(Skill, sid).is_active = False
                session.commit()
            assert (await client.post(start, headers=owner)).json() == saved.json()
            assert (await client.post(start, headers=admin)).status_code == 404
            cleared = await client.patch(url, json={"draft_answer": ""}, headers=owner)
            assert cleared.json()["draft_answer"] == "" and cleared.json()["challenge_snapshot"]["title"] == "Original"
            assert (await client.post(url+"/submit")).status_code == 401
            assert (await client.post(url+"/submit", headers=admin)).status_code == 404
            assert (await client.post(url+"/submit", headers=owner)).status_code == 409
            await client.patch(url, json={"draft_answer": " \n\t"}, headers=owner)
            assert (await client.post(url+"/submit", headers=owner)).status_code == 409
            await client.patch(url, json={"draft_answer": "  final\n"}, headers=owner)
            assert (await client.post(url+"/submit", json={}, headers=owner)).status_code == 422
            assert (await client.post(url+"/submit?extra=1", headers=owner)).status_code == 422
            submitted = await client.post(url+"/submit", headers=owner)
            assert submitted.status_code == 200 and submitted.json()["draft_answer"] == "  final\n"
            assert submitted.json()["submitted_at"] == submitted.json()["last_activity_at"]
            assert (await client.post(url+"/submit", headers=owner)).json() == submitted.json()
            assert (await client.patch(url, json={"draft_answer": "x"}, headers=owner)).status_code == 409
            assert (await client.get(url, headers=owner)).json()["status"] == "SUBMITTED"
            assert (await client.post(start, headers=owner)).status_code == 404
            with Session(engine) as session:
                session.get(Challenge, cid).is_active = True
                session.get(Skill, sid).is_active = True
                session.commit()
            second = await client.post(start, headers=owner)
            assert second.status_code == 201 and second.json()["attempt_number"] == 2
            assert second.json()["challenge_snapshot"]["title"] == "Changed"
            assert (await client.get(url, headers=owner)).json() == submitted.json()
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)


def test_attempt_concurrent_start_and_rollback(migrated_database):
    engine, _ = migrated_database
    uid, _, cid, _ = seed(engine)
    barrier = Barrier(2)
    def start():
        with Session(engine) as session:
            barrier.wait(timeout=15)
            return AttemptService(session).start(uid, cid)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: start(), range(2)))
    assert sorted(created for _, created in results) == [False, True]
    assert results[0][0].id == results[1][0].id
    aid = results[0][0].id
    with Session(engine) as session:
        service = AttemptService(session)
        original = service.repository.save_draft
        def fail(*args):
            original(*args)
            raise RuntimeError("simulated after flush")
        service.repository.save_draft = fail
        with pytest.raises(RuntimeError):
            service.save_draft(uid, aid, AttemptDraft(draft_answer="lost"))
        assert service.get(uid, aid).draft_answer == ""


def test_attempt_submit_rollback_and_concurrency(migrated_database):
    engine, _ = migrated_database
    uid, _, cid, _ = seed(engine)
    with Session(engine) as session:
        service = AttemptService(session)
        attempt, _ = service.start(uid, cid)
        aid = attempt.id
        before = service.save_draft(uid, aid, AttemptDraft(draft_answer="original"))
        original = service.repository.submit
        def fail(*args):
            original(*args)
            raise RuntimeError("simulated after flush")
        service.repository.submit = fail
        with pytest.raises(RuntimeError):
            service.submit(uid, aid)
        assert service.get(uid, aid) == before
    barrier = Barrier(2)
    def submit():
        with Session(engine) as session:
            barrier.wait(timeout=15)
            return AttemptService(session).submit(uid, aid)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: submit(), range(2)))
    assert results[0] == results[1] and results[0].status == "SUBMITTED"


@pytest.mark.parametrize("first_action", ["save", "submit"])
def test_attempt_save_submit_order(migrated_database, first_action):
    from threading import Event
    engine, _ = migrated_database
    uid, _, cid, _ = seed(engine)
    with Session(engine) as session:
        service = AttemptService(session)
        attempt, _ = service.start(uid, cid)
        aid = attempt.id
        service.save_draft(uid, aid, AttemptDraft(draft_answer="original"))
    entered = Event()
    def second_action():
        with Session(engine) as session:
            service = AttemptService(session)
            original = service.repository.get_owned
            def notify(*args, **kwargs):
                entered.set()
                return original(*args, **kwargs)
            service.repository.get_owned = notify
            if first_action == "save":
                return service.submit(uid, aid)
            with pytest.raises(AttemptConflict):
                service.save_draft(uid, aid, AttemptDraft(draft_answer="late"))
            return service.get(uid, aid)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with Session(engine) as session:
            service = AttemptService(session)
            service.repository.get_owned(aid, uid, lock=True)
            future = pool.submit(second_action)
            assert entered.wait(timeout=15)
            if first_action == "save":
                service.save_draft(uid, aid, AttemptDraft(draft_answer="updated"))
            else:
                service.submit(uid, aid)
        result = future.result(timeout=15)
    assert result.status == "SUBMITTED"
    assert result.draft_answer == ("updated" if first_action == "save" else "original")
