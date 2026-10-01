"""Exemplos aprovados e propriedades da política; não validação pedagógica."""

from decimal import Decimal, localcontext
import pytest
from app.modules.skills.policy import EvidenceTotals, calculate_change


@pytest.mark.parametrize("score,difficulty,weight,number,classification,expected", [
    (500,500,100,1,"MET",520), (500,500,100,1,"PARTIALLY_MET",500),
    (500,500,100,1,"NOT_MET",480), (500,800,100,1,"MET",532),
    (500,200,100,1,"MET",508), (500,500,60,1,"MET",512),
    (500,500,100,2,"MET",510), (0,1000,100,1,"NOT_MET",0),
    (1000,0,100,1,"MET",1000), (500,500,100,8,"MET",503),
])
def test_examples(score,difficulty,weight,number,classification,expected):
    assert calculate_change(score,difficulty,weight,number,classification).score == expected


def test_insufficient_and_confidence():
    first = calculate_change(500,500,100,1,"MET")
    assert first.confidence == Decimal("0.047619")
    unchanged = calculate_change(first.score,500,100,1,"INSUFFICIENT_EVIDENCE",first.totals)
    assert unchanged.score == first.score and unchanged.totals == first.totals
    assert unchanged.confidence == first.confidence and not unchanged.applied
    consistent = calculate_change(500,500,100,1,"MET",first.totals)
    contradictory = calculate_change(500,500,100,1,"NOT_MET",first.totals)
    assert contradictory.confidence < consistent.confidence
    assert consistent.confidence < Decimal("0.1")


def test_grid_limits_and_ordering():
    for score in range(0,1001,50):
        for difficulty in range(0,1001,50):
            for weight in (1,40,60,100):
                for number in (1,2,10):
                    changes = [calculate_change(score,difficulty,weight,number,c) for c in ("NOT_MET","PARTIALLY_MET","MET")]
                    assert 0 <= changes[0].score <= changes[1].score <= changes[2].score <= 1000
                    assert changes[0].score <= score <= changes[2].score
                    assert all(0 <= change.confidence <= Decimal("0.95") for change in changes)


@pytest.mark.parametrize("field,value", [("score",-1),("score",1001),("score",True),("difficulty",1001),("weight",0),("weight",101),("attempt_number",0),("classification","OTHER")])
def test_invalid_inputs(field,value):
    values = dict(score=500,difficulty=500,weight=100,attempt_number=1,classification="MET")
    values[field] = value
    with pytest.raises(ValueError): calculate_change(**values)


def test_decimal_context_is_local():
    expected = calculate_change(500,733,37,3,"MET")
    with localcontext() as context:
        context.prec = 6
        assert calculate_change(500,733,37,3,"MET") == expected


@pytest.mark.parametrize("totals", [EvidenceTotals(Decimal("NaN")), EvidenceTotals(Decimal("-1")), EvidenceTotals(Decimal(0),Decimal(1))])
def test_invalid_accumulators(totals):
    with pytest.raises(ValueError): calculate_change(500,500,100,1,"MET",totals)
