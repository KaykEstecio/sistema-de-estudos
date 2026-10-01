"""Integração atômica, origem e ordem histórica do progresso."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import pytest
from app.modules.users.models import User, UserRole
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill, SkillEvidence
from app.modules.skills.progress_repository import ProgressRepository
from app.modules.assessments.models import Assessment, AssessmentResult
from app.modules.challenges.models import Challenge
from app.modules.attempts.models import ChallengeAttempt
from app.modules.evaluation.models import AttemptEvaluation
from app.modules.evaluation.repository import EvaluationRepository
from app.modules.evaluation.service import EvaluationService
from app.modules.evaluation.schemas import EvaluationCreate


def test_progress_integration(migrated_database, monkeypatch):
    engine, _ = migrated_database
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        owner = User(name="Owner", email="owner@test.com", password_hash="unused")
        admin = User(name="Admin", email="admin@test.com", password_hash="unused", role=UserRole.ADMIN)
        category = Category(name="Code", slug="code")
        challenge = Challenge(title="Test", description="Test", challenge_type="CODE", difficulty="MEDIUM", difficulty_score=500, estimated_minutes=10)
        session.add_all([owner, admin, category, challenge]); session.flush()
        skill = Skill(name="Python", slug="python", category_id=category.id)
        session.add(skill); session.flush()
        snapshot = dict(title="Test", description="Test", challenge_type="CODE", difficulty="MEDIUM", difficulty_score=500, estimated_minutes=10, starter_code=None, skills=[dict(skill_id=skill.id, weight=100)])
        attempts = []
        for n in range(1, 6):
            attempt = ChallengeAttempt(user_id=owner.id, challenge_id=challenge.id, attempt_number=n,
                challenge_snapshot=snapshot, status="SUBMITTED", draft_answer="answer",
                started_at=now-timedelta(days=10-n), submitted_at=now-timedelta(days=9-n), last_activity_at=now)
            session.add(attempt); attempts.append(attempt)
        # Empate: maior ID elegível; diagnóstico igual ao início é excluído.
        assessments = []
        for score, completed in [(600, now-timedelta(days=20)), (700, now-timedelta(days=20)), (900, now-timedelta(days=7))]:
            assessment = Assessment(user_id=owner.id, started_at=now-timedelta(days=21), completed_at=completed)
            session.add(assessment); session.flush()
            session.add(AssessmentResult(assessment_id=assessment.id, skill_id=skill.id, score=score, confidence=0, correct_count=1, question_count=3))
            assessments.append(assessment)
        session.commit()
        service = EvaluationService(session)
        def data(classification):
            return EvaluationCreate(feedback="Feedback", skills=[dict(skill_id=skill.id, classification=classification, justification="Evidence")])
        met, insufficient = data("MET"), data("INSUFFICIENT_EVIDENCE")
        service.evaluate(admin.id, attempts[0].id, insufficient)
        assert session.scalar(select(func.count()).select_from(UserSkill)) == 0
        # Avaliação anterior ao corte: reenvio não inicializa progresso.
        EvaluationRepository(session).create(attempts[4].id, admin.id, met)
        session.commit()
        assert not service.evaluate(admin.id, attempts[4].id, met)[1]
        assert session.scalar(select(func.count()).select_from(UserSkill)) == 0
        original = ProgressRepository.save
        def fail_after_save(repository, progress, evidence):
            original(repository, progress, evidence)
            raise RuntimeError("Injected after skill flush")
        with monkeypatch.context() as patch:
            patch.setattr(ProgressRepository, "save", fail_after_save)
            with pytest.raises(RuntimeError): service.evaluate(admin.id, attempts[2].id, met)
        assert session.scalar(select(func.count()).select_from(UserSkill)) == 0
        assert session.scalar(select(func.count()).select_from(AttemptEvaluation)) == 2
        result, created = service.evaluate(admin.id, attempts[2].id, met)
        assert created
        progress = session.scalar(select(UserSkill))
        assert progress.initial_score == 700 and progress.initial_assessment_id == assessments[1].id
        assert progress.score == 704 and progress.attempts == progress.successful_attempts == 1
        evidence = session.scalar(select(SkillEvidence).where(SkillEvidence.evaluation_id == result.id))
        assert evidence.before_state["score"] == 700 and evidence.before_state["attempts"] == 0
        assert isinstance(evidence.after_state["mass"], str)
        assert not service.evaluate(admin.id, attempts[2].id, met)[1]
        service.evaluate(admin.id, attempts[1].id, met)
        session.refresh(progress)
        assert progress.attempts == 2 and progress.initial_score == 700
        assert progress.last_practiced_at == attempts[2].submitted_at
        prior = (progress.score, progress.confidence, progress.updated_at, progress.last_practiced_at)
        service.evaluate(admin.id, attempts[3].id, insufficient)
        session.refresh(progress)
        assert (progress.score, progress.confidence, progress.updated_at, progress.last_practiced_at) == prior
        assert session.scalar(select(func.count()).select_from(SkillEvidence)) == 4
