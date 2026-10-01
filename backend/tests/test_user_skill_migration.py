"""Precisão, unicidade e histórico em PostgreSQL descartável."""

from datetime import datetime, timezone
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.challenges.models import Challenge
from app.modules.attempts.models import ChallengeAttempt
from app.modules.assessments.models import AssessmentResult  # Registers the referenced table.
from app.modules.evaluation.models import AttemptEvaluation, AttemptEvaluationSkill
from app.modules.skills.progress_models import UserSkill, SkillEvidence
from app.modules.skills.policy import calculate_change, EvidenceTotals


def test_user_skill_storage(migrated_database):
    engine, alembic = migrated_database
    alembic("downgrade", "0007_create_evaluations")
    with Session(engine) as session:
        user = User(name="Fixture", email="progress@example.com", password_hash="unused")
        category = Category(name="Fixture", slug="fixture")
        challenge = Challenge(title="Fixture", description="Fixture", challenge_type="CODE", difficulty="EASY", difficulty_score=100, estimated_minutes=10)
        session.add_all([user, category, challenge]); session.flush()
        skill = Skill(name="Fixture", slug="fixture", category_id=category.id)
        session.add(skill); session.flush()
        attempt = ChallengeAttempt(user_id=user.id, challenge_id=challenge.id, attempt_number=1, challenge_snapshot={"skills": [{"skill_id": skill.id, "weight": 100}]})
        session.add(attempt); session.flush()
        evaluation = AttemptEvaluation(attempt_id=attempt.id, reviewer_id=user.id, feedback="Historical fixture; authorization is service responsibility")
        session.add(evaluation); session.flush()
        session.add(AttemptEvaluationSkill(evaluation_id=evaluation.id, skill_id=skill.id, classification="MET", justification="Fixture"))
        session.commit(); uid, sid, eid = user.id, skill.id, evaluation.id
    alembic("upgrade", "head")
    with Session(engine) as session:
        assert session.query(UserSkill).count() == session.query(SkillEvidence).count() == 0
        result = calculate_change(500,500,100,3,"MET")
        progress = UserSkill(user_id=uid, skill_id=sid, score=result.score, confidence=result.confidence, attempts=1, successful_attempts=1, initial_score=500, mass=result.totals.mass, residual_sum=result.totals.residual_sum, squared_residual_sum=result.totals.squared_residual_sum, last_practiced_at=datetime.now(timezone.utc))
        session.add(progress)
        session.add(SkillEvidence(user_id=uid, skill_id=sid, evaluation_id=eid, policy_version="manual-skill-v1", applied=False))
        session.commit(); session.expire_all()
        saved = session.get(UserSkill, progress.id)
        totals = EvidenceTotals(saved.mass, saved.residual_sum, saved.squared_residual_sum)
        assert totals == result.totals
        assert calculate_change(result.score,700,37,7,"PARTIALLY_MET",totals) == calculate_change(result.score,700,37,7,"PARTIALLY_MET",result.totals)
        assert saved.confidence == result.confidence and saved.updated_at.tzinfo is not None
    cases = [
        ("UPDATE user_skills SET score=1001", "ck_user_skills_scores"),
        ("UPDATE user_skills SET confidence=0.950001", "ck_user_skills_confidence"),
        ("UPDATE user_skills SET confidence='NaN'", "ck_user_skills_confidence"),
        ("UPDATE user_skills SET attempts=0", "ck_user_skills_counts"),
        ("UPDATE user_skills SET successful_attempts=2", "ck_user_skills_counts"),
        ("UPDATE user_skills SET initial_score=400", "ck_user_skills_initial"),
        ("UPDATE user_skills SET initial_assessment_id=2147483647", "fk_user_skills_initial_result"),
        ("UPDATE user_skills SET mass='NaN'", "ck_user_skills_totals"),
        ("UPDATE user_skills SET mass='Infinity'", "ck_user_skills_totals"),
        ("UPDATE user_skills SET residual_sum='-Infinity'", "ck_user_skills_totals"),
        ("UPDATE user_skills SET squared_residual_sum=-1", "ck_user_skills_totals"),
        ("UPDATE skill_evidence SET applied=true", "ck_skill_evidence_states"),
        ("UPDATE skill_evidence SET before_state='{}'", "ck_skill_evidence_states"),
        ("UPDATE skill_evidence SET policy_version='other'", "ck_skill_evidence_policy"),
        ("UPDATE skill_evidence SET evaluation_id=2147483647", "fk_skill_evidence_result"),
        ("INSERT INTO skill_evidence(user_id,skill_id,evaluation_id,policy_version,applied) VALUES(:uid,:sid,:eid,'manual-skill-v1',false)", "uq_skill_evidence_evaluation_skill"),
        ("DELETE FROM attempt_evaluation_skills WHERE evaluation_id=:eid", "fk_skill_evidence_result"),
        ("INSERT INTO user_skills(user_id,skill_id,score,confidence,attempts,successful_attempts,initial_score,mass,residual_sum,squared_residual_sum,last_practiced_at) SELECT user_id,skill_id,score,confidence,attempts,successful_attempts,initial_score,mass,residual_sum,squared_residual_sum,last_practiced_at FROM user_skills", "uq_user_skills_user_skill"),
    ]
    for sql, constraint in cases:
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as c: c.execute(text(sql), dict(uid=uid,sid=sid,eid=eid))
        assert error.value.orig.diag.constraint_name == constraint
    with engine.begin() as c:
        c.execute(text("UPDATE skill_evidence SET applied=true,before_state='{}',after_state='{}'"))
    with pytest.raises(IntegrityError):
        with engine.begin() as c: c.execute(text("UPDATE skill_evidence SET after_state='null'::jsonb"))
    alembic("check")
    engine.dispose(); alembic("downgrade", "0007_create_evaluations")
    assert not {"user_skills", "skill_evidence"} & set(inspect(engine).get_table_names())
    with Session(engine) as session:
        assert session.get(AttemptEvaluation, eid).feedback.startswith("Historical fixture")
        assert session.get(Skill, sid) is not None
    engine.dispose(); alembic("upgrade", "head"); alembic("check")
