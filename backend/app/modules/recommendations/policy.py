"""Seleção pura skill-focus-v1; sem banco, relógio implícito ou mutações."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.recommendations.schemas import EvidenceSource, RecommendationKind

POLICY_VERSION = "skill-focus-v1"
CONFIDENCE_THRESHOLD = Decimal("0.20")
MIN_ATTEMPTS = 5
RECENT_WINDOW = timedelta(days=7)
TYPE_PRIORITY = {"EXPLORATION": 0, "PRACTICE": 0, "PROGRESSION": 1, "REVIEW": 2}


def _integer(value: int, minimum: int, maximum: int) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("Inteiro fora dos limites da política.")


def _aware(value: datetime) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("Data deve conter fuso horário.")


@dataclass(frozen=True)
class SkillContext:
    skill_id: int
    weight: int
    is_active: bool = True
    score: int | None = None
    confidence: Decimal | None = None
    attempts: int | None = None
    assessment_score: int | None = None

    def __post_init__(self) -> None:
        _integer(self.skill_id, 1, 2147483647)
        _integer(self.weight, 1, 100)
        if type(self.is_active) is not bool:
            raise ValueError("Atividade deve ser booleana.")
        if self.assessment_score is not None:
            _integer(self.assessment_score, 0, 1000)
        if self.score is None:
            if self.confidence is not None or self.attempts is not None:
                raise ValueError("Progresso incompleto.")
        else:
            _integer(self.score, 0, 1000)
            if self.attempts is None:
                raise ValueError("Progresso exige contagem de evidências.")
            _integer(self.attempts, 1, 2147483647)
            if (not isinstance(self.confidence, Decimal) or not self.confidence.is_finite()
                    or not Decimal(0) <= self.confidence <= Decimal("0.95")):
                raise ValueError("Confiança inválida.")


@dataclass(frozen=True)
class Candidate:
    challenge_id: int
    difficulty_score: int
    skills: tuple[SkillContext, ...]
    is_active: bool = True
    has_open_attempt: bool = False
    has_pending_evaluation: bool = False
    has_future_practice: bool = False
    last_submitted_at: datetime | None = None

    def __post_init__(self) -> None:
        _integer(self.challenge_id, 1, 2147483647)
        _integer(self.difficulty_score, 0, 1000)
        if not isinstance(self.skills, tuple) or not 1 <= len(self.skills) <= 20:
            raise ValueError("Candidato exige de 1 a 20 skills imutáveis.")
        if (len({s.skill_id for s in self.skills}) != len(self.skills)
                or sum(s.weight for s in self.skills) != 100):
            raise ValueError("Skills devem ser distintas com pesos somando 100%.")
        for flag in (self.is_active, self.has_open_attempt, self.has_pending_evaluation, self.has_future_practice):
            if type(flag) is not bool:
                raise ValueError("Estado deve ser booleano.")
        if self.last_submitted_at is not None:
            _aware(self.last_submitted_at)


@dataclass(frozen=True)
class SkillReference:
    skill_id: int
    weight: int
    source: EvidenceSource
    score: int | None
    confidence: Decimal | None
    anchor: int
    ceiling: int


@dataclass(frozen=True)
class Selection:
    challenge_id: int
    kind: RecommendationKind
    practiced_recently: bool
    weighted_distance: int
    references: tuple[SkillReference, ...]


def _reference(skill: SkillContext) -> SkillReference:
    if skill.score is not None:
        assert skill.confidence is not None and skill.attempts is not None
        margin = 200 if skill.confidence >= CONFIDENCE_THRESHOLD and skill.attempts >= MIN_ATTEMPTS else 100
        return SkillReference(skill.skill_id, skill.weight, "USER_SKILL", skill.score,
                              skill.confidence, skill.score, min(1000, skill.score + margin))
    if skill.assessment_score is not None:
        return SkillReference(skill.skill_id, skill.weight, "ASSESSMENT", skill.assessment_score,
                              None, skill.assessment_score, min(1000, skill.assessment_score + 100))
    return SkillReference(skill.skill_id, skill.weight, "NONE", None, None, 100, 200)


def select_candidates(candidates: Sequence[Candidate], *, skill_id: int,
                      now: datetime, limit: int = 5) -> list[Selection]:
    """Contextos já pertencem ao dono; repository resolve diagnóstico/histórico."""
    _integer(skill_id, 1, 2147483647)
    _integer(limit, 1, 10)
    _aware(now)
    if len({candidate.challenge_id for candidate in candidates}) != len(candidates):
        raise ValueError("Candidatos duplicados.")
    selected: list[Selection] = []
    for candidate in candidates:
        if (not candidate.is_active or candidate.has_open_attempt or candidate.has_pending_evaluation
                or candidate.has_future_practice or any(not s.is_active for s in candidate.skills)
                or skill_id not in {s.skill_id for s in candidate.skills}):
            continue
        submitted = candidate.last_submitted_at
        if submitted is not None and submitted > now:
            continue
        references = tuple(_reference(s) for s in sorted(candidate.skills, key=lambda s: s.skill_id))
        difficulty = candidate.difficulty_score
        if any(difficulty > reference.ceiling for reference in references):
            continue
        maximum_delta = max(difficulty - reference.anchor for reference in references)
        kind: RecommendationKind
        if any(reference.source != "USER_SKILL" for reference in references):
            kind = "EXPLORATION"
        elif maximum_delta < -200:
            kind = "REVIEW"
        elif maximum_delta > 100:
            kind = "PROGRESSION"
        else:
            kind = "PRACTICE"
        recent = submitted is not None and now - RECENT_WINDOW <= submitted <= now
        distance = sum(reference.weight * abs(difficulty - reference.anchor) for reference in references)
        selected.append(Selection(candidate.challenge_id, kind, recent, distance, references))
    selected.sort(key=lambda item: (item.practiced_recently, TYPE_PRIORITY[item.kind],
                                   item.weighted_distance, item.challenge_id))
    return selected[:limit]
