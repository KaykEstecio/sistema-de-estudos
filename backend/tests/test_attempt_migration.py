"""Histórico, constraints e reversão de tentativas em banco descartável."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from app.modules.attempts.models import ChallengeAttempt
from app.modules.challenges.models import Challenge
from app.modules.users.models import User


def test_attempt_migration(migrated_database):
    engine, alembic = migrated_database
    with Session(engine) as session:
        user = User(name="Fixture", email="attempt@example.com", password_hash="unused")
        challenge = Challenge(title="Original", description="Fixture", challenge_type="CODE",
                              difficulty="EASY", difficulty_score=100, estimated_minutes=10)
        session.add_all([user, challenge])
        session.flush()
        snapshot = dict(title=challenge.title, description=challenge.description, challenge_type="CODE",
                        difficulty="EASY", difficulty_score=100, estimated_minutes=10, starter_code=None,
                        skills=[dict(skill_id=1, weight=100)])
        attempt = ChallengeAttempt(user_id=user.id, challenge_id=challenge.id, attempt_number=1,
                                   challenge_snapshot=snapshot)
        session.add(attempt)
        session.commit()
        uid, cid, aid = user.id, challenge.id, attempt.id
        assert attempt.status == "IN_PROGRESS" and attempt.draft_answer == ""
        assert attempt.submitted_at is None
        assert attempt.started_at.tzinfo is not None and attempt.started_at == attempt.last_activity_at
        challenge.title = "Changed"
        session.commit()
        assert attempt.challenge_snapshot["title"] == "Original"
    cases = [
        ("UPDATE challenge_attempts SET attempt_number=0", "ck_attempts_number"),
        ("UPDATE challenge_attempts SET status='SUBMITTED'", "ck_attempts_submission"),
        ("UPDATE challenge_attempts SET submitted_at=now()", "ck_attempts_submission"),
        ("UPDATE challenge_attempts SET challenge_snapshot='[]'::jsonb", "ck_attempts_snapshot"),
        ("UPDATE challenge_attempts SET challenge_snapshot='null'::jsonb", "ck_attempts_snapshot"),
        ("UPDATE challenge_attempts SET last_activity_at=started_at-interval '1 second'", "ck_attempts_dates"),
        ("UPDATE challenge_attempts SET user_id=2147483647", "fk_attempts_user"),
        ("UPDATE challenge_attempts SET challenge_id=2147483647", "fk_attempts_challenge"),
        ("DELETE FROM users WHERE id=:uid", "fk_attempts_user"),
        ("DELETE FROM challenges WHERE id=:cid", "fk_attempts_challenge"),
        ("INSERT INTO challenge_attempts(user_id,challenge_id,attempt_number,challenge_snapshot) VALUES(:uid,:cid,2,'{}')", "uq_attempts_open"),
    ]
    for statement, constraint in cases:
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(statement), dict(uid=uid, cid=cid))
        assert error.value.orig.diag.constraint_name == constraint
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text("UPDATE challenge_attempts SET status='OTHER'"))
    with engine.begin() as connection:
        connection.execute(text("UPDATE challenge_attempts SET draft_answer=:answer"), {"answer": "x" * 20000})
    with pytest.raises(DataError):
        with engine.begin() as connection:
            connection.execute(text("UPDATE challenge_attempts SET draft_answer=:answer"), {"answer": "x" * 20001})
    with Session(engine) as session:
        first = session.get(ChallengeAttempt, aid)
        first.status = "SUBMITTED"
        first.submitted_at = first.last_activity_at = datetime.now(timezone.utc)
        session.commit()
        session.add(ChallengeAttempt(user_id=uid, challenge_id=cid, attempt_number=2, challenge_snapshot=snapshot))
        session.commit()
        assert session.get(ChallengeAttempt, aid).draft_answer == "x" * 20000
    with pytest.raises(IntegrityError) as error:
        with engine.begin() as connection:
            connection.execute(text("UPDATE challenge_attempts SET attempt_number=1 WHERE attempt_number=2"))
    assert error.value.orig.diag.constraint_name == "uq_attempts_number"
    alembic("check")
    engine.dispose()
    alembic("downgrade", "0005_create_challenges")
    assert "challenge_attempts" not in inspect(engine).get_table_names()
    with Session(engine) as session:
        assert session.get(User, uid).email == "attempt@example.com"
        assert session.get(Challenge, cid).title == "Changed"
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
