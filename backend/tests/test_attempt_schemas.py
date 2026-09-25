"""Entrada restrita e formato completo do snapshot histórico."""

import pytest
from pydantic import ValidationError

from app.modules.attempts.schemas import AttemptDraft, ChallengeSnapshot


@pytest.mark.parametrize("body", [{}, {"draft_answer": None}, {"draft_answer": 1},
    {"draft_answer": "x" * 20001}, {"draft_answer": "x", "status": "SUBMITTED"},
    {"draft_answer": "x", "user_id": 1}])
def test_attempt_draft_rejects_invalid_input(body):
    with pytest.raises(ValidationError):
        AttemptDraft.model_validate(body)


def test_attempt_text_and_snapshot():
    for text in ("", "  code\n", "x" * 20000):
        assert AttemptDraft(draft_answer=text).draft_answer == text
    data = dict(title="Fixture", description="Text", challenge_type="CODE", difficulty="EASY",
                difficulty_score=0, estimated_minutes=1, starter_code=None,
                skills=[dict(skill_id=2, weight=50), dict(skill_id=1, weight=50)])
    assert [s.skill_id for s in ChallengeSnapshot.model_validate(data).skills] == [1, 2]
    for change in ({"skills": []}, {"skills": [dict(skill_id=1, weight=99)]},
                   {"skills": [dict(skill_id=1, weight=50)] * 2}, {"is_active": True},
                   {"difficulty_score": True}, {"challenge_type": "OTHER"}):
        with pytest.raises(ValidationError):
            ChallengeSnapshot.model_validate(data | change)
