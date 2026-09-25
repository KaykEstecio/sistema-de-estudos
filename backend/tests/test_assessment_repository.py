"""Persistência, seleção e rollback do diagnóstico em PostgreSQL isolado."""

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.schemas import QuestionCreate
from app.modules.assessments.models import AssessmentResult
from app.modules.users.models import User
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.onboarding.models import UserInterest


def test_assessment_repository(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        user = User(name="User", email="repo-assessment@example.com", password_hash="test")
        other = User(name="Other", email="other-assessment@example.com", password_hash="test")
        category = Category(name="Logic", slug="logic")
        session.add_all([user, other, category]); session.flush()
        skill = Skill(name="Logic", slug="logic", category_id=category.id)
        inactive = Skill(name="Inactive", slug="inactive", category_id=category.id, is_active=False)
        session.add_all([skill, inactive]); session.flush()
        session.add(UserInterest(user_id=user.id, category_id=category.id))
        session.commit()
        uid, oid, sid = user.id, other.id, skill.id
        repository = AssessmentRepository(session)
        assert repository.get_user_locked(uid) is user
        assert repository.eligible_skill_ids(uid, [sid, inactive.id]) == {sid}
        assert repository.eligible_skill_ids(oid, [sid]) == set()
        assert repository.get_questions(sid, limit=3) == []
        for index in range(4):
            repository.create_question(QuestionCreate(code=f"q-{index}", skill_id=sid, prompt=f"Question {index}",
                options={"A": "one", "B": "two", "C": "three", "D": "four"}, correct_option="A", is_active=index != 0))
        session.commit()
        questions = repository.get_questions(sid, limit=2)
        assert [question.code for question in questions] == ["q-1", "q-2"]
        assessment = repository.create(uid, questions)
        aid = assessment.id
        session.rollback()
        assert repository.get_open(uid) is None
        assert repository.get_items(aid) == []
        assessment = repository.create(uid, repository.get_questions(sid, limit=3))
        session.commit()
        aid = assessment.id
        assert repository.get_owned_locked(aid, oid) is None
        assert repository.get_owned_locked(aid, uid, read=True) is assessment
        assert repository.get_open(uid).id == aid
        items = repository.get_items(aid)
        assert [item.position for item in items] == [1, 2, 3]
        assert repository.get_item(aid + 1, items[0].id) is None
        repository.save_answer(items[0], "B")
        session.rollback()
        assert repository.get_items(aid)[0].selected_option is None
        repository.save_answer(items[0], "A")
        session.commit()
        result = AssessmentResult(assessment_id=aid, skill_id=sid, score=333, confidence=Decimal("0"), correct_count=1, question_count=3)
        repository.finish(assessment, [result], datetime.now(timezone.utc))
        session.rollback()
        assert repository.get_results(aid) == [] and repository.get_open(uid) is not None
    with Session(engine) as session:
        repository = AssessmentRepository(session)
        assert repository.get_items(aid)[0].selected_option == "A"
