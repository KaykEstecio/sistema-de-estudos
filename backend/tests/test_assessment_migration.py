"""Integridade e reversão do diagnóstico em PostgreSQL descartável."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.assessments.models import Assessment, AssessmentQuestion, AssessmentItem, AssessmentResult
from app.modules.users.models import User, DeclaredExperience
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.onboarding.models import UserInterest, UserGoal


def test_assessment_migration(migrated_database):
    engine, alembic = migrated_database
    with Session(engine) as session:
        user = User(name="Test", email="assessment@example.com", password_hash="test",
                    declared_experience=DeclaredExperience.BASIC, onboarding_completed=True)
        category = Category(name="Logic", slug="logic")
        session.add_all([user, category]); session.flush()
        skill = Skill(category_id=category.id, name="Logic", slug="logic")
        session.add(skill); session.flush()
        session.add_all([UserInterest(user_id=user.id, category_id=category.id), UserGoal(user_id=user.id, goal_type="Learn")])
        assessment = Assessment(user_id=user.id)
        question = AssessmentQuestion(code="question-1", skill_id=skill.id, prompt="Original",
                                      options={"A": "one", "B": "two", "C": "three", "D": "four"}, correct_option="A")
        session.add_all([assessment, question]); session.flush()
        item = AssessmentItem(assessment_id=assessment.id, skill_id=skill.id, position=1,
                              prompt=question.prompt, options=dict(question.options), correct_option=question.correct_option)
        result = AssessmentResult(assessment_id=assessment.id, skill_id=skill.id, score=333,
                                  confidence=Decimal("0"), correct_count=1, question_count=3)
        session.add_all([item, result]); session.commit()
        uid, sid, aid, iid, rid = user.id, skill.id, assessment.id, item.id, result.id
        assert assessment.assessment_type == "INITIAL" and assessment.completed_at is None
        assert assessment.started_at.tzinfo is not None and question.is_active
        assert item.selected_option is None and result.confidence == Decimal("0.000")
        question.prompt = "Changed"
        question.correct_option = "B"
        session.commit()
        assert item.prompt == "Original" and item.correct_option == "A"
    cases = [
        ("INSERT INTO assessments(user_id) VALUES(:uid)", "uq_assessments_open_user"),
        ("INSERT INTO assessments(user_id) VALUES(2147483647)", "fk_assessments_user"),
        ("UPDATE assessments SET assessment_type='OTHER' WHERE id=:aid", "ck_assessments_type"),
        ("UPDATE assessment_items SET selected_option='X' WHERE id=:iid", "ck_assessment_items_selected"),
        ("UPDATE assessment_items SET correct_option='X' WHERE id=:iid", "ck_assessment_items_correct"),
        ("UPDATE assessment_items SET position=0 WHERE id=:iid", "ck_assessment_items_position"),
        ("UPDATE assessment_items SET skill_id=2147483647 WHERE id=:iid", "fk_assessment_items_skill"),
        ("UPDATE assessment_questions SET code='Invalid'", "ck_assessment_questions_code"),
        ("UPDATE assessment_results SET score=1001 WHERE id=:rid", "ck_assessment_results_score"),
        ("UPDATE assessment_results SET score=-1 WHERE id=:rid", "ck_assessment_results_score"),
        ("UPDATE assessment_results SET confidence=1.001 WHERE id=:rid", "ck_assessment_results_confidence"),
        ("UPDATE assessment_results SET confidence=-0.001 WHERE id=:rid", "ck_assessment_results_confidence"),
        ("UPDATE assessment_results SET correct_count=4 WHERE id=:rid", "ck_assessment_results_counts"),
        ("UPDATE assessment_results SET question_count=0 WHERE id=:rid", "ck_assessment_results_counts"),
        ("INSERT INTO assessment_results(assessment_id,skill_id,score,confidence,correct_count,question_count) VALUES(:aid,:sid,0,0,0,3)", "uq_assessment_results_skill"),
    ]
    for sql, constraint in cases:
        with pytest.raises(IntegrityError) as error:
            with engine.begin() as connection:
                connection.execute(text(sql), dict(uid=uid, sid=sid, aid=aid, iid=iid, rid=rid))
        assert error.value.orig.diag.constraint_name == constraint
    with Session(engine) as session:
        session.get(Assessment, aid).completed_at = datetime.now(timezone.utc)
        session.commit()
        session.add(Assessment(user_id=uid)); session.commit()
    alembic("check")
    engine.dispose()
    alembic("downgrade", "0003_create_onboarding")
    assert not {"assessments", "assessment_items", "assessment_questions", "assessment_results"} & set(inspect(engine).get_table_names())
    with Session(engine) as session:
        assert session.get(User, uid).onboarding_completed
        assert session.get(Skill, sid) is not None
        assert session.query(UserGoal).filter_by(user_id=uid).count() == 1
        assert session.query(UserInterest).filter_by(user_id=uid).count() == 1
    engine.dispose()
    alembic("upgrade", "head")
    alembic("check")
