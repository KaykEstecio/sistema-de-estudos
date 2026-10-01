"""Constraints e reversão preservam tentativas em PostgreSQL isolado."""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from app.modules.attempts.models import ChallengeAttempt
from app.modules.challenges.models import Challenge
from app.modules.users.models import User, UserRole
from app.modules.evaluation.models import AttemptEvaluation, AttemptEvaluationSkill


def test_evaluation_migration(migrated_database):
    engine, alembic = migrated_database
    # Recriar a base anterior para provar preservação durante upgrade.
    alembic("downgrade", "0006_create_attempts")
    with Session(engine) as session:
        owner = User(name="Owner", email="owner@example.com", password_hash="fixture")
        reviewer = User(name="Reviewer", email="reviewer@example.com", password_hash="fixture", role=UserRole.ADMIN)
        challenge = Challenge(title="Fixture", description="Synthetic", challenge_type="CODE", difficulty="EASY", difficulty_score=100, estimated_minutes=10)
        session.add_all([owner, reviewer, challenge]); session.flush()
        attempt = ChallengeAttempt(user_id=owner.id, challenge_id=challenge.id, attempt_number=1, draft_answer="Original answer", challenge_snapshot={"skills": [{"skill_id": 123, "weight": 100}]})
        session.add(attempt); session.commit()
        aid, rid = attempt.id, reviewer.id
    with engine.begin() as connection:
        connection.execute(text("UPDATE challenge_attempts SET status='SUBMITTED', submitted_at=now(), last_activity_at=now()"))
    alembic("upgrade", "head")
    with Session(engine) as session:
        evaluation = AttemptEvaluation(attempt_id=aid, reviewer_id=rid, feedback="Partial solution")
        session.add(evaluation); session.flush()
        eid = evaluation.id
        session.add(AttemptEvaluationSkill(evaluation_id=eid, skill_id=123, classification="PARTIALLY_MET", justification="Missing condition"))
        session.commit()
        assert evaluation.rubric_version == "manual-v1"
        assert evaluation.created_at.tzinfo is not None
        assert session.get(ChallengeAttempt, aid).draft_answer == "Original answer"
    cases = [
        ("UPDATE attempt_evaluations SET rubric_version='unknown'", "ck_evaluations_rubric"),
        ("UPDATE attempt_evaluations SET feedback=E' \\t\\n'", "ck_evaluations_feedback"),
        ("UPDATE attempt_evaluation_skills SET justification=E'\\t'", "ck_evaluation_skills_justification"),
        ("UPDATE attempt_evaluation_skills SET classification='UNKNOWN'", "ck_evaluation_skills_classification"),
        ("UPDATE attempt_evaluation_skills SET skill_id=0", "ck_evaluation_skills_id"),
        ("UPDATE attempt_evaluations SET reviewer_id=2147483647", "fk_evaluations_reviewer"),
        ("UPDATE attempt_evaluations SET attempt_id=2147483647", "fk_evaluations_attempt"),
        ("UPDATE attempt_evaluation_skills SET evaluation_id=2147483647", "fk_evaluation_skills_evaluation"),
        ("INSERT INTO attempt_evaluations(attempt_id,reviewer_id,feedback) VALUES(:aid,:rid,'Duplicate')", "uq_evaluations_attempt"),
        ("INSERT INTO attempt_evaluation_skills VALUES(:eid,123,'MET','Duplicate')", "attempt_evaluation_skills_pkey"),
        ("DELETE FROM challenge_attempts WHERE id=:aid", "fk_evaluations_attempt"),
        ("DELETE FROM users WHERE id=:rid", "fk_evaluations_reviewer"),
        ("DELETE FROM attempt_evaluations WHERE id=:eid", "fk_evaluation_skills_evaluation"),
    ]
    for statement, constraint in cases:
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(statement), dict(aid=aid, rid=rid, eid=eid))
        assert error.value.orig.diag.constraint_name == constraint
    for table, column, maximum in (("attempt_evaluations", "feedback", 4000), ("attempt_evaluation_skills", "justification", 2000)):
        with engine.begin() as connection:
            connection.execute(text(f"UPDATE {table} SET {column}=:value"), {"value": "x" * maximum})
        with pytest.raises(DataError):
            with engine.begin() as connection:
                connection.execute(text(f"UPDATE {table} SET {column}=:value"), {"value": "x" * (maximum + 1)})
    for classification in ("NOT_MET", "PARTIALLY_MET", "MET", "INSUFFICIENT_EVIDENCE"):
        with engine.begin() as connection:
            connection.execute(text("UPDATE attempt_evaluation_skills SET classification=:value"), {"value": classification})
    alembic("check")
    engine.dispose()
    alembic("downgrade", "0006_create_attempts")
    assert "attempt_evaluations" not in inspect(engine).get_table_names()
    assert "attempt_evaluation_skills" not in inspect(engine).get_table_names()
    with Session(engine) as session:
        assert session.get(ChallengeAttempt, aid).draft_answer == "Original answer"
        assert session.get(ChallengeAttempt, aid).status == "SUBMITTED"
        assert session.get(User, rid) is not None
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
