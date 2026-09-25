"""Resposta textual e contexto histórico, sem campos de controle na entrada."""

from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, StringConstraints, field_validator

from app.modules.challenges.schemas import Title, Description, ChallengeType, Difficulty, Score, Minutes, StarterCode, SkillList, ChallengeSkillInput

DraftAnswer = Annotated[str, StringConstraints(strict=True, max_length=20000)]
AttemptStatus = Literal["IN_PROGRESS", "SUBMITTED"]


class AttemptDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    draft_answer: DraftAnswer


class ChallengeSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    title: Title
    description: Description
    challenge_type: ChallengeType
    difficulty: Difficulty
    difficulty_score: Score
    estimated_minutes: Minutes
    starter_code: StarterCode | None
    skills: SkillList

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[ChallengeSkillInput]) -> list[ChallengeSkillInput]:
        if len({item.skill_id for item in value}) != len(value) or sum(item.weight for item in value) != 100:
            raise ValueError("Contexto exige skills distintas com pesos somando 100%.")
        return sorted(value, key=lambda item: item.skill_id)


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    challenge_id: int
    status: AttemptStatus
    draft_answer: DraftAnswer
    attempt_number: int
    challenge_snapshot: ChallengeSnapshot
    started_at: AwareDatetime
    submitted_at: AwareDatetime | None
    last_activity_at: AwareDatetime
