"""Contagens, paginação e isolamento do resumo no PostgreSQL real."""

from datetime import datetime, timedelta, timezone
import secrets
import httpx
import pytest
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from app.modules.users.models import User, UserRole
from app.modules.users.auth_service import InvalidCredentials
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill
from app.modules.assessments.models import AssessmentResult  # Registra FK do progresso.
from app.modules.onboarding.models import UserGoal, UserInterest
from app.modules.challenges.models import Challenge
from app.modules.attempts.models import ChallengeAttempt
from app.modules.evaluation.models import AttemptEvaluation, AttemptEvaluationSkill
from app.modules.dashboard.service import DashboardService
from app.modules.dashboard.schemas import DashboardQuery


@pytest.fixture
def dashboard_context(migrated_database):
    engine, _ = migrated_database
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        users = [User(name=f"Person {i}", email=f"dashboard{i}@example.com", password_hash="private",
                      role=UserRole.ADMIN if i == 1 else UserRole.STUDENT) for i in range(3)]
        categories = [Category(name=f"Category {i}", slug=f"category-{i}") for i in range(2)]
        challenge = Challenge(title="Fixture", description="Fixture", challenge_type="CODE",
            difficulty="EASY", difficulty_score=100, estimated_minutes=10)
        session.add_all([*users, *categories, challenge]); session.flush()
        skills = [Skill(name=f"Skill {i}", slug=f"skill-{i}", category_id=categories[0].id,
                        is_active=i == 0) for i in range(3)]
        session.add_all(skills); session.flush()
        session.add_all([UserInterest(user_id=users[0].id, category_id=c.id) for c in reversed(categories)])
        session.add(UserGoal(user_id=users[0].id, goal_type="Backend", description="Declared goal"))
        session.add(UserGoal(user_id=users[0].id, goal_type="Secondary", is_primary=False))
        for index, skill in enumerate(skills):
            session.add(UserSkill(user_id=users[0 if index < 2 else 1].id, skill_id=skill.id,
                score=520, confidence="0.047619", attempts=1, successful_attempts=1,
                initial_score=500, mass=1, residual_sum="0.5", squared_residual_sum="0.25",
                last_practiced_at=now, updated_at=now))
        for n in range(1, 6):
            owner = users[1] if n == 5 else users[0]
            attempt = ChallengeAttempt(user_id=owner.id, challenge_id=challenge.id, attempt_number=n,
                status="IN_PROGRESS" if n == 4 else "SUBMITTED", challenge_snapshot={},
                started_at=now-timedelta(days=1), submitted_at=None if n == 4 else now, last_activity_at=now)
            session.add(attempt); session.flush()
            if n in (1, 2):
                evaluation = AttemptEvaluation(attempt_id=attempt.id, reviewer_id=users[1].id, feedback="Fixture")
                session.add(evaluation); session.flush()
                session.add_all([AttemptEvaluationSkill(evaluation_id=evaluation.id, skill_id=s.id,
                    classification="INSUFFICIENT_EVIDENCE" if n == 2 else "MET", justification="Fixture") for s in skills[:2]])
        session.commit()
        return engine, [u.id for u in users], [s.id for s in skills]


def test_dashboard_counts_and_pagination(dashboard_context):
    engine, users, skills = dashboard_context
    statements = []
    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    with Session(engine) as session:
        session.execute(text("SET TRANSACTION READ ONLY"))
        event.listen(engine, "before_cursor_execute", record)
        try:
            result = DashboardService(session).get_owned(users[0], DashboardQuery(limit=1))
        finally:
            event.remove(engine, "before_cursor_execute", record)
        assert len(statements) == 1
        assert result.summary.model_dump() == dict(tracked_skills=2, submitted_attempts=3, pending_reviews=1)
        assert result.profile.primary_goal.goal_type == "Backend"
        assert [i.name for i in result.profile.interests] == ["Category 0", "Category 1"]
        assert result.progress.total == 2 and result.progress.items[0].skill_id == skills[0]
        second = DashboardService(session).get_owned(users[0], DashboardQuery(limit=1, offset=1))
        assert second.summary == result.summary and second.progress.items[0].skill_id == skills[1]
        assert not second.progress.items[0].is_active
        assert second.progress.items[0].model_dump(mode="json")["confidence"] == "0.047619"
        beyond = DashboardService(session).get_owned(users[0], DashboardQuery(offset=100))
        assert beyond.progress.items == [] and beyond.progress.total == 2 and beyond.summary == result.summary
        admin = DashboardService(session).get_owned(users[1], DashboardQuery())
        assert [i.skill_id for i in admin.progress.items] == [skills[2]]
        assert admin.summary.submitted_attempts == admin.summary.pending_reviews == 1
        assert admin.profile.primary_goal is None and admin.profile.interests == []
        empty = DashboardService(session).get_owned(users[2], DashboardQuery())
        assert empty.summary.model_dump() == dict(tracked_skills=0, submitted_attempts=0, pending_reviews=0)
        assert empty.progress.items == [] and not empty.profile.onboarding_completed
        with pytest.raises(InvalidCredentials): DashboardService(session).get_owned(2147483647, DashboardQuery())
        assert session.in_transaction() and not session.new and not session.dirty
    with Session(engine) as session:
        session.get(Skill, skills[1]).name = "Renamed inactive skill"
        session.commit()
        result = DashboardService(session).get_owned(users[0], DashboardQuery())
        assert result.progress.items[1].name == "Renamed inactive skill"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_dashboard_http(dashboard_context, monkeypatch):
    engine, users, skills = dashboard_context
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
    app.dependency_overrides[get_session] = sessions
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    def auth(uid): return {"Authorization": "Bearer " + create_access_token(uid, settings)}
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for headers in ({}, auth(2147483647)):
                response = await client.get("/api/v1/dashboard", headers=headers)
                assert response.status_code == 401 and response.headers["cache-control"] == "no-store"
                assert response.headers["www-authenticate"] == "Bearer"
            response = await client.get("/api/v1/dashboard", headers=auth(users[0]))
            assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
            body = response.json()
            assert set(body) == {"profile", "summary", "progress"}
            assert set(body["profile"]) == {"name", "onboarding_completed", "primary_goal", "interests"}
            assert set(body["progress"]["items"][0]) == {"skill_id", "name", "is_active", "score", "confidence", "attempts", "successful_attempts", "last_practiced_at", "updated_at"}
            for params in ({"limit": 0}, {"limit": 51}, {"offset": -1}, {"limit": "abc"}, {"user_id": users[0]}):
                invalid = await client.get("/api/v1/dashboard", params=params, headers=auth(users[1]))
                assert invalid.status_code == 422 and invalid.headers["cache-control"] == "no-store"
            admin = (await client.get("/api/v1/dashboard", headers=auth(users[1]))).json()
            assert [i["skill_id"] for i in admin["progress"]["items"]] == [skills[2]]
            empty = await client.get("/api/v1/dashboard", headers=auth(users[2]))
            assert empty.status_code == 200 and empty.json()["progress"]["items"] == []
    finally:
        app.dependency_overrides.clear()
