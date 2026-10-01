"""Owner-only attempt history against disposable PostgreSQL."""
from datetime import datetime, timedelta, timezone
import secrets

import httpx
import pytest
from sqlalchemy import event, text
from sqlalchemy.orm import Session

from app.modules.users.models import User, UserRole
from app.modules.challenges.models import Challenge
from app.modules.attempts.models import ChallengeAttempt
from app.modules.attempts.schemas import AttemptQuery
from app.modules.attempts.service import AttemptService


@pytest.fixture
def history(migrated_database):
    engine, _ = migrated_database
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        users = [User(name=f"Reader {i}", email=f"reader{i}@example.com", password_hash="fixture",
                      role=UserRole.ADMIN if i == 1 else UserRole.STUDENT) for i in range(3)]
        challenge = Challenge(title="Current title", description="Changed", challenge_type="CODE",
                              difficulty="EASY", difficulty_score=100, estimated_minutes=10, is_active=False)
        session.add_all([*users, challenge]); session.flush()
        ids = []
        for index in range(4):
            activity = now - timedelta(days=1) if index == 1 else now
            attempt = ChallengeAttempt(user_id=users[1 if index == 3 else 0].id,
                challenge_id=challenge.id, attempt_number=index + 1,
                status="IN_PROGRESS" if index == 2 else "SUBMITTED",
                draft_answer="Private answer", challenge_snapshot={"title": f"Historical {index}"},
                started_at=now-timedelta(days=2), last_activity_at=activity,
                submitted_at=None if index == 2 else activity)
            session.add(attempt); session.flush(); ids.append(attempt.id)
        session.commit()
        return engine, [u.id for u in users], ids


def test_history_snapshot_order_and_read_only(history):
    engine, users, ids = history
    statements = []
    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    with Session(engine) as session:
        session.execute(text("SET TRANSACTION READ ONLY"))
        event.listen(engine, "before_cursor_execute", record)
        try:
            first = AttemptService(session).list_owned(users[0], AttemptQuery(limit=2))
        finally:
            event.remove(engine, "before_cursor_execute", record)
        assert len(statements) == 1
        assert [i.id for i in first.items] == [ids[2], ids[0]]
        assert first.items[0].title == "Historical 2"
        assert first.items[0].submitted_at is None
        assert first.total == 3 and first.limit == 2 and first.offset == 0
        second = AttemptService(session).list_owned(users[0], AttemptQuery(limit=2, offset=2))
        assert [i.id for i in second.items] == [ids[1]] and second.total == 3
        beyond = AttemptService(session).list_owned(users[0], AttemptQuery(offset=100))
        assert beyond.items == [] and beyond.total == 3
        admin = AttemptService(session).list_owned(users[1], AttemptQuery())
        assert [i.id for i in admin.items] == [ids[3]] and admin.total == 1
        empty = AttemptService(session).list_owned(users[2], AttemptQuery())
        assert empty.items == [] and empty.total == 0
        assert session.in_transaction() and not session.dirty and not session.new


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_history_http(history, monkeypatch):
    engine, users, ids = history
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    from app.main import app
    from app.database.connection import get_session
    from app.modules.users.dependencies import get_jwt_settings
    from app.core.config import JWTSettings
    from app.core.tokens import create_access_token
    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
    def sessions():
        with Session(engine) as session:
            session.execute(text("SET TRANSACTION READ ONLY"))
            yield session
    def auth(uid):
        return {"Authorization": "Bearer " + create_access_token(uid, settings)}
    app.dependency_overrides[get_session] = sessions
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for headers in ({}, auth(2147483647)):
                response = await client.get("/api/v1/attempts", headers=headers)
                assert response.status_code == 401
                assert response.headers["cache-control"] == "no-store"
            response = await client.get("/api/v1/attempts", headers=auth(users[0]))
            assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
            body = response.json()
            assert set(body) == {"items", "total", "limit", "offset"}
            assert body["total"] == 3 and body["limit"] == 10 and body["offset"] == 0
            assert set(body["items"][0]) == {"id", "challenge_id", "title", "status", "attempt_number",
                                           "started_at", "submitted_at", "last_activity_at"}
            for params in ({"limit": 0}, {"limit": 51}, {"offset": -1}, {"limit": "abc"},
                           {"offset": "1.5"}, {"user_id": users[0]}, {"status": "SUBMITTED"}, {"challenge_id": 1}):
                invalid = await client.get("/api/v1/attempts", params=params, headers=auth(users[1]))
                assert invalid.status_code == 422 and invalid.headers["cache-control"] == "no-store"
            for uid, expected in ((users[1], [ids[3]]), (users[2], [])):
                response = await client.get("/api/v1/attempts?limit=50", headers=auth(uid))
                assert response.status_code == 200
                assert [i["id"] for i in response.json()["items"]] == expected
            beyond = await client.get("/api/v1/attempts?offset=100", headers=auth(users[0]))
            assert beyond.json()["items"] == [] and beyond.json()["total"] == 3
            # Pagination is accepted only by the collection route.
            for method, path, kwargs in (
                ("GET", f"/attempts/{ids[0]}", {}),
                ("PATCH", f"/attempts/{ids[0]}", {"json": {"draft_answer": "x"}}),
                ("POST", f"/attempts/{ids[0]}/submit", {}),
                ("POST", "/challenges/1/attempts", {}),
            ):
                response = await client.request(method, "/api/v1" + path + "?limit=1", headers=auth(users[0]), **kwargs)
                assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
