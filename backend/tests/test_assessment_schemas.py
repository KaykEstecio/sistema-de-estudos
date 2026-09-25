"""Validação e ausência de dados de correção nos contratos públicos."""

import pytest
from pydantic import ValidationError
from app.modules.assessments.schemas import AssessmentCreate, AnswerCreate, QuestionCreate, AssessmentItemRead
from app.modules.assessments.models import AssessmentItem


@pytest.mark.parametrize("data", [{"skill_ids": []}, {"skill_ids": [1, 1]}, {"skill_ids": [1, 2, 3, 4]},
    {"skill_ids": [True]}, {"skill_ids": ["1"]}, {"skill_ids": [0]}, {"skill_ids": [2147483648]},
    {"skill_ids": [1], "user_id": 2}, {"skill_ids": [1], "score": 1000}])
def test_invalid_assessment_input(data):
    with pytest.raises(ValidationError):
        AssessmentCreate.model_validate(data)


@pytest.mark.parametrize("data", [{"item_id": 1, "selected_option": "a"}, {"item_id": 1, "selected_option": "X"},
    {"item_id": True, "selected_option": "A"}, {"item_id": 1, "selected_option": "A", "correct_option": "A"}])
def test_invalid_answer(data):
    with pytest.raises(ValidationError):
        AnswerCreate.model_validate(data)


def test_question_validation_and_public_projection():
    payload = {"code": " QUESTION-1 ", "skill_id": 1, "prompt": " Text ",
               "options": {"A": " one ", "B": "two", "C": "three", "D": "four"}, "correct_option": "B"}
    question = QuestionCreate.model_validate(payload)
    assert question.code == "question-1" and question.options.A == "one"
    for changes in ({"prompt": " "}, {"prompt": "x" * 4001}, {"correct_option": "X"}, {"is_active": 1},
                    {"options": {"A": "one"}}, {"options": {**payload["options"], "E": "five"}},
                    {"options": {**payload["options"], "A": "x" * 1001}}):
        with pytest.raises(ValidationError):
            QuestionCreate.model_validate({**payload, **changes})
    item = AssessmentItem(id=1, assessment_id=2, skill_id=1, position=1, prompt="Text",
                          options=question.options.model_dump(), correct_option="B", selected_option="A")
    public = AssessmentItemRead.model_validate(item).model_dump()
    assert set(public) == {"id", "skill_id", "position", "prompt", "options", "selected_option"}
    assert "correct_option" not in public and "assessment_id" not in public
