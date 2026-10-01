"""Uma instrução de leitura, com contagens independentes da página."""

from sqlalchemy import RowMapping, and_, func, select, true
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.categories.models import Category
from app.modules.onboarding.models import UserGoal, UserInterest
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill
from app.modules.attempts.models import ChallengeAttempt
from app.modules.evaluation.models import AttemptEvaluation


class DashboardRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load(self, user_id: int, *, limit: int, offset: int) -> list[RowMapping]:
        progress_total = select(func.count()).select_from(UserSkill).where(
            UserSkill.user_id == user_id).scalar_subquery()
        reviewed = select(AttemptEvaluation.id).where(
            AttemptEvaluation.attempt_id == ChallengeAttempt.id).exists()
        attempts = select(func.count().label("submitted_attempts"),
            func.count().filter(~reviewed).label("pending_reviews")).select_from(ChallengeAttempt).where(
            ChallengeAttempt.user_id == user_id, ChallengeAttempt.status == "SUBMITTED").cte("attempt_counts")
        interests = select(func.json_agg(aggregate_order_by(
            func.json_build_object("category_id", Category.id, "name", Category.name), Category.id))
        ).select_from(UserInterest).join(Category, Category.id == UserInterest.category_id).where(
            UserInterest.user_id == user_id).scalar_subquery()
        page = select(UserSkill.skill_id, Skill.name, Skill.is_active, UserSkill.score,
            UserSkill.confidence, UserSkill.attempts, UserSkill.successful_attempts,
            UserSkill.last_practiced_at, UserSkill.updated_at).join(Skill, Skill.id == UserSkill.skill_id).where(
            UserSkill.user_id == user_id).order_by(UserSkill.last_practiced_at.desc(), UserSkill.skill_id)
        page = page.limit(limit).offset(offset).cte("progress_page")
        statement = select(User.name.label("user_name"), User.onboarding_completed,
            UserGoal.goal_type, UserGoal.description, interests.label("interests"),
            progress_total.label("tracked_skills"), attempts.c.submitted_attempts,
            attempts.c.pending_reviews, *page.c).select_from(User).join(attempts, true()).outerjoin(
            UserGoal, and_(UserGoal.user_id == User.id, UserGoal.is_primary.is_(True))).outerjoin(
            page, true()).where(User.id == user_id).order_by(page.c.last_practiced_at.desc(), page.c.skill_id)
        return list(self.session.execute(statement).mappings())
