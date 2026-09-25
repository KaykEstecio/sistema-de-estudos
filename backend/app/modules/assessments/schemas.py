"""Contratos públicos explícitos e entrada privada de autoria."""

from datetime import datetime
from typing import Annotated, Literal, Self
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, StrictBool, model_validator
from app.modules.categories.schemas import CatalogId, Slug

Option = Literal["A", "B", "C", "D"]
Prompt = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=4000)]
OptionText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=1000)]


class QuestionOptions(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    A: OptionText
    B: OptionText
    C: OptionText
    D: OptionText


class QuestionCreate(BaseModel):
    """Somente importação local; nunca usado como resposta pública."""
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    code: Slug
    skill_id: CatalogId
    prompt: Prompt
    options: QuestionOptions
    correct_option: Option = Field(repr=False)
    is_active: StrictBool = True


class AssessmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    skill_ids: list[CatalogId] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def distinct_skills(self) -> Self:
        if len(self.skill_ids) != len(set(self.skill_ids)):
            raise ValueError("Skills não podem se repetir.")
        return self


class AnswerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    item_id: CatalogId
    selected_option: Option


class AssessmentItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    skill_id: int
    position: int
    prompt: str
    options: QuestionOptions
    selected_option: Option | None


class AssessmentResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    score: int = Field(ge=0, le=1000)
    confidence: float = Field(ge=0, le=1)
    correct_count: int = Field(ge=0)
    question_count: int = Field(gt=0)


class AssessmentRead(BaseModel):
    id: int
    assessment_type: Literal["INITIAL"]
    started_at: datetime
    completed_at: datetime | None
    items: list[AssessmentItemRead]
    results: list[AssessmentResultRead]
