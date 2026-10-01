"""Estado auditável; Decimal é serializado como string no JSON."""

from decimal import Decimal
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class ProgressQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class UserSkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    score: int
    confidence: Decimal
    attempts: int
    successful_attempts: int
    last_practiced_at: AwareDatetime
    updated_at: AwareDatetime


class UserSkillPage(BaseModel):
    items: list[UserSkillRead]
    total: int
    limit: int
    offset: int


class ProgressState(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    score: int = Field(ge=0, le=1000)
    confidence: Decimal = Field(ge=0, le=Decimal("0.95"), allow_inf_nan=False)
    attempts: int = Field(ge=0)
    successful_attempts: int = Field(ge=0)
    mass: Decimal = Field(ge=0, allow_inf_nan=False)
    residual_sum: Decimal = Field(allow_inf_nan=False)
    squared_residual_sum: Decimal = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def consistent(self) -> "ProgressState":
        if self.successful_attempts > self.attempts or abs(self.residual_sum) > self.mass or self.squared_residual_sum > self.mass:
            raise ValueError("Estado de evidência inconsistente.")
        return self
