"""Isolamento HTTP e concorrência entre tentativas distintas."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timezone
import secrets
import pytest
import httpx
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.modules.users.models import User, UserRole
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill, SkillEvidence
from app.modules.skills.progress_repository import ProgressRepository
from app.modules.challenges.models import Challenge
from app.modules.attempts.models import ChallengeAttempt
from app.modules.evaluation.service import EvaluationService
from app.modules.evaluation.schemas import EvaluationCreate
from app.modules.skills.policy import calculate_change, EvidenceTotals


@pytest.fixture
def progress_context(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        users = [User(name="Fixture", email=f"progress{i}@test.com", password_hash="unused",
                      role=UserRole.ADMIN if i == 2 else UserRole.STUDENT) for i in range(3)]
        category = Category(name="Code", slug="code")
        challenge = Challenge(title="Test", description="Test", challenge_type="CODE", difficulty="MEDIUM", difficulty_score=500, estimated_minutes=10)
        session.add_all([*users, category, challenge]); session.flush()
        skills = [Skill(name=f"Skill {i}", slug=f"skill-{i}", category_id=category.id, is_active=False) for i in range(2)]
        session.add_all(skills); session.flush()
        snapshot = dict(title="Test", description="Test", challenge_type="CODE", difficulty="MEDIUM", difficulty_score=500, estimated_minutes=10, starter_code=None,
                        skills=[dict(skill_id=s.id, weight=50) for s in skills])
        now = datetime.now(timezone.utc)
        attempts = [ChallengeAttempt(user_id=users[0].id, challenge_id=challenge.id, attempt_number=n,
                    status="SUBMITTED", draft_answer="answer", challenge_snapshot=snapshot,
                    started_at=now, submitted_at=now, last_activity_at=now) for n in (1, 2)]
        session.add_all(attempts); session.commit()
        yield engine, [u.id for u in users], [a.id for a in attempts], [s.id for s in skills]


def test_distinct_attempts_are_serialized(progress_context, monkeypatch):
    engine, users, attempts, skills = progress_context
    barrier = Barrier(2)
    original = ProgressRepository.lock_user
    def synchronized_lock(repository, user_id):
        barrier.wait(timeout=10)
        original(repository, user_id)
    monkeypatch.setattr(ProgressRepository, "lock_user", synchronized_lock)
    def review(index):
        with Session(engine) as session:
            session.execute(text("SET LOCAL lock_timeout = '10s'"))
            data = EvaluationCreate(feedback="Feedback", skills=[dict(skill_id=s, classification="MET" if index == 0 else "NOT_MET", justification="Evidence") for s in skills])
            return EvaluationService(session).evaluate(users[2], attempts[index], data)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(review, (0, 1)))
    assert all(created for _, created in results)
    evaluation_order = {result.id: index for index, (result, _) in enumerate(results)}
    with Session(engine) as session:
        for skill_id in skills:
            history = list(session.scalars(select(SkillEvidence).where(SkillEvidence.skill_id == skill_id).order_by(SkillEvidence.id)))
            assert len(history) == 2
            assert history[1].before_state == history[0].after_state
            score, totals = 500, EvidenceTotals()
            for evidence in history:
                index = evaluation_order[evidence.evaluation_id]
                change = calculate_change(score, 500, 50, index+1, "MET" if index == 0 else "NOT_MET", totals)
                score, totals = change.score, change.totals
            progress = session.scalar(select(UserSkill).where(UserSkill.skill_id == skill_id))
            assert progress.score == score and progress.mass == totals.mass
            assert progress.confidence == change.confidence
            assert progress.attempts == 2 and progress.successful_attempts == 1


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_progress_http_ownership(progress_context, monkeypatch):
    engine, users, attempts, skills = progress_context
    with Session(engine) as session:
        data = EvaluationCreate(feedback="Feedback", skills=[dict(skill_id=s, classification="MET", justification="Evidence") for s in skills])
        EvaluationService(session).evaluate(users[2], attempts[0], data)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")
    from app.main import app
    from app.database.connection import get_session
    from app.modules.users.dependencies import get_jwt_settings
    from app.core.config import JWTSettings
    from app.core.tokens import create_access_token
    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
    def sessions():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = sessions
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    headers = [{"Authorization": "Bearer " + create_access_token(uid, settings)} for uid in users]
    url = "/api/v1/users/me/skills"
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get(url)).status_code == 401
            for auth in headers[1:]:
                response = await client.get(url, headers=auth)
                assert response.status_code == 200 and response.json()["items"] == []
                assert response.json()["total"] == 0
            response = await client.get(url, headers=headers[0])
            assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
            body = response.json()
            assert body["total"] == 2 and [i["skill_id"] for i in body["items"]] == skills
            assert set(body["items"][0]) == {"skill_id", "score", "confidence", "attempts", "successful_attempts", "last_practiced_at", "updated_at"}
            assert isinstance(body["items"][0]["confidence"], str)
            page = (await client.get(url+"?limit=1&offset=1", headers=headers[0])).json()
            assert page["total"] == 2 and page["items"] == body["items"][1:]
            assert (await client.get(url+"?offset=20", headers=headers[0])).json()["items"] == []
            for query in ("limit=0", "limit=101", "offset=-1", "user_id="+str(users[0]), "is_active=true"):
                rejected = await client.get(url+"?"+query, headers=headers[2])
                assert rejected.status_code == 422 and rejected.headers["cache-control"] == "no-store"
            assert (await client.get(url, headers=headers[0])).json() == body
    finally:
        app.dependency_overrides.clear()
