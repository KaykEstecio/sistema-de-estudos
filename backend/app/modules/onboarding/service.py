"""Conclusão e edição atômica do perfil declarado."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.schemas import OnboardingCreate, OnboardingUpdate, OnboardingRead, PrimaryGoal
from app.modules.users.models import User
from app.modules.users.auth_service import InvalidCredentials


class OnboardingAlreadyCompleted(Exception):
    pass


class OnboardingNotCompleted(Exception):
    pass


class InterestCategoryNotFound(Exception):
    pass


class OnboardingService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = OnboardingRepository(session)

    def _read(self, user: User) -> OnboardingRead:
        if not user.onboarding_completed:
            return OnboardingRead(onboarding_completed=False, declared_experience=None,
                                  interest_category_ids=[], primary_goal=None)
        goal = self.repository.get_primary_goal(user.id)
        return OnboardingRead(onboarding_completed=True, declared_experience=user.declared_experience,
            interest_category_ids=self.repository.get_interest_ids(user.id),
            primary_goal=PrimaryGoal(goal_type=goal.goal_type, description=goal.description) if goal else None)

    def get(self, user_id: int) -> OnboardingRead:
        user = self.repository.get_user_locked(user_id, read=True)
        if user is None:
            raise InvalidCredentials()
        return self._read(user)

    def create(self, user_id: int, data: OnboardingCreate) -> OnboardingRead:
        return self._write(user_id, data)

    def update(self, user_id: int, data: OnboardingUpdate) -> OnboardingRead:
        return self._write(user_id, data)

    def _write(self, user_id: int, data: OnboardingCreate | OnboardingUpdate) -> OnboardingRead:
        try:
            user = self.repository.get_user_locked(user_id)
            if user is None:
                raise InvalidCredentials()
            if isinstance(data, OnboardingCreate) and user.onboarding_completed:
                raise OnboardingAlreadyCompleted()
            if isinstance(data, OnboardingUpdate) and not user.onboarding_completed:
                raise OnboardingNotCompleted()
            if data.interest_category_ids is not None:
                ids = data.interest_category_ids
                if self.repository.existing_category_ids(ids) != set(ids):
                    raise InterestCategoryNotFound()
                self.repository.replace_interests(user.id, ids)
            if data.primary_goal is not None:
                self.repository.set_primary_goal(user.id, data.primary_goal)
            if data.declared_experience is not None:
                user.declared_experience = data.declared_experience
            user.onboarding_completed = True
            self.session.flush()
            result = self._read(user)
            self.session.commit()
            return result
        except IntegrityError as exc:
            self.session.rollback()
            if (getattr(exc.orig, "sqlstate", None) == "23503" and
                getattr(getattr(exc.orig, "diag", None), "constraint_name", None) == "fk_user_interests_category"):
                raise InterestCategoryNotFound() from None
            raise
        except Exception:
            self.session.rollback()
            raise
