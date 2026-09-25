"""Isolamento por dono, snapshots e rollback em PostgreSQL real."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.modules.attempts.repository import AttemptRepository
from app.modules.attempts.schemas import AttemptRead, ChallengeSnapshot
from app.modules.challenges.models import Challenge
from app.modules.users.models import User


def test_attempt_repository(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        users = [User(name="Test", email=f"attempt{i}@example.com", password_hash="unused") for i in range(2)]
        challenge = Challenge(title="Original", description="Fixture", challenge_type="CODE",
                              difficulty="EASY", difficulty_score=0, estimated_minutes=1)
        session.add_all([*users, challenge])
        session.commit()
        uid, other = [user.id for user in users]
        cid = challenge.id
        repo = AttemptRepository(session)
        assert repo.get_user_locked(uid).id == uid
        assert repo.get_challenge_locked(cid).title == "Original"
        assert repo.last_number(uid, cid) == 0
        snapshot = ChallengeSnapshot(title="Original", description="Fixture", challenge_type="CODE",
            difficulty="EASY", difficulty_score=0, estimated_minutes=1, starter_code=None,
            skills=[dict(skill_id=1, weight=100)])
        now = datetime.now(timezone.utc)
        attempt = repo.create(uid, cid, 1, snapshot, now)
        aid = attempt.id
        session.commit()
        snapshot.title = "Changed input"
        challenge.title = "Changed catalog"
        session.commit()
        assert repo.get_owned(aid, uid).challenge_snapshot["title"] == "Original"
        assert repo.get_owned(aid, other, lock=True) is None
        assert repo.get_open_locked(other, cid) is None
        assert repo.get_open_locked(uid, cid).id == aid
        result = AttemptRead.model_validate(attempt).model_dump()
        assert "user_id" not in result and "password_hash" not in result
        repo.save_draft(attempt, "  answer\n", now + timedelta(seconds=1))
        session.rollback()
        assert repo.get_owned(aid, uid).draft_answer == ""
        repo.save_draft(attempt, "  answer\n", now + timedelta(seconds=1))
        session.commit()
        repo.submit(attempt, now + timedelta(seconds=2))
        session.rollback()
        assert repo.get_owned(aid, uid).status == "IN_PROGRESS"
        repo.submit(attempt, now + timedelta(seconds=2))
        session.commit()
        assert repo.get_open_locked(uid, cid) is None
        assert attempt.draft_answer == "  answer\n" and attempt.submitted_at == attempt.last_activity_at
        second = repo.create(uid, cid, repo.last_number(uid, cid) + 1, snapshot, now + timedelta(seconds=3))
        second_id = second.id
        session.rollback()
        assert repo.get_owned(second_id, uid) is None and repo.last_number(uid, cid) == 1
