"""Contratos HTTP de revisão não ampliam o acesso às rotas de tentativas."""

import secrets
from datetime import datetime, timezone
import httpx
import pytest
from sqlalchemy.orm import Session
from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.users.models import User, UserRole
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.challenges.models import Challenge
from app.modules.attempts.models import ChallengeAttempt


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_evaluation_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    with Session(engine) as session:
        users = [User(name="Test", email=f"http-review{i}@example.com", password_hash="unused", role=role) for i, role in enumerate((UserRole.STUDENT, UserRole.STUDENT, UserRole.ADMIN, UserRole.ADMIN))]
        challenge = Challenge(title="Fixture", description="Test", challenge_type="CODE", difficulty="EASY", difficulty_score=100, estimated_minutes=10)
        session.add_all([*users, challenge]); session.flush()
        category = Category(name="Fixture", slug="fixture")
        session.add(category); session.flush()
        session.add(Skill(id=123, name="Fixture", slug="fixture", category_id=category.id))
        session.flush()
        ids = [user.id for user in users]
        snapshot = dict(title="Fixture", description="Test", challenge_type="CODE", difficulty="EASY", difficulty_score=100, estimated_minutes=10, starter_code=None, skills=[dict(skill_id=123, weight=100)])
        attempt = ChallengeAttempt(user_id=ids[0], challenge_id=challenge.id, attempt_number=1, draft_answer="private response", challenge_snapshot=snapshot)
        session.add(attempt); session.flush(); aid = attempt.id
        now = datetime.now(timezone.utc)
        session.add(ChallengeAttempt(user_id=ids[2], challenge_id=challenge.id, attempt_number=1,
            status="SUBMITTED", started_at=now, submitted_at=now, last_activity_at=now,
            draft_answer="own admin response", challenge_snapshot=snapshot))
        session.commit()
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
    owner, stranger, admin, other_admin = [{"Authorization": "Bearer " + create_access_token(uid, settings)} for uid in ids]
    review = f"/api/v1/reviews/attempts/{aid}"
    evaluation = review + "/evaluation"
    owned = f"/api/v1/attempts/{aid}/evaluation"
    payload = {"feedback": "Useful feedback", "skills": [{"skill_id": 123, "classification": "INSUFFICIENT_EVIDENCE", "justification": "Not observable"}]}
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Drafts and the reviewer's own submitted attempts are excluded.
            assert (await client.get('/api/v1/reviews/attempts', headers=admin)).json()['items'] == []
            for method, url, headers, expected in [
                ("GET", review, {}, 401), ("POST", evaluation, {}, 401), ("GET", owned, {}, 401),
                ("GET", review, owner, 403), ("POST", evaluation, stranger, 403),
                ("GET", review, admin, 409), ("POST", evaluation, admin, 409),
                ("GET", owned, owner, 404), ("GET", owned, admin, 404),
                ("GET", "/api/v1/reviews/attempts/2147483647", admin, 404),
            ]:
                response = await client.request(method, url, headers=headers, **({"json": payload} if method == "POST" else {}))
                assert response.status_code == expected
                assert response.headers["cache-control"] == "no-store"
                assert "private response" not in response.text
            assert (await client.post(f"/api/v1/attempts/{aid}/submit", headers=owner)).status_code == 200
            queue = "/api/v1/reviews/attempts"
            assert (await client.get(queue)).status_code == 401
            assert (await client.get(queue, headers=owner)).status_code == 403
            pending = await client.get(queue, headers=admin)
            assert pending.status_code == 200 and pending.headers["cache-control"] == "no-store"
            assert pending.json()["total"] == 1
            assert pending.json()["items"][0]["id"] == aid
            assert "draft_answer" not in pending.text and "user_id" not in pending.text
            assert "private response" not in pending.text
            assert "own admin response" not in pending.text
            beyond = (await client.get(queue + "?limit=1&offset=10", headers=admin)).json()
            assert beyond["total"] == 1 and beyond["items"] == []
            for query in ("limit=0", "limit=51", "offset=-1", "extra=1"):
                assert (await client.get(queue + "?" + query, headers=admin)).status_code == 422
            response = await client.get(review, headers=admin)
            assert response.status_code == 200 and response.json()["evaluation"] is None
            assert response.json()["attempt"]["draft_answer"] == "private response"
            assert "user_id" not in response.json()["attempt"]
            assert (await client.get(f"/api/v1/attempts/{aid}", headers=admin)).status_code == 404
            for url in (review, owned):
                invalid_query = await client.get(url + "?extra=1", headers=admin)
                assert invalid_query.status_code == 422
                assert invalid_query.headers["cache-control"] == "no-store"
            assert (await client.post(evaluation + "?extra=1", headers=admin, json=payload)).status_code == 422
            assert (await client.post(evaluation, headers=admin, json={**payload, "reviewer_id": ids[2]})).status_code == 422
            invalid = {**payload, "skills": [{**payload["skills"][0], "skill_id": 124}]}
            assert (await client.post(evaluation, headers=admin, json=invalid)).status_code == 422
            created = await client.post(evaluation, headers=admin, json=payload)
            assert created.status_code == 201 and created.headers["cache-control"] == "no-store"
            assert (await client.get(queue, headers=admin)).json()["total"] == 0
            data = created.json()
            assert set(data) == {"id", "attempt_id", "rubric_version", "feedback", "skills", "created_at"}
            repeated = await client.post(evaluation, headers=admin, json={**payload, "feedback": " Useful feedback "})
            assert repeated.status_code == 200 and repeated.json() == data
            assert (await client.post(evaluation, headers=other_admin, json=payload)).status_code == 409
            assert (await client.post(evaluation, headers=admin, json={**payload, "feedback": "Different"})).status_code == 409
            assert (await client.get(owned, headers=owner)).json() == data
            assert (await client.get(owned, headers=stranger)).status_code == 404
            assert (await client.get(owned, headers=admin)).status_code == 404
            assert (await client.get(review, headers=other_admin)).json()["evaluation"] == data
            with Session(engine) as session:
                session.get(User, ids[0]).role = UserRole.ADMIN
                session.get(User, ids[2]).role = UserRole.STUDENT
                session.commit()
            assert (await client.get(review, headers=owner)).status_code == 403
            assert (await client.post(evaluation, headers=owner, json=payload)).status_code == 403
            assert (await client.get(review, headers=admin)).status_code == 403
            assert (await client.get(queue, headers=admin)).status_code == 403
            assert (await client.get(owned, headers=owner)).json() == data
    finally:
        app.dependency_overrides.clear()
