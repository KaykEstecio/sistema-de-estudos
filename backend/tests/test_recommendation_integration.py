"""Recomendação sobre PostgreSQL real e contrato HTTP isolado por identidade."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import secrets

import httpx
import pytest
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session
from app.modules.users.models import User, UserRole
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill
from app.modules.onboarding.models import UserInterest
from app.modules.assessments.models import Assessment, AssessmentResult
from app.modules.challenges.models import Challenge, ChallengeSkill
from app.modules.attempts.models import ChallengeAttempt
from app.modules.evaluation.models import AttemptEvaluation
from app.modules.recommendations.schemas import RecommendationQuery
from app.modules.recommendations.service import RecommendationService, RecommendationSkillUnavailable

NOW = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)


@pytest.fixture
def recommendation_context(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        users = [User(name="Fixture", email=f"recommend{i}@example.com", password_hash="unused",
                      role=UserRole.ADMIN if i == 2 else UserRole.STUDENT) for i in range(3)]
        category, outside = Category(name="Code", slug="code"), Category(name="Outside", slug="outside")
        session.add_all([*users, category, outside]); session.flush()
        skills = [Skill(name=name, slug=name, category_id=cat, is_active=active) for name, cat, active in [
            ("focus", category.id, True), ("secondary", outside.id, True),
            ("inactive", category.id, False), ("empty", category.id, True)]]
        session.add_all(skills); session.flush()
        for user in users:
            session.add(UserInterest(user_id=user.id, category_id=category.id))
        for user, score in [(users[0], 500), (users[1], 900)]:
            session.add(UserSkill(user_id=user.id, skill_id=skills[0].id, score=score, confidence=Decimal("0.20"),
                attempts=5, successful_attempts=3, initial_score=500, mass=5, residual_sum=0,
                squared_residual_sum=1, last_practiced_at=NOW-timedelta(days=20)))
        for user, skill, score, date in [(users[0], skills[0], 950, NOW),
                (users[0], skills[1], 300, NOW-timedelta(days=1)),
                (users[0], skills[1], 400, NOW-timedelta(days=1)),
                (users[0], skills[1], 900, NOW+timedelta(days=1)),
                (users[1], skills[1], 999, NOW)]:
            assessment = Assessment(user_id=user.id, started_at=NOW-timedelta(days=2), completed_at=date)
            session.add(assessment); session.flush()
            session.add(AssessmentResult(assessment_id=assessment.id, skill_id=skill.id,
                score=score, confidence=0, correct_count=1, question_count=3))
        challenges = {}
        for name, difficulty in [("new", 500), ("near", 480), ("mixed", 500), ("hidden", 100),
                ("inactive", 100), ("open", 500), ("pending", 500), ("recent", 500),
                ("old", 500), ("future", 500), ("hard", 800), ("intro", 100)]:
            challenge = Challenge(title=name, description="Fixture", challenge_type="CODE", difficulty="MEDIUM",
                difficulty_score=difficulty, estimated_minutes=10, is_active=name != "inactive")
            session.add(challenge); session.flush()
            challenges[name] = challenge.id
            links = [(skills[0].id, 100)]
            if name in ("mixed", "hidden"):
                links = [(skills[0].id, 50), (skills[1 if name == "mixed" else 2].id, 50)]
            session.add_all([ChallengeSkill(challenge_id=challenge.id, skill_id=sid, weight=weight) for sid, weight in links])
            if name in ("open", "pending", "recent", "old", "future"):
                submitted = None if name == "open" else NOW-timedelta(days=20 if name == "old" else 1)
                if name == "future": submitted = NOW+timedelta(days=1)
                attempt = ChallengeAttempt(user_id=users[0].id, challenge_id=challenge.id,
                    attempt_number=1, status="IN_PROGRESS" if submitted is None else "SUBMITTED",
                    challenge_snapshot={"skills": links}, started_at=NOW-timedelta(days=30),
                    submitted_at=submitted, last_activity_at=submitted or NOW)
                session.add(attempt); session.flush()
                if name in ("recent", "old", "future"):
                    session.add(AttemptEvaluation(attempt_id=attempt.id, reviewer_id=users[2].id,
                                                  feedback="Historical qualitative review", created_at=NOW))
        session.commit()
        return engine, [user.id for user in users], [skill.id for skill in skills], challenges


def test_recommendation_context_and_read_only(recommendation_context):
    engine, users, skills, challenges = recommendation_context
    statements = []
    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    with Session(engine) as session:
        session.execute(text("SET TRANSACTION READ ONLY"))
        event.listen(engine, "before_cursor_execute", record)
        try:
            response = RecommendationService(session).recommend(users[0], RecommendationQuery(skill_id=skills[0], limit=10), now=NOW)
        finally:
            event.remove(engine, "before_cursor_execute", record)
        assert len(statements) == 1 and statements[0].startswith("WITH")
        names = [item.title for item in response.items]
        assert names == ["new", "old", "near", "mixed", "intro", "recent"]
        mixed = next(item for item in response.items if item.title == "mixed")
        assert mixed.kind == "EXPLORATION"
        assert mixed.skills[0].source == "USER_SKILL" and mixed.skills[0].reference_score == 500
        assert mixed.skills[1].source == "ASSESSMENT" and mixed.skills[1].reference_score == 400
        assert "diagnóstico" in mixed.reason
        assert not next(item for item in response.items if item.title == "old").practiced_recently
        assert response.items[-1].practiced_recently and "menor prioridade" in response.items[-1].reason
        assert RecommendationService(session).recommend(users[0], RecommendationQuery(skill_id=skills[0]), now=NOW).items == response.items[:5]
        empty = RecommendationService(session).recommend(users[0], RecommendationQuery(skill_id=skills[3]), now=NOW)
        assert empty.items == [] and empty.empty_reason == "NO_ELIGIBLE_CHALLENGES"
        for sid in (skills[1], skills[2], 2147483647):
            with pytest.raises(RecommendationSkillUnavailable):
                RecommendationService(session).recommend(users[0], RecommendationQuery(skill_id=sid), now=NOW)
        assert not session.new and not session.dirty and not session.deleted
        assert session.in_transaction()  # O service não encerra a transação de leitura.
    with Session(engine) as session:
        other = RecommendationService(session).recommend(users[1], RecommendationQuery(skill_id=skills[0], limit=10), now=NOW)
        assert "hard" in [item.title for item in other.items]
        assert "pending" in [item.title for item in other.items]  # Histórico pertence ao dono.
        admin = RecommendationService(session).recommend(users[2], RecommendationQuery(skill_id=skills[0]), now=NOW)
        assert [item.title for item in admin.items] == ["intro"]
        assert admin.items[0].skills[0].source == "NONE"
        assert admin.items[0].skills[0].reference_score is None
        # Desativação atual afeta imediatamente uma nova leitura.
        session.get(Skill, skills[0]).is_active = False
        session.commit()
        with pytest.raises(RecommendationSkillUnavailable):
            RecommendationService(session).recommend(users[0], RecommendationQuery(skill_id=skills[0]), now=NOW)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_recommendation_http(recommendation_context, monkeypatch):
    engine, users, skills, _ = recommendation_context
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
    auth = {"Authorization": "Bearer " + create_access_token(users[2], settings)}
    url = "/api/v1/recommendations"
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            anonymous = await client.get(url, params={"skill_id": skills[0]})
            assert anonymous.status_code == 401 and anonymous.headers["cache-control"] == "no-store"
            assert anonymous.headers["www-authenticate"] == "Bearer"
            response = await client.get(url, params={"skill_id": skills[0]}, headers=auth)
            assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
            body = response.json()
            assert set(body) == {"policy_version", "generated_at", "skill_id", "limit", "items", "empty_reason"}
            assert [item["title"] for item in body["items"]] == ["intro"]
            assert body["items"][0]["skills"][0] == dict(skill_id=skills[0], weight=100, source="NONE", reference_score=None, confidence=None)
            for params in ({}, {"skill_id": 0}, {"skill_id": skills[0], "limit": 11},
                           {"skill_id": skills[0], "user_id": users[0]}, {"skill_id": skills[0], "offset": 1}):
                invalid = await client.get(url, params=params, headers=auth)
                assert invalid.status_code == 422 and invalid.headers["cache-control"] == "no-store"
            errors = []
            for sid in (skills[1], skills[2], 2147483647):
                missing = await client.get(url, params={"skill_id": sid}, headers=auth)
                assert missing.status_code == 404 and missing.headers["cache-control"] == "no-store"
                errors.append(missing.json())
            assert errors[0] == errors[1] == errors[2]
            empty = await client.get(url, params={"skill_id": skills[3]}, headers=auth)
            assert empty.status_code == 200 and empty.json()["empty_reason"] == "NO_ELIGIBLE_CHALLENGES"
    finally:
        app.dependency_overrides.clear()
