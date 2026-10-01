"""Política experimental aprovada; cálculo puro, sem persistência."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext
from app.modules.evaluation.schemas import Classification

POLICY_VERSION = "manual-skill-v1"
INITIAL_SCORE = 500
GAIN = Decimal("40")
CONFIDENCE_PRIOR = Decimal("20")
ZERO = Decimal("0")
ONE = Decimal("1")
OUTCOMES = {"MET": ONE, "PARTIALLY_MET": Decimal("0.5"), "NOT_MET": ZERO}


@dataclass(frozen=True)
class EvidenceTotals:
    mass: Decimal = ZERO
    residual_sum: Decimal = ZERO
    squared_residual_sum: Decimal = ZERO


@dataclass(frozen=True)
class SkillChange:
    score: int
    confidence: Decimal
    totals: EvidenceTotals
    applied: bool
    successful: bool


def _integer(value: int, minimum: int, maximum: int) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("Parâmetro inteiro fora dos limites da política.")


def _validate_totals(totals: EvidenceTotals) -> None:
    values = (totals.mass, totals.residual_sum, totals.squared_residual_sum)
    if any(not isinstance(value, Decimal) or not value.is_finite() for value in values):
        raise ValueError("Acumuladores devem ser Decimal finitos.")
    if totals.mass < 0 or totals.squared_residual_sum < 0:
        raise ValueError("Acumuladores negativos.")
    if totals.mass == 0 and (totals.residual_sum != 0 or totals.squared_residual_sum != 0):
        raise ValueError("Acumuladores sem massa de evidência.")


def _confidence(totals: EvidenceTotals) -> Decimal:
    if totals.mass == 0:
        return ZERO.quantize(Decimal("0.000001"))
    variance = max(ZERO, totals.squared_residual_sum / totals.mass - (totals.residual_sum / totals.mass) ** 2)
    value = totals.mass / (totals.mass + CONFIDENCE_PRIOR) * max(ZERO, ONE - variance)
    return min(Decimal("0.95"), max(ZERO, value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def calculate_change(score: int, difficulty: int, weight: int, attempt_number: int,
                     classification: Classification, totals: EvidenceTotals = EvidenceTotals()) -> SkillChange:
    _integer(score, 0, 1000)
    _integer(difficulty, 0, 1000)
    _integer(weight, 1, 100)
    _integer(attempt_number, 1, 2147483647)
    _validate_totals(totals)
    with localcontext() as context:
        context.prec = 28
        context.rounding = ROUND_HALF_UP
        if classification == "INSUFFICIENT_EVIDENCE":
            return SkillChange(score, _confidence(totals), totals, False, False)
        if classification not in OUTCOMES:
            raise ValueError("Classificação desconhecida.")
        expected = min(Decimal("0.95"), max(Decimal("0.05"), Decimal("0.5") + (Decimal(score) - difficulty) / 1000))
        mass = Decimal(weight) / 100 / attempt_number
        residual = OUTCOMES[classification] - expected
        updated_score = int(min(Decimal(1000), max(ZERO, Decimal(score) + GAIN * mass * residual)).quantize(ONE, rounding=ROUND_HALF_UP))
        updated_totals = EvidenceTotals(totals.mass + mass, totals.residual_sum + mass * residual,
                                        totals.squared_residual_sum + mass * residual ** 2)
        return SkillChange(updated_score, _confidence(updated_totals), updated_totals, True, classification == "MET")
