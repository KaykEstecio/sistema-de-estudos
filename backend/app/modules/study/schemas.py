from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, AwareDatetime, field_validator

Title = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=200)]
Text = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=12000)]
Mistakes = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=6000)]


class StudyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    skill_id: int = Field(strict=True, ge=1, le=2147483647)
    title: Title
    explanation: Text
    code_example: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=12000)]
    common_mistakes: Mistakes

    @field_validator('code_example')
    @classmethod
    def nonempty_code(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Exemplo de código obrigatório.')
        return value


class StudyQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    skill_id: int | None = Field(default=None, ge=1, le=2147483647)
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class StudyPracticeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    challenge_id: int | None = Field(strict=True, ge=1, le=2147483647)


class StudyOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    study_order: int | None = Field(strict=True, ge=1, le=10000)


class StudySummary(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    title: str
    completed_at: AwareDatetime | None
    study_order: int | None


class StudyRead(StudySummary):
    explanation: str
    code_example: str
    common_mistakes: str


class StudyPage(BaseModel):
    items: list[StudySummary]
    total: int
    limit: int
    offset: int
    has_sequence: bool = False
    next_content: StudySummary | None = None
