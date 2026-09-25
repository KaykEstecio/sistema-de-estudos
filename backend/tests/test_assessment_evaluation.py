"""Cálculo explícito por skill sem confiança artificial."""

import pytest
from app.modules.assessments.evaluation import evaluate
from app.modules.assessments.models import AssessmentItem


def items(correct, total=3, skill_id=1):
    return [AssessmentItem(skill_id=skill_id, selected_option="A" if index < correct else "B", correct_option="A")
            for index in range(total)]


@pytest.mark.parametrize("correct,score", [(0, 0), (1, 333), (2, 667), (3, 1000)])
def test_score(correct, score):
    result = evaluate(items(correct))[0]
    assert result.score == score and result.confidence == 0
    assert result.correct_count == correct and result.question_count == 3


def test_rounding_and_independent_skills():
    result = evaluate(items(1, 16, 2) + items(3))
    assert [(value.skill_id, value.score) for value in result] == [(1, 1000), (2, 63)]


@pytest.mark.parametrize("values", [[], [AssessmentItem(skill_id=1, correct_option="A", selected_option=None)]])
def test_incomplete(values):
    with pytest.raises(ValueError):
        evaluate(values)
