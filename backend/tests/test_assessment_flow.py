"""Fluxo autenticado e concorrência de provas e respostas."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timezone
import secrets
import httpx
import pytest
from sqlalchemy.orm import Session
from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.users.models import User, DeclaredExperience
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.onboarding.models import UserInterest
from app.modules.assessments.models import Assessment, AssessmentQuestion
from app.modules.assessments.models import AssessmentResult
from app.modules.assessments.service import AssessmentService, AssessmentConflict
from app.modules.assessments.schemas import AssessmentCreate, AnswerCreate


def seed(engine):
    with Session(engine) as session:
        user = User(name="User", email="flow@example.com", password_hash="unused",
                    declared_experience=DeclaredExperience.BASIC, onboarding_completed=True)
        other = User(name="Other", email="other-flow@example.com", password_hash="unused")
        category = Category(name="Logic", slug="logic")
        session.add_all([user, other, category]); session.flush()
        skill = Skill(name="Logic", slug="logic", category_id=category.id)
        session.add(skill); session.flush()
        session.add(UserInterest(user_id=user.id, category_id=category.id))
        for index in range(3):
            session.add(AssessmentQuestion(code=f"q-{index}", skill_id=skill.id, prompt=f"Question {index}",
                options={"A": "one", "B": "two", "C": "three", "D": "four"}, correct_option="A"))
        session.commit()
        return user.id, other.id, skill.id


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_assessment_http(migrated_database, monkeypatch):
    engine, _ = migrated_database
    uid, oid, sid = seed(engine)
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
    other_headers = {"Authorization": "Bearer " + create_access_token(oid, settings)}
    url = "/api/v1/assessments"
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.post(url, json={"skill_ids": [sid]})).status_code == 401
            assert (await client.post(url, headers=other_headers, json={"skill_ids": [sid]})).status_code == 409
            assert (await client.post(url, headers=headers, json={"skill_ids": [2147483647]})).status_code == 404
            with Session(engine) as session:
                question = session.query(AssessmentQuestion).first()
                question.is_active = False
                qid = question.id
                session.commit()
            assert (await client.post(url, headers=headers, json={"skill_ids": [sid]})).status_code == 409
            with Session(engine) as session:
                session.get(AssessmentQuestion, qid).is_active = True
                session.commit()
            created = await client.post(url, headers=headers, json={"skill_ids": [sid]})
            assert created.status_code == 201
            data = created.json()
            aid, iid = data["id"], data["items"][0]["id"]
            finish_url = f"{url}/{aid}/finish"
            assert (await client.post(finish_url, headers=other_headers)).status_code == 404
            assert (await client.post(finish_url, headers=headers)).status_code == 409
            assert (await client.post(finish_url, headers=headers, json={"score": 1000})).status_code == 422
            assert len(data["items"]) == 3 and data["results"] == []
            assert "correct_option" not in created.text and "user_id" not in created.text
            assert created.headers["Cache-Control"] == "no-store"
            assert (await client.post(url, headers=headers, json={"skill_ids": [sid]})).status_code == 409
            assert (await client.get(f"{url}/{aid}", headers=other_headers)).status_code == 404
            answer_url = f"{url}/{aid}/answers"
            assert (await client.post(answer_url, headers=other_headers, json={"item_id": iid, "selected_option": "A"})).status_code == 404
            assert (await client.post(answer_url, headers=headers, json={"item_id": 2147483647, "selected_option": "A"})).status_code == 404
            for option in ("B", "A", "A"):
                answered = await client.post(answer_url, headers=headers, json={"item_id": iid, "selected_option": option})
                assert answered.status_code == 200 and answered.json()["selected_option"] == option
                assert "correct_option" not in answered.text
            assert (await client.get(f"{url}/{aid}?user_id={oid}", headers=headers)).status_code == 422
            with Session(engine) as session:
                session.get(Skill, sid).is_active = False
                session.get(AssessmentQuestion, qid).prompt = "Changed"
                session.commit()
            read = await client.get(f"{url}/{aid}", headers=headers)
            assert read.status_code == 200 and read.json()["items"][0]["prompt"] == "Question 0"
            for item in data["items"][1:]:
                assert (await client.post(answer_url, headers=headers, json={"item_id": item["id"], "selected_option": "B"})).status_code == 200
            finished = await client.post(finish_url, headers=headers)
            assert finished.status_code == 200 and finished.json()["completed_at"] is not None
            assert finished.json()["results"] == [{"skill_id": sid, "score": 333, "confidence": 0.0, "correct_count": 1, "question_count": 3}]
            assert "correct_option" not in finished.text
            assert (await client.post(finish_url, headers=headers)).json() == finished.json()
            assert (await client.post(answer_url, headers=headers, json={"item_id": iid, "selected_option": "B"})).status_code == 409
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)


def test_concurrent_start_and_answers(migrated_database):
    engine, _ = migrated_database
    uid, _, sid = seed(engine)
    barrier = Barrier(2)
    def start():
        with Session(engine) as session:
            barrier.wait(timeout=15)
            try:
                return AssessmentService(session).create(uid, AssessmentCreate(skill_ids=[sid])).id
            except AssessmentConflict:
                return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: start(), range(2)))
    assert results.count(None) == 1
    aid = next(value for value in results if value is not None)
    with Session(engine) as session:
        iid = AssessmentService(session).get(uid, aid).items[0].id
    def answer(option):
        with Session(engine) as session:
            barrier.wait(timeout=15)
            return AssessmentService(session).answer(uid, aid, AnswerCreate(item_id=iid, selected_option=option)).selected_option
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(answer, ["A", "B"])) == ["A", "B"]
    with Session(engine) as session:
        result = AssessmentService(session).get(uid, aid)
        assert len(result.items) == 3 and result.items[0].selected_option in {"A", "B"}


def test_finish_rollback_and_concurrency(migrated_database):
    engine, _ = migrated_database
    uid, _, sid = seed(engine)
    with Session(engine) as session:
        service = AssessmentService(session)
        assessment = service.create(uid, AssessmentCreate(skill_ids=[sid]))
        aid = assessment.id
        for item in assessment.items:
            service.answer(uid, aid, AnswerCreate(item_id=item.id, selected_option="A"))
        original = service.repository.finish
        def fail_after_flush(*args):
            original(*args)
            raise RuntimeError("simulated failure")
        service.repository.finish = fail_after_flush
        with pytest.raises(RuntimeError):
            service.finish(uid, aid)
        assert service.get(uid, aid).completed_at is None
        assert session.query(AssessmentResult).filter_by(assessment_id=aid).count() == 0
    barrier = Barrier(2)
    def finish():
        with Session(engine) as session:
            session.get(Assessment, aid)
            barrier.wait(timeout=15)
            return AssessmentService(session).finish(uid, aid)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: finish(), range(2)))
    assert results[0] == results[1]
    assert results[0].results[0].score == 1000
    with Session(engine) as session:
        assert session.query(AssessmentResult).filter_by(assessment_id=aid).count() == 1
        assert AssessmentService(session).create(uid, AssessmentCreate(skill_ids=[sid])).id != aid
