"""Persistência por usuário, locks e rollback em PostgreSQL isolado."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from app.modules.categories.models import Category
from app.modules.users.models import User, DeclaredExperience
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.schemas import PrimaryGoal


def test_onboarding_repository(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        users = [User(name="User", email=f"user{i}@example.com", password_hash="test") for i in range(2)]
        categories = [Category(name="Category", slug=f"category-{i}") for i in range(2)]
        session.add_all(users + categories)
        session.commit()
        uid, other_id = [user.id for user in users]
        first, second = [category.id for category in categories]
    with Session(engine) as session:
        repository = OnboardingRepository(session)
        assert repository.get_user_locked(2147483647) is None
        user = repository.get_user_locked(uid)
        assert repository.existing_category_ids([first, 2147483647]) == {first}
        assert repository.get_interest_ids(uid) == [] and repository.get_primary_goal(uid) is None
        repository.replace_interests(uid, [second, first])
        goal = repository.set_primary_goal(uid, PrimaryGoal(goal_type="Learn", description="Text"))
        goal_id, created_at = goal.id, goal.created_at
        user.declared_experience = DeclaredExperience.BASIC
        user.onboarding_completed = True
        session.commit()
        assert repository.get_interest_ids(uid) == [first, second]
        assert repository.get_interest_ids(other_id) == [] and repository.get_primary_goal(other_id) is None
        repository.replace_interests(uid, [second])
        goal = repository.set_primary_goal(uid, PrimaryGoal(goal_type="Other"))
        assert goal.id == goal_id and goal.created_at == created_at and goal.description is None
        session.rollback()
        assert repository.get_interest_ids(uid) == [first, second]
        assert repository.get_primary_goal(uid).goal_type == "Learn"
        with pytest.raises(IntegrityError):
            repository.replace_interests(uid, [2147483647])
        session.rollback()
        assert repository.get_interest_ids(uid) == [first, second]
        repository.replace_interests(other_id, [first])
        repository.set_primary_goal(other_id, PrimaryGoal(goal_type="Independent"))
        session.rollback()
        assert repository.get_primary_goal(other_id) is None
    # A sessão já carregou User antes de outra transação alterar o registro.
    with Session(engine) as reader:
        cached = reader.get(User, uid)
        with Session(engine) as writer:
            writer.get(User, uid).declared_experience = DeclaredExperience.ADVANCED
            writer.commit()
        refreshed = OnboardingRepository(reader).get_user_locked(uid, read=True)
        assert refreshed is cached and refreshed.declared_experience == DeclaredExperience.ADVANCED
        # Lock compartilhado impede escrita concorrente até encerrar a leitura.
        with Session(engine) as blocked:
            blocked.execute(text("SET LOCAL lock_timeout = '100ms'"))
            with pytest.raises(OperationalError) as error:
                OnboardingRepository(blocked).get_user_locked(uid)
            assert error.value.orig.sqlstate == "55P03"
            blocked.rollback()
        reader.rollback()
    with Session(engine) as session:
        assert OnboardingRepository(session).get_user_locked(uid) is not None
