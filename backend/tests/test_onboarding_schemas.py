"""Validação do perfil e semântica de edição parcial."""

import pytest
from pydantic import ValidationError
from app.modules.onboarding.schemas import OnboardingCreate, OnboardingUpdate, OnboardingRead


def payload():
    return {"declared_experience": "BEGINNER", "interest_category_ids": [1, 2],
            "primary_goal": {"goal_type": " Learn ", "description": " "}}


def test_normalization_and_partial_update():
    data = OnboardingCreate.model_validate(payload())
    assert data.primary_goal.goal_type == "Learn" and data.primary_goal.description is None
    patch = OnboardingUpdate(primary_goal={"goal_type": "Other"})
    assert patch.model_fields_set == {"primary_goal"}
    assert patch.primary_goal.description is None
    assert OnboardingCreate.model_validate({**payload(), "interest_category_ids": list(range(1, 21))})
    assert OnboardingRead(onboarding_completed=False, declared_experience=None,
                          interest_category_ids=[], primary_goal=None).model_dump()["primary_goal"] is None


@pytest.mark.parametrize("changes", [
    {"declared_experience": "beginner"}, {"declared_experience": "EXPERT"},
    {"interest_category_ids": []}, {"interest_category_ids": [1, 1]},
    {"interest_category_ids": [True]}, {"interest_category_ids": ["1"]},
    {"interest_category_ids": [0]}, {"interest_category_ids": [2147483648]},
    {"interest_category_ids": list(range(1, 22))}, {"user_id": 1},
    {"onboarding_completed": True}, {"primary_goal": {}},
    {"primary_goal": {"goal_type": " "}}, {"primary_goal": {"goal_type": 12}},
    {"primary_goal": {"goal_type": "x" * 121}},
    {"primary_goal": {"goal_type": "Learn", "description": "x" * 2001}},
    {"primary_goal": {"goal_type": "Learn", "is_primary": True}},
])
def test_invalid_create(changes):
    with pytest.raises(ValidationError):
        OnboardingCreate.model_validate({**payload(), **changes})


@pytest.mark.parametrize("changes", [{}, {"declared_experience": None}, {"primary_goal": None},
                                      {"interest_category_ids": None}, {"user_id": 2}])
def test_invalid_patch(changes):
    with pytest.raises(ValidationError):
        OnboardingUpdate.model_validate(changes)
