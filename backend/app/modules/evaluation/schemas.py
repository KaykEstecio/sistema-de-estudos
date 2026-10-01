"""Entrada qualitativa sem identidades, notas ou campos de controle."""

from typing import Annotated, Literal
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, field_validator
from app.modules.categories.schemas import CatalogId
from app.modules.attempts.schemas import AttemptRead

Classification = Literal["NOT_MET", "PARTIALLY_MET", "MET", "INSUFFICIENT_EVIDENCE"]
Feedback = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=4000)]
Justification = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=2000)]


class EvaluationSkillInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True, from_attributes=True)
    skill_id: CatalogId
    classification: Classification
    justification: Justification


class EvaluationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    feedback: Feedback
    skills: list[EvaluationSkillInput] = Field(min_length=1, max_length=20)

    @field_validator("skills")
    @classmethod
    def distinct_skills(cls, values: list[EvaluationSkillInput]) -> list[EvaluationSkillInput]:
        if len({item.skill_id for item in values}) != len(values):
            raise ValueError("Skills não podem se repetir.")
        return sorted(values, key=lambda item: item.skill_id)


class EvaluationRead(BaseModel):
    id: int
    attempt_id: int
    rubric_version: Literal["manual-v1"]
    feedback: Feedback
    skills: list[EvaluationSkillInput]
    created_at: AwareDatetime


class ReviewRead(BaseModel):
    attempt: AttemptRead
    evaluation: EvaluationRead | None
