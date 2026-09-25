"""Persistência do perfil; transação e regras de conclusão pertencem ao service."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.modules.categories.models import Category
from app.modules.onboarding.models import UserInterest, UserGoal
from app.modules.onboarding.schemas import PrimaryGoal
from app.modules.users.models import User


class OnboardingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_locked(self, user_id: int, *, read: bool = False) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id)
            .with_for_update(read=read).execution_options(populate_existing=True))

    def existing_category_ids(self, category_ids: list[int]) -> set[int]:
        return set(self.session.scalars(select(Category.id).where(Category.id.in_(category_ids))))

    def get_interest_ids(self, user_id: int) -> list[int]:
        return list(self.session.scalars(select(UserInterest.category_id)
            .where(UserInterest.user_id == user_id).order_by(UserInterest.category_id)))

    def replace_interests(self, user_id: int, category_ids: list[int]) -> None:
        self.session.execute(delete(UserInterest).where(UserInterest.user_id == user_id))
        self.session.add_all([UserInterest(user_id=user_id, category_id=category_id, priority=1)
                             for category_id in category_ids])
        self.session.flush()

    def get_primary_goal(self, user_id: int) -> UserGoal | None:
        return self.session.scalar(select(UserGoal).where(UserGoal.user_id == user_id, UserGoal.is_primary.is_(True)))

    def set_primary_goal(self, user_id: int, data: PrimaryGoal) -> UserGoal:
        goal = self.get_primary_goal(user_id)
        if goal is None:
            goal = UserGoal(user_id=user_id, goal_type=data.goal_type, description=data.description, is_primary=True)
            self.session.add(goal)
        else:
            goal.goal_type = data.goal_type
            goal.description = data.description
        self.session.flush()
        return goal
