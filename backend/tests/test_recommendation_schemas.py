"""Fronteiras externas e distinção entre evidência e âncora técnica."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.modules.recommendations.schemas import RecommendationQuery, SkillReferenceRead, RecommendationResponse


@pytest.mark.parametrize("query", [{}, {"skill_id": 0}, {"skill_id": 2147483648},
    {"skill_id": "abc"}, {"skill_id": 1, "limit": 0}, {"skill_id": 1, "limit": 11},
    {"skill_id": 1, "user_id": 2}, {"skill_id": 1, "offset": 0}])
def test_invalid_query(query):
    with pytest.raises(ValidationError):
        RecommendationQuery.model_validate(query)


def test_query_accepts_http_strings():
    assert RecommendationQuery.model_validate({"skill_id": "1"}).limit == 5
    assert RecommendationQuery.model_validate({"skill_id": "2147483647", "limit": "10"}).limit == 10


@pytest.mark.parametrize("source,score,confidence", [
    ("NONE", 100, None), ("NONE", None, "0"), ("ASSESSMENT", 600, "0"),
    ("ASSESSMENT", None, None), ("USER_SKILL", 600, None),
    ("USER_SKILL", None, "0.2"), ("USER_SKILL", 600, "NaN"),
    ("USER_SKILL", 600, "0.950001")])
def test_inconsistent_reference(source, score, confidence):
    with pytest.raises(ValidationError):
        SkillReferenceRead(skill_id=1, weight=100, source=source, reference_score=score, confidence=confidence)


def response_data():
    return dict(generated_at=datetime.now(timezone.utc), skill_id=1, limit=5,
        items=[dict(challenge_id=1, title="Test", difficulty_score=500, estimated_minutes=10,
                    kind="PRACTICE", practiced_recently=False, reason="Referência de prática disponível.",
                    skills=[dict(skill_id=1, weight=100, source="USER_SKILL", reference_score=500, confidence=Decimal("0.200000"))])],
        empty_reason=None)


def test_response_and_empty_serialization():
    data = response_data()
    result = RecommendationResponse.model_validate(data).model_dump(mode="json")
    assert result["items"][0]["skills"][0]["confidence"] == "0.200000"
    assert result["policy_version"] == "skill-focus-v1"
    data.update(items=[], empty_reason="NO_ELIGIBLE_CHALLENGES")
    assert RecommendationResponse.model_validate(data).items == []
    for source, score in [("NONE", None), ("ASSESSMENT", 600)]:
        assert SkillReferenceRead(skill_id=1, weight=100, source=source, reference_score=score, confidence=None).confidence is None


@pytest.mark.parametrize("case", ["empty", "duplicate", "focal", "naive", "weight", "source", "extra"])
def test_invalid_response(case):
    data = response_data()
    if case == "empty": data["empty_reason"] = "NO_ELIGIBLE_CHALLENGES"
    elif case == "duplicate": data["items"] *= 2
    elif case == "focal": data["skill_id"] = 2
    elif case == "naive": data["generated_at"] = datetime(2026, 9, 30)
    elif case == "weight": data["items"][0]["skills"][0]["weight"] = 99
    elif case == "source": data["items"][0]["skills"][0]["source"] = "NONE"
    else: data["user_id"] = 1
    with pytest.raises(ValidationError):
        RecommendationResponse.model_validate(data)
