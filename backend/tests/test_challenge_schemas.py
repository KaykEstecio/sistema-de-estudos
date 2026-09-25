"""Limites externos e distinção entre omissão e null no catálogo."""

import pytest
from pydantic import ValidationError

from app.modules.challenges.schemas import ChallengeCreate, ChallengeUpdate, ChallengeListQuery


def payload():
    return dict(title=" Test ", description=" Description ", challenge_type="CODE", difficulty="EASY",
                difficulty_score=0, estimated_minutes=1, skills=[dict(skill_id=1, weight=100)])


@pytest.mark.parametrize("field,value", [
    ("title", " "), ("title", "x" * 201), ("description", "x" * 20001),
    ("challenge_type", "code"), ("difficulty", "OTHER"),
    ("difficulty_score", -1), ("difficulty_score", 1001), ("difficulty_score", True),
    ("estimated_minutes", "10"), ("estimated_minutes", 1441), ("estimated_minutes", 0),
    ("starter_code", "x" * 20001), ("is_active", 1), ("skills", []),
    ("skills", [dict(skill_id=1, weight=50)] * 2),
    ("skills", [dict(skill_id=True, weight=100)]),
    ("skills", [dict(skill_id=1, weight=100.0)]),
    ("skills", [dict(skill_id=1, weight=0)]), ("module_id", 1),
])
def test_invalid_challenge_input(field, value):
    with pytest.raises(ValidationError):
        ChallengeCreate.model_validate(payload() | {field: value})


def test_challenge_defaults_boundaries_and_patch():
    data = ChallengeCreate.model_validate(payload())
    assert data.title == "Test" and data.description == "Description"
    assert data.is_active is False and data.starter_code is None
    data = ChallengeCreate.model_validate(payload() | dict(title="x" * 200, description="x" * 20000,
        difficulty_score=1000, estimated_minutes=1440, starter_code="  code\n"))
    assert data.starter_code == "  code\n"
    assert ChallengeUpdate(starter_code=None).model_dump(exclude_unset=True) == {"starter_code": None}
    for body in ({}, {"title": None}, {"skills": None}, {"is_active": None},
                 {"skills": [dict(skill_id=1, weight=50)] * 2}):
        with pytest.raises(ValidationError):
            ChallengeUpdate.model_validate(body)
    # A soma é responsabilidade do service, com erro de domínio 409.
    assert ChallengeCreate.model_validate(payload() | {"skills": [dict(skill_id=1, weight=1)]})
    assert len(ChallengeCreate.model_validate(payload() | {"skills": [
        dict(skill_id=i, weight=5) for i in range(1, 21)]}).skills) == 20
    with pytest.raises(ValidationError):
        ChallengeCreate.model_validate(payload() | {"skills": [
            dict(skill_id=i, weight=5) for i in range(1, 22)]})


def test_challenge_query_contract():
    query = ChallengeListQuery.model_validate(dict(type="CODE", skill="1", limit="10"))
    assert query.challenge_type == "CODE" and query.skill == 1 and query.limit == 10
    for body in ({"completed": True}, {"challenge_type": "CODE"}, {"limit": 101}, {"offset": -1}, {"skill": 0}):
        with pytest.raises(ValidationError):
            ChallengeListQuery.model_validate(body)
