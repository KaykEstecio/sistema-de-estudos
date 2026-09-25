"""Constraints e reversão do catálogo em PostgreSQL descartável."""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from app.modules.challenges.models import Challenge, ChallengeSkill
from app.modules.assessments.models import Assessment
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.users.models import User, DeclaredExperience
from app.modules.onboarding.models import UserInterest, UserGoal


def test_challenge_migration(migrated_database):
    engine, alembic = migrated_database
    with Session(engine) as session:
        user = User(name="Test", email="challenge@example.com", password_hash="fixture",
                    declared_experience=DeclaredExperience.BASIC, onboarding_completed=True)
        category = Category(name="Logic", slug="logic")
        session.add_all([user, category])
        session.flush()
        skill = Skill(name="Logic", slug="logic", category_id=category.id)
        assessment = Assessment(user_id=user.id)
        session.add_all([skill, assessment, UserInterest(user_id=user.id, category_id=category.id),
                         UserGoal(user_id=user.id, goal_type="Learn")])
        challenge = Challenge(title="Fixture", description="Synthetic fixture", challenge_type="CODE",
                              difficulty="VERY_EASY", difficulty_score=0, estimated_minutes=1,
                              starter_code="  code\n")
        session.add(challenge)
        session.flush()
        session.add(ChallengeSkill(challenge_id=challenge.id, skill_id=skill.id, weight=100))
        session.commit()
        uid, sid, aid, cid = user.id, skill.id, assessment.id, challenge.id
        assert not challenge.is_active
        assert challenge.created_at.tzinfo is not None and challenge.updated_at.tzinfo is not None
        assert challenge.starter_code == "  code\n"
        previous = challenge.updated_at
        challenge.difficulty_score = 1000
        challenge.estimated_minutes = 1440
        challenge.starter_code = None
        session.commit()
        assert challenge.updated_at >= previous
        assert challenge.difficulty_score == 1000 and challenge.starter_code is None

    cases = [
        ("UPDATE challenges SET difficulty_score=-1", "ck_challenges_score"),
        ("UPDATE challenges SET difficulty_score=1001", "ck_challenges_score"),
        ("UPDATE challenges SET estimated_minutes=0", "ck_challenges_minutes"),
        ("UPDATE challenges SET estimated_minutes=1441", "ck_challenges_minutes"),
        ("UPDATE challenges SET challenge_type='UNKNOWN'", "ck_challenges_type"),
        ("UPDATE challenges SET difficulty='UNKNOWN'", "ck_challenges_difficulty"),
        ("UPDATE challenges SET title='   '", "ck_challenges_title"),
        ("UPDATE challenges SET description=''", "ck_challenges_description"),
        ("UPDATE challenge_skills SET weight=0", "ck_challenge_skills_weight"),
        ("UPDATE challenge_skills SET weight=101", "ck_challenge_skills_weight"),
        ("UPDATE challenge_skills SET skill_id=2147483647", "fk_challenge_skills_skill"),
        ("UPDATE challenge_skills SET challenge_id=2147483647", "fk_challenge_skills_challenge"),
        ("INSERT INTO challenge_skills VALUES(:cid,:sid,100)", "challenge_skills_pkey"),
        ("DELETE FROM challenges WHERE id=:cid", "fk_challenge_skills_challenge"),
        ("DELETE FROM skills WHERE id=:sid", "fk_challenge_skills_skill"),
    ]
    for statement, constraint in cases:
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(statement), {"cid": cid, "sid": sid})
        assert error.value.orig.diag.constraint_name == constraint

    for column, maximum in (("title", 200), ("description", 20000), ("starter_code", 20000)):
        with engine.begin() as connection:
            connection.execute(text(f"UPDATE challenges SET {column}=:value"), {"value": "x" * maximum})
        with pytest.raises(DataError):
            with engine.begin() as connection:
                connection.execute(text(f"UPDATE challenges SET {column}=:value"), {"value": "x" * (maximum + 1)})
    with engine.begin() as connection:
        connection.execute(text("UPDATE challenge_skills SET weight=1"))
        # Soma do conjunto será validada pelo service; o banco valida cada linha.
        assert connection.scalar(text("SELECT weight FROM challenge_skills")) == 1
    alembic("check")
    engine.dispose()
    alembic("downgrade", "0004_create_assessments")
    assert not {"challenges", "challenge_skills"} & set(inspect(engine).get_table_names())
    with Session(engine) as session:
        assert session.get(User, uid).onboarding_completed
        assert session.get(Skill, sid) is not None
        assert session.get(Assessment, aid).user_id == uid
        assert session.query(UserGoal).filter_by(user_id=uid).count() == 1
        assert session.query(UserInterest).filter_by(user_id=uid).count() == 1
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
    assert {"challenges", "challenge_skills"} <= set(inspect(engine).get_table_names())
