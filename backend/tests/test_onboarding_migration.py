"""Integridade do perfil e migração de estado em banco descartável."""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.onboarding.models import UserInterest, UserGoal
from app.modules.users.models import User, DeclaredExperience
from app.modules.categories.models import Category


def test_onboarding_migration(migrated_database):
    engine, alembic = migrated_database
    engine.dispose()
    alembic("downgrade", "0002_create_catalog")
    with engine.begin() as connection:
        uid = connection.execute(text("INSERT INTO users (name,email,password_hash,onboarding_completed) VALUES ('Ana','ana@example.com','test',true) RETURNING id")).scalar_one()
        cid = connection.execute(text("INSERT INTO categories (name,slug) VALUES ('Logic','logic') RETURNING id")).scalar_one()
    engine.dispose()
    alembic("upgrade", "head")
    with Session(engine) as session:
        user = session.get(User, uid)
        assert user.declared_experience is None and not user.onboarding_completed
        interest = UserInterest(user_id=uid, category_id=cid)
        goal = UserGoal(user_id=uid, goal_type="Learn")
        session.add_all([interest, goal])
        user.declared_experience = DeclaredExperience.BEGINNER
        user.onboarding_completed = True
        session.commit()
        assert interest.priority == 1 and goal.is_primary
        assert goal.description is None and goal.created_at.tzinfo is not None

    cases = [
        ("UPDATE users SET declared_experience=NULL WHERE id=:uid", "ck_users_onboarding_experience"),
        ("UPDATE users SET declared_experience='EXPERT' WHERE id=:uid", "ck_users_declared_experience"),
        ("INSERT INTO user_interests(user_id,category_id) VALUES(:uid,:cid)", "uq_user_interests_user_category"),
        ("UPDATE user_interests SET priority=0 WHERE user_id=:uid", "ck_user_interests_priority"),
        ("INSERT INTO user_goals(user_id,goal_type) VALUES(:uid,'Duplicate')", "uq_user_goals_primary"),
        ("INSERT INTO user_goals(user_id,goal_type) VALUES(2147483647,'Orphan')", "fk_user_goals_user"),
        ("INSERT INTO user_interests(user_id,category_id) VALUES(:uid,2147483647)", "fk_user_interests_category"),
        ("INSERT INTO user_interests(user_id,category_id) VALUES(2147483647,:cid)", "fk_user_interests_user"),
        ("DELETE FROM categories WHERE id=:cid", "fk_user_interests_category"),
    ]
    for sql, constraint in cases:
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(sql), {"uid": uid, "cid": cid})
        assert error.value.orig.diag.constraint_name == constraint
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM users WHERE id=:uid"), {"uid": uid})
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO user_goals(user_id,goal_type,is_primary) VALUES(:uid,'Secondary',false)"), {"uid": uid})
    alembic("check")
    engine.dispose()
    alembic("downgrade", "0002_create_catalog")
    assert "user_goals" not in inspect(engine).get_table_names()
    assert "user_interests" not in inspect(engine).get_table_names()
    assert "declared_experience" not in {column["name"] for column in inspect(engine).get_columns("users")}
    with engine.connect() as connection:
        assert connection.execute(text("SELECT onboarding_completed FROM users WHERE id=:uid"), {"uid": uid}).scalar_one() is False
        assert connection.execute(text("SELECT id FROM categories WHERE id=:cid"), {"cid": cid}).scalar_one() == cid
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
