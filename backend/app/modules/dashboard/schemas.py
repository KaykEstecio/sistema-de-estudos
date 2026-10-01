"""Resumo do dono, sem indicadores globais de domínio."""

from pydantic import BaseModel, ConfigDict, Field
from app.modules.skills.progress_schemas import UserSkillRead


class DashboardQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class DashboardGoal(BaseModel):
    goal_type: str
    description: str | None


class DashboardInterest(BaseModel):
    category_id: int
    name: str


class DashboardProfile(BaseModel):
    name: str
    onboarding_completed: bool
    primary_goal: DashboardGoal | None
    interests: list[DashboardInterest]


class DashboardSummary(BaseModel):
    tracked_skills: int = Field(ge=0)
    submitted_attempts: int = Field(ge=0)
    pending_reviews: int = Field(ge=0)


class DashboardSkill(UserSkillRead):
    name: str
    is_active: bool


class DashboardProgress(BaseModel):
    items: list[DashboardSkill]
    total: int
    limit: int
    offset: int


class DashboardRead(BaseModel):
    profile: DashboardProfile
    summary: DashboardSummary
    progress: DashboardProgress
