"""Entrada e saída do perfil declarado, sem ownership fornecido pelo cliente."""

from typing import Annotated, Self
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, model_validator
from app.modules.categories.schemas import CatalogId, Name, Description
from app.modules.users.models import DeclaredExperience


def distinct_interests(values: list[int]) -> list[int]:
    if len(values) != len(set(values)):
        raise ValueError("Interesses não podem se repetir.")
    return values


Interests = Annotated[list[CatalogId], Field(min_length=1, max_length=20), AfterValidator(distinct_interests)]


class PrimaryGoal(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    goal_type: Name
    description: Description = None


class OnboardingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    declared_experience: DeclaredExperience
    interest_category_ids: Interests
    primary_goal: PrimaryGoal


class OnboardingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    declared_experience: DeclaredExperience | None = None
    interest_category_ids: Interests | None = None
    primary_goal: PrimaryGoal | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo editável.")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Campos do onboarding não aceitam null.")
        return self


class OnboardingRead(BaseModel):
    onboarding_completed: bool
    declared_experience: DeclaredExperience | None
    interest_category_ids: list[int]
    primary_goal: PrimaryGoal | None
