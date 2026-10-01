"""Revisão autorizada, atômica e idempotente no PostgreSQL real."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session
from app.modules.attempts.models import ChallengeAttempt
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill, SkillEvidence
from app.modules.challenges.models import Challenge
from app.modules.users.models import User, UserRole
from app.modules.users.auth_service import PermissionDenied
from app.modules.evaluation.models import AttemptEvaluation, AttemptEvaluationSkill
from app.modules.evaluation.schemas import EvaluationCreate
from app.modules.evaluation.service import EvaluationService, EvaluationConflict, EvaluationNotFound, EvaluationSkillsMismatch


def test_evaluation_flow(migrated_database, monkeypatch):
    engine, _ = migrated_database
    with Session(engine) as session:
        users = [User(name=f"Fixture {i}", email=f"review{i}@example.com", password_hash="fixture", role=UserRole.STUDENT if i == 0 else UserRole.ADMIN) for i in range(3)]
        challenge = Challenge(title="Original", description="Fixture", challenge_type="CODE", difficulty="EASY", difficulty_score=100, estimated_minutes=10)
        session.add_all([*users, challenge]); session.flush()
        category = Category(name="Fixture", slug="fixture")
        session.add(category); session.flush()
        session.add(Skill(id=123, name="Fixture", slug="fixture", category_id=category.id))
        session.flush()
        owner, admin, other = [user.id for user in users]
        snapshot = dict(title="Original", description="Fixture", challenge_type="CODE", difficulty="EASY", difficulty_score=100, estimated_minutes=10, starter_code=None, skills=[dict(skill_id=123, weight=100)])
        attempt = ChallengeAttempt(user_id=owner, challenge_id=challenge.id, attempt_number=1, challenge_snapshot=snapshot, draft_answer="immutable answer")
        session.add(attempt); session.commit(); aid = attempt.id
        data = EvaluationCreate(feedback="Feedback", skills=[dict(skill_id=123, classification="PARTIALLY_MET", justification="Missing a condition")])
        service = EvaluationService(session)
        with pytest.raises(PermissionDenied): service.evaluate(owner, aid, data)
        with pytest.raises(EvaluationConflict): service.evaluate(admin, aid, data)
        with pytest.raises(EvaluationNotFound): service.get_owned(owner, aid)
        session.execute(text("UPDATE challenge_attempts SET status='SUBMITTED', submitted_at=now(), last_activity_at=now() WHERE id=:id"), {"id": aid})
        challenge.title = "Changed after attempt"
        session.commit()
        assert service.review(admin, aid).attempt.challenge_snapshot.title == "Original"
        with pytest.raises(EvaluationSkillsMismatch):
            service.evaluate(admin, aid, EvaluationCreate(feedback="Feedback", skills=[dict(skill_id=124, classification="MET", justification="Wrong skill")]))
        users[0].role = UserRole.ADMIN; session.commit()
        with pytest.raises(PermissionDenied): service.evaluate(owner, aid, data)
        # Falha depois dos flushes deve desfazer avaliação e todas as evidências.
        original = service.repository.create
        def fail_after_create(*args):
            original(*args)
            raise RuntimeError("Injected persistence failure")
        with monkeypatch.context() as patch:
            patch.setattr(service.repository, "create", fail_after_create)
            with pytest.raises(RuntimeError): service.evaluate(admin, aid, data)
        assert session.scalar(select(func.count()).select_from(AttemptEvaluation)) == 0
        assert session.scalar(select(func.count()).select_from(AttemptEvaluationSkill)) == 0
        session.rollback()
    barrier = Barrier(2)
    def concurrent_review(reviewer):
        with Session(engine) as session:
            barrier.wait(timeout=10)
            try:
                return EvaluationService(session).evaluate(reviewer, aid, data)
            except EvaluationConflict:
                return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(concurrent_review, [admin, other]))
    assert sum(result is not None for result in results) == 1
    winner = admin if results[0] is not None else other
    with Session(engine) as session:
        service = EvaluationService(session)
        result = service.get_owned(owner, aid)
        repeated, created = service.evaluate(winner, aid, data)
        assert not created and repeated == result
        assert "reviewer_id" not in result.model_dump() and "score" not in result.model_dump()
        with pytest.raises(EvaluationNotFound): service.get_owned(winner, aid)
        different = data.model_copy(update={"feedback": "Different"})
        with pytest.raises(EvaluationConflict): service.evaluate(winner, aid, different)
        assert session.scalar(select(func.count()).select_from(AttemptEvaluation)) == 1
        assert session.scalar(select(func.count()).select_from(AttemptEvaluationSkill)) == 1
        progress = session.scalar(select(UserSkill))
        assert progress.initial_score == 500 and progress.initial_assessment_id is None
        assert progress.attempts == 1 and progress.successful_attempts == 0
        assert progress.score == 484
        assert session.scalar(select(func.count()).select_from(SkillEvidence)) == 1
        assert session.get(ChallengeAttempt, aid).draft_answer == "immutable answer"
        assert session.get(ChallengeAttempt, aid).status == "SUBMITTED"
