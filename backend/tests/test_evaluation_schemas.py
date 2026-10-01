"""Entradas externas não podem controlar identidade, notas ou rubrica."""

import pytest
from pydantic import ValidationError
from app.modules.evaluation.schemas import EvaluationCreate


def payload():
    return {"feedback": "  Feedback  ", "skills": [{"skill_id": 2, "classification": "PARTIALLY_MET", "justification": "  Evidence  "}]}


def test_normalization_and_order():
    data = payload()
    data["skills"].append({"skill_id": 1, "classification": "INSUFFICIENT_EVIDENCE", "justification": "Not observable"})
    result = EvaluationCreate.model_validate(data)
    assert result.feedback == "Feedback"
    assert [item.skill_id for item in result.skills] == [1, 2]
    assert result.skills[1].justification == "Evidence"


@pytest.mark.parametrize("field,value", [("feedback", None), ("feedback", 1), ("feedback", " \n"), ("feedback", "x" * 4001), ("skills", []), ("skills", None), ("reviewer_id", 1), ("score", 1000), ("rubric_version", "manual-v1")])
def test_invalid_evaluation(field, value):
    data = payload(); data[field] = value
    with pytest.raises(ValidationError):
        EvaluationCreate.model_validate(data)


@pytest.mark.parametrize("field,value", [("skill_id", True), ("skill_id", "2"), ("skill_id", 0), ("skill_id", 2147483648), ("classification", "OTHER"), ("justification", "\t"), ("justification", None), ("justification", "x" * 2001), ("confidence", 1)])
def test_invalid_skill(field, value):
    data = payload(); data["skills"][0][field] = value
    with pytest.raises(ValidationError):
        EvaluationCreate.model_validate(data)


def test_duplicates_and_limits():
    data = payload(); data["skills"] *= 2
    with pytest.raises(ValidationError):
        EvaluationCreate.model_validate(data)
    data = {"feedback": "x" * 4000, "skills": [{"skill_id": i, "classification": "MET", "justification": "x" * 2000} for i in range(1, 21)]}
    assert len(EvaluationCreate.model_validate(data).skills) == 20
    data["skills"].append({"skill_id": 21, "classification": "NOT_MET", "justification": "Evidence"})
    with pytest.raises(ValidationError):
        EvaluationCreate.model_validate(data)
