"""Compõe o resumo sem recalcular progresso ou recomendações."""

from datetime import timezone
from sqlalchemy.orm import Session
from app.modules.users.auth_service import InvalidCredentials
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import (
    DashboardGoal, DashboardInterest, DashboardProfile, DashboardProgress,
    DashboardQuery, DashboardRead, DashboardSkill, DashboardSummary,
)


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.repository = DashboardRepository(session)

    def get_owned(self, user_id: int, query: DashboardQuery) -> DashboardRead:
        rows = self.repository.load(user_id, limit=query.limit, offset=query.offset)
        if not rows:
            raise InvalidCredentials()
        first = rows[0]
        profile = DashboardProfile(name=first["user_name"], onboarding_completed=first["onboarding_completed"],
            primary_goal=DashboardGoal(goal_type=first["goal_type"], description=first["description"])
            if first["goal_type"] is not None else None,
            interests=[DashboardInterest.model_validate(item) for item in first["interests"] or []])
        summary = DashboardSummary(tracked_skills=first["tracked_skills"],
            submitted_attempts=first["submitted_attempts"], pending_reviews=first["pending_reviews"])
        items = [DashboardSkill(skill_id=row["skill_id"], name=row["name"], is_active=row["is_active"],
            score=row["score"], confidence=row["confidence"], attempts=row["attempts"],
            successful_attempts=row["successful_attempts"],
            last_practiced_at=row["last_practiced_at"].astimezone(timezone.utc),
            updated_at=row["updated_at"].astimezone(timezone.utc)) for row in rows if row["skill_id"] is not None]
        return DashboardRead(profile=profile, summary=summary,
            progress=DashboardProgress(items=items, total=summary.tracked_skills, limit=query.limit, offset=query.offset))
