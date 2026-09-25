"""Duas identidades percorrem o fluxo público sem compartilhar perfil."""

import secrets
import httpx
import pytest
from sqlalchemy.orm import Session
from app.core.config import JWTSettings
from app.modules.users.models import User, UserRole


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_two_accounts_onboarding(migrated_database, monkeypatch):
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
    try:
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                identities = []
                for index in range(2):
                    email = f"person{index}@example.com"
                    password = "Test password long!"
                    registered = await client.post("/api/v1/auth/register", json={"name": "Person", "email": email, "password": password})
                    assert registered.status_code == 201
                    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
                    assert login.status_code == 200
                    identities.append((registered.json()["id"], {"Authorization": "Bearer " + login.json()["access_token"]}))
                admin_id, admin_headers = identities[0]
                student_id, student_headers = identities[1]
                with Session(engine) as session:
                    session.get(User, admin_id).role = UserRole.ADMIN
                    session.commit()
                category = await client.post("/api/v1/categories", headers=admin_headers, json={"name": "Logic", "slug": "logic"})
                assert category.status_code == 201
                cid = category.json()["id"]
                url = "/api/v1/onboarding"
                profile = {"declared_experience": "NEVER_PROGRAMMED", "interest_category_ids": [cid],
                           "primary_goal": {"goal_type": "Learn logic"}}
                response = await client.post(url, headers=student_headers, json=profile)
                assert response.status_code == 201
                student_before = response.json()
                assert set(student_before) == {"declared_experience", "interest_category_ids", "primary_goal", "onboarding_completed"}
                assert (await client.get(url, headers=admin_headers)).json()["onboarding_completed"] is False
                admin_profile = {**profile, "declared_experience": "ADVANCED", "primary_goal": {"goal_type": "Practice"}}
                assert (await client.post(url, headers=admin_headers, json=admin_profile)).status_code == 201
                assert (await client.patch(url, headers=admin_headers, json={"user_id": student_id, "declared_experience": "BASIC"})).status_code == 422
                assert (await client.get(url + f"?user_id={student_id}", headers=admin_headers)).status_code == 422
                assert (await client.patch(url, headers=admin_headers, json={"declared_experience": "INTERMEDIATE"})).status_code == 200
                assert (await client.get(url, headers=student_headers)).json() == student_before
                invalid = await client.patch(url, headers=student_headers, json={"interest_category_ids": [2147483647], "declared_experience": "ADVANCED"})
                assert invalid.status_code == 404
                assert (await client.get(url, headers=student_headers)).json() == student_before
                for _, headers in identities:
                    me = (await client.get("/api/v1/auth/me", headers=headers)).json()
                    assert me["onboarding_completed"] is True
                    assert "score" not in me and "password_hash" not in me
                assert (await client.get("/api/v1/categories", headers=student_headers)).json()["total"] == 1
                skill = await client.post("/api/v1/skills", headers=admin_headers,
                                          json={"name": "Logic", "slug": "logic", "category_id": cid})
                assert skill.status_code == 201
                sid = skill.json()["id"]
                from app.modules.assessments.import_service import QuestionImportService
                from app.modules.assessments.schemas import QuestionCreate
                with Session(engine) as session:
                    QuestionImportService(session).import_questions([
                        QuestionCreate(code=f"integration-{index}", skill_id=sid, prompt="Synthetic question",
                            options={"A": "one", "B": "two", "C": "three", "D": "four"}, correct_option="A")
                        for index in range(3)])
                assessment_url = "/api/v1/assessments"
                created = await client.post(assessment_url, headers=student_headers, json={"skill_ids": [sid]})
                assert created.status_code == 201
                aid = created.json()["id"]
                assert (await client.get(f"{assessment_url}/{aid}", headers=admin_headers)).status_code == 404
                assert (await client.post(f"{assessment_url}/{aid}/finish", headers=admin_headers)).status_code == 404
                for item in created.json()["items"]:
                    answer = await client.post(f"{assessment_url}/{aid}/answers", headers=student_headers,
                                              json={"item_id": item["id"], "selected_option": "A"})
                    assert answer.status_code == 200
                finished = await client.post(f"{assessment_url}/{aid}/finish", headers=student_headers)
                assert finished.status_code == 200 and "correct_option" not in finished.text
                assert finished.json()["results"][0]["score"] == 1000
                assert finished.json()["results"][0]["confidence"] == 0
                assert (await client.post(f"{assessment_url}/{aid}/finish", headers=student_headers)).json() == finished.json()
                assert (await client.get(url, headers=student_headers)).json() == student_before
                assert (await client.get(f"/api/v1/skills/{sid}", headers=student_headers)).json() == skill.json()
                challenges_url = "/api/v1/challenges"
                challenge = await client.post(challenges_url, headers=admin_headers, json={
                    "title": "Integration fixture", "description": "Synthetic content",
                    "challenge_type": "CODE", "difficulty": "EASY", "difficulty_score": 100,
                    "estimated_minutes": 10, "skills": [{"skill_id": sid, "weight": 100}]})
                assert challenge.status_code == 201
                detail_url = f"{challenges_url}/{challenge.json()['id']}"
                assert (await client.get(detail_url, headers=student_headers)).status_code == 404
                assert (await client.patch(detail_url, headers=student_headers, json={"is_active": True})).status_code == 403
                published = await client.patch(detail_url, headers=admin_headers, json={"is_active": True})
                assert published.status_code == 200
                assert (await client.get(detail_url, headers=student_headers)).json() == published.json()
                page = (await client.get(challenges_url+f"?skill={sid}", headers=student_headers)).json()
                assert page["total"] == 1 and page["items"] == [published.json()]
                assert (await client.patch(f"/api/v1/skills/{sid}", headers=admin_headers,
                                          json={"is_active": False})).status_code == 200
                assert (await client.get(detail_url, headers=student_headers)).status_code == 404
                assert (await client.get(challenges_url, headers=student_headers)).json()["total"] == 0
                assert (await client.get(detail_url, headers=admin_headers)).json()["is_active"] is True
                assert (await client.patch(f"/api/v1/skills/{sid}", headers=admin_headers,
                                          json={"is_active": True})).status_code == 200
                assert (await client.get(detail_url, headers=student_headers)).json() == published.json()
                assert (await client.get(f"{assessment_url}/{aid}", headers=student_headers)).json() == finished.json()
                assert (await client.get(url, headers=student_headers)).json() == student_before
                assert (await client.get(f"/api/v1/skills/{sid}", headers=student_headers)).json() == skill.json()
                start_url = detail_url + "/attempts"
                started = await client.post(start_url, headers=student_headers)
                assert started.status_code == 201
                attempt_url = f"/api/v1/attempts/{started.json()['id']}"
                assert (await client.get(attempt_url, headers=admin_headers)).status_code == 404
                saved = await client.patch(attempt_url, headers=student_headers,
                                           json={"draft_answer": "  integration answer\n"})
                assert saved.status_code == 200
                resumed = await client.post(start_url, headers=student_headers)
                assert resumed.status_code == 200 and resumed.json() == saved.json()
                assert (await client.patch(detail_url, headers=admin_headers,
                                          json={"title": "Revised content", "is_active": False})).status_code == 200
                assert (await client.post(start_url, headers=student_headers)).json() == saved.json()
                submitted = await client.post(attempt_url + "/submit", headers=student_headers)
                assert submitted.status_code == 200 and submitted.json()["status"] == "SUBMITTED"
                assert submitted.json()["challenge_snapshot"] == started.json()["challenge_snapshot"]
                assert (await client.post(attempt_url + "/submit", headers=student_headers)).json() == submitted.json()
                assert (await client.post(start_url, headers=student_headers)).status_code == 404
                assert (await client.patch(detail_url, headers=admin_headers, json={"is_active": True})).status_code == 200
                next_attempt = await client.post(start_url, headers=student_headers)
                assert next_attempt.status_code == 201 and next_attempt.json()["attempt_number"] == 2
                assert next_attempt.json()["challenge_snapshot"]["title"] == "Revised content"
                assert (await client.get(attempt_url, headers=student_headers)).json() == submitted.json()
                assert (await client.get(f"{assessment_url}/{aid}", headers=student_headers)).json() == finished.json()
                assert (await client.get(url, headers=student_headers)).json() == student_before
                assert (await client.get(f"/api/v1/skills/{sid}", headers=student_headers)).json() == skill.json()
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_jwt_settings, None)
