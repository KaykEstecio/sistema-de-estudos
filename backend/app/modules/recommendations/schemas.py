"""Contrato de recomendações; não executa seleção nem altera progresso."""

from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictBool, model_validator
from app.modules.categories.schemas import CatalogId
from app.modules.challenges.schemas import Score, Title, Minutes

RecommendationKind = Literal["EXPLORATION", "PRACTICE", "PROGRESSION", "REVIEW"]
EvidenceSource = Literal["USER_SKILL", "ASSESSMENT", "NONE"]


class RecommendationQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    skill_id: int = Field(ge=1, le=2147483647)
    limit: int = Field(default=5, ge=1, le=10)


class SkillReferenceRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill_id: CatalogId
    weight: Annotated[int, Field(strict=True, ge=1, le=100)]
    source: EvidenceSource
    reference_score: Score | None
    confidence: Annotated[Decimal, Field(ge=0, le=Decimal("0.95"), allow_inf_nan=False)] | None

    @model_validator(mode="after")
    def consistent_source(self) -> Self:
        if self.source == "NONE":
            valid = self.reference_score is None and self.confidence is None
        elif self.source == "ASSESSMENT":
            valid = self.reference_score is not None and self.confidence is None
        else:
            valid = self.reference_score is not None and self.confidence is not None
        if not valid:
            raise ValueError("Referência incompatível com a fonte de evidência.")
        return self


class RecommendationRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    challenge_id: CatalogId
    title: Title
    difficulty_score: Score
    estimated_minutes: Minutes
    kind: RecommendationKind
    practiced_recently: StrictBool
    reason: str = Field(min_length=1)
    skills: list[SkillReferenceRead] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def consistent_skills(self) -> Self:
        ids = [item.skill_id for item in self.skills]
        if ids != sorted(set(ids)) or sum(item.weight for item in self.skills) != 100:
            raise ValueError("Skills devem ser distintas, ordenadas e somar 100%.")
        return self


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_version: Literal["skill-focus-v1"] = "skill-focus-v1"
    generated_at: AwareDatetime
    skill_id: CatalogId
    limit: int = Field(ge=1, le=10)
    items: list[RecommendationRead] = Field(max_length=10)
    empty_reason: Literal["NO_ELIGIBLE_CHALLENGES"] | None

    @model_validator(mode="after")
    def consistent_result(self) -> Self:
        if len(self.items) > self.limit or bool(self.items) != (self.empty_reason is None):
            raise ValueError("Resultado incompatível com limite ou motivo de ausência.")
        if len({item.challenge_id for item in self.items}) != len(self.items):
            raise ValueError("Desafio repetido.")
        if any(self.skill_id not in {skill.skill_id for skill in item.skills} for item in self.items):
            raise ValueError("Recomendação sem a skill selecionada.")
        return self
