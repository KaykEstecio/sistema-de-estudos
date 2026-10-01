"""Critérios observáveis da política de recomendação experimental."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from itertools import permutations
import pytest
from app.modules.recommendations.policy import Candidate, SkillContext, select_candidates

NOW = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)


def progress(score=500, confidence="0.20", attempts=5, **kwargs):
    return SkillContext(skill_id=1, weight=100, score=score, confidence=Decimal(confidence), attempts=attempts, **kwargs)


def choose(difficulty, skill, **kwargs):
    return select_candidates([Candidate(1, difficulty, (skill,), **kwargs)], skill_id=1, now=NOW)


@pytest.mark.parametrize("skill,difficulty,kind", [
    (SkillContext(1, 100), 100, "EXPLORATION"), (SkillContext(1, 100), 200, "EXPLORATION"),
    (SkillContext(1, 100), 201, None),
    (SkillContext(1, 100, assessment_score=600), 650, "EXPLORATION"),
    (SkillContext(1, 100, assessment_score=600), 701, None),
    (progress(confidence="0.10"), 600, "PRACTICE"), (progress(confidence="0.10"), 601, None),
    (progress(), 600, "PRACTICE"), (progress(), 601, "PROGRESSION"),
    (progress(), 700, "PROGRESSION"), (progress(), 701, None),
    (progress(confidence="0.199999"), 601, None), (progress(attempts=4), 601, None),
    (progress(score=700), 499, "REVIEW"), (progress(score=700), 500, "PRACTICE"),
    (progress(score=0), 0, "PRACTICE"), (progress(score=1000), 1000, "PRACTICE"),
    (progress(score=1000), 0, "REVIEW"),
])
def test_documented_examples_and_boundaries(skill, difficulty, kind):
    result = choose(difficulty, skill)
    assert (result[0].kind if result else None) == kind


def test_source_precedence_and_unknown_anchor():
    selected = choose(600, progress(assessment_score=900))[0]
    assert selected.references[0].source == "USER_SKILL" and selected.references[0].score == 500
    assert choose(750, progress(assessment_score=900)) == []
    unknown = choose(100, SkillContext(1, 100))[0].references[0]
    assert unknown.score is None and unknown.confidence is None and unknown.anchor == 100


def test_secondary_skill_cannot_be_hidden_by_weight():
    strong = replace(progress(800), weight=90)
    weak = replace(progress(200, "0.10"), skill_id=2, weight=10)
    assert select_candidates([Candidate(1, 400, (strong, weak))], skill_id=1, now=NOW) == []
    mixed = select_candidates([Candidate(1, 300, (strong, weak))], skill_id=1, now=NOW)[0]
    assert mixed.kind == "PRACTICE"
    unknown = SkillContext(2, 10)
    assert select_candidates([Candidate(1, 201, (strong, unknown))], skill_id=1, now=NOW) == []
    assert select_candidates([Candidate(1, 200, (unknown, strong))], skill_id=1, now=NOW)[0].kind == "EXPLORATION"


@pytest.mark.parametrize("changes", [dict(is_active=False), dict(has_open_attempt=True),
    dict(has_pending_evaluation=True), dict(has_future_practice=True),
    dict(last_submitted_at=NOW+timedelta(microseconds=1))])
def test_excluded_history_or_catalog(changes):
    assert choose(500, progress(), **changes) == []


def test_inactive_skill_or_missing_focal():
    assert choose(500, replace(progress(), is_active=False)) == []
    assert select_candidates([Candidate(1, 500, (progress(),))], skill_id=2, now=NOW) == []


@pytest.mark.parametrize("age,recent", [(timedelta(0), True), (timedelta(days=7), True),
    (timedelta(days=7, microseconds=1), False), (timedelta(days=20), False)])
def test_recent_boundary_uses_submission(age, recent):
    assert choose(500, progress(), last_submitted_at=NOW-age)[0].practiced_recently is recent


def test_ranking_is_stable_and_limits_only_after_sorting():
    candidates = [Candidate(9, 480, (progress(),)), Candidate(3, 480, (progress(),)),
                  Candidate(1, 500, (progress(),), last_submitted_at=NOW),
                  Candidate(2, 650, (progress(),)), Candidate(4, 200, (progress(),))]
    for order in permutations(candidates):
        result = select_candidates(order, skill_id=1, now=NOW)
        assert [item.challenge_id for item in result] == [3, 9, 2, 4, 1]
        assert select_candidates(order, skill_id=1, now=NOW, limit=1) == result[:1]
    assert candidates[0].challenge_id == 9


def test_weighted_distance_and_empty():
    skills = (replace(progress(500), weight=60), replace(progress(400), skill_id=2, weight=40))
    selected = select_candidates([Candidate(1, 450, skills)], skill_id=1, now=NOW)[0]
    assert selected.weighted_distance == 5000
    assert select_candidates([], skill_id=1, now=NOW) == []


@pytest.mark.parametrize("kwargs", [dict(score=-1), dict(score=1001), dict(confidence="NaN"),
    dict(confidence="Infinity"), dict(confidence="0.96"), dict(attempts=0)])
def test_invalid_evidence(kwargs):
    with pytest.raises(ValueError): progress(**kwargs)


def test_invalid_structures_and_clock():
    with pytest.raises(ValueError): Candidate(1, 500, ())
    with pytest.raises(ValueError): Candidate(1, 500, (replace(progress(), weight=99),))
    with pytest.raises(ValueError): Candidate(1, 500, (replace(progress(), weight=50),)*2)
    with pytest.raises(ValueError): SkillContext(1, 100, confidence=Decimal("0.2"))
    candidate = Candidate(1, 500, (progress(),))
    with pytest.raises(ValueError): select_candidates([candidate, candidate], skill_id=1, now=NOW)
    with pytest.raises(ValueError): select_candidates([candidate], skill_id=1, now=NOW.replace(tzinfo=None))
    with pytest.raises(ValueError): select_candidates([candidate], skill_id=1, now=NOW, limit=11)


def test_grid_respects_each_ceiling_and_preserves_inputs():
    for score in (0, 100, 500, 900, 1000):
        for confidence in ("0", "0.199999", "0.20", "0.95"):
            for attempts in (1, 4, 5, 20):
                skill = progress(score, confidence, attempts)
                margin = 200 if Decimal(confidence) >= Decimal("0.20") and attempts >= 5 else 100
                for difficulty in range(0, 1001, 25):
                    result = choose(difficulty, skill)
                    assert bool(result) == (difficulty <= min(1000, score+margin))
                    assert skill.score == score and skill.attempts == attempts
