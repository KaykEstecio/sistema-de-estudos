"""Contratos de conteúdo público; regras de publicação pertencem ao service."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StringConstraints, field_validator, model_validator

from app.modules.categories.schemas import CatalogId, CategoryListQuery

ChallengeType = Literal["QUIZ", "CODE", "BUG_FIX", "CODE_READING", "REFACTORING", "SQL", "API", "ARCHITECTURE", "PROJECT"]
Difficulty = Literal["VERY_EASY", "EASY", "MEDIUM", "HARD", "VERY_HARD"]
Title = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=20000)]
StarterCode = Annotated[str, StringConstraints(strict=True, max_length=20000)]
Score = Annotated[int, Field(strict=True, ge=0, le=1000)]
Minutes = Annotated[int, Field(strict=True, ge=1, le=1440)]


class ChallengeSkillInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    skill_id: CatalogId
    weight: Annotated[int, Field(strict=True, ge=1, le=100)]


SkillList = Annotated[list[ChallengeSkillInput], Field(min_length=1, max_length=20)]


class ChallengeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    title: Title
    description: Description
    challenge_type: ChallengeType
    difficulty: Difficulty
    difficulty_score: Score
    estimated_minutes: Minutes
    starter_code: StarterCode | None = None
    is_active: StrictBool = False
    skills: SkillList

    @field_validator("skills")
    @classmethod
    def distinct_skills(cls, value: list[ChallengeSkillInput]) -> list[ChallengeSkillInput]:
        if len({item.skill_id for item in value}) != len(value):
            raise ValueError("Skills não podem se repetir.")
        return value


class ChallengeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    title: Title | None = None
    description: Description | None = None
    challenge_type: ChallengeType | None = None
    difficulty: Difficulty | None = None
    difficulty_score: Score | None = None
    estimated_minutes: Minutes | None = None
    starter_code: StarterCode | None = None
    is_active: StrictBool | None = None
    skills: SkillList | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo editável.")
        for field in self.model_fields_set - {"starter_code"}:
            if getattr(self, field) is None:
                raise ValueError("Somente starter_code aceita null.")
        if self.skills is not None:
            ChallengeCreate.distinct_skills(self.skills)
        return self


class ChallengeSkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    weight: int


class ChallengeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: Difficulty
    difficulty_score: int
    estimated_minutes: int
    starter_code: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    skills: list[ChallengeSkillRead]


class ChallengeListQuery(CategoryListQuery):
    skill: int | None = Field(default=None, ge=1, le=2147483647)
    difficulty: Difficulty | None = None
    challenge_type: ChallengeType | None = Field(default=None, alias="type")
    is_active: bool | None = None


class ChallengePage(BaseModel):
    items: list[ChallengeRead]
    total: int
    limit: int
    offset: int
