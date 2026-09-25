"""Correção pura do diagnóstico; não estima domínio nem persiste dados."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from app.modules.assessments.models import AssessmentItem

INITIAL_DIAGNOSTIC_CONFIDENCE = Decimal("0")


@dataclass(frozen=True)
class SkillResult:
    skill_id: int
    score: int
    confidence: Decimal
    correct_count: int
    question_count: int


def evaluate(items: Sequence[AssessmentItem]) -> list[SkillResult]:
    if not items or any(item.selected_option is None for item in items):
        raise ValueError("Diagnóstico incompleto.")
    counts: dict[int, list[int]] = {}
    for item in items:
        correct, total = counts.setdefault(item.skill_id, [0, 0])
        counts[item.skill_id] = [correct + int(item.selected_option == item.correct_option), total + 1]
    return [SkillResult(skill_id=skill_id,
                       score=int((Decimal(correct) * 1000 / total).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
                       confidence=INITIAL_DIAGNOSTIC_CONFIDENCE, correct_count=correct, question_count=total)
            for skill_id, (correct, total) in sorted(counts.items())]
