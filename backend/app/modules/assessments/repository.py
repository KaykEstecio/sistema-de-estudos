"""Persistência do diagnóstico; sem decisão de acesso, avaliação ou commit."""

from collections.abc import Sequence
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.assessments.models import Assessment, AssessmentQuestion, AssessmentItem, AssessmentResult
from app.modules.assessments.schemas import QuestionCreate, Option
from app.modules.users.models import User
from app.modules.skills.models import Skill
from app.modules.onboarding.models import UserInterest


class AssessmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_locked(self, user_id: int) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id).with_for_update()
                                   .execution_options(populate_existing=True))

    def get_open(self, user_id: int) -> Assessment | None:
        return self.session.scalar(select(Assessment).where(Assessment.user_id == user_id, Assessment.completed_at.is_(None)))

    def get_owned_locked(self, assessment_id: int, user_id: int, *, read: bool = False) -> Assessment | None:
        return self.session.scalar(select(Assessment).where(Assessment.id == assessment_id, Assessment.user_id == user_id)
                                   .with_for_update(read=read).execution_options(populate_existing=True))

    def eligible_skill_ids(self, user_id: int, skill_ids: list[int]) -> set[int]:
        return set(self.session.scalars(select(Skill.id).join(UserInterest, UserInterest.category_id == Skill.category_id)
            .where(UserInterest.user_id == user_id, Skill.id.in_(skill_ids), Skill.is_active.is_(True))))

    def get_questions(self, skill_id: int, *, limit: int) -> list[AssessmentQuestion]:
        return list(self.session.scalars(select(AssessmentQuestion).where(AssessmentQuestion.skill_id == skill_id,
            AssessmentQuestion.is_active.is_(True)).order_by(AssessmentQuestion.id).limit(limit)))

    def create_question(self, data: QuestionCreate) -> AssessmentQuestion:
        question = AssessmentQuestion(**data.model_dump())
        self.session.add(question)
        self.session.flush()
        return question

    def existing_skill_ids(self, ids: set[int]) -> set[int]:
        return set(self.session.scalars(select(Skill.id).where(Skill.id.in_(ids))))

    def existing_question_codes(self, codes: set[str]) -> set[str]:
        return set(self.session.scalars(select(AssessmentQuestion.code).where(AssessmentQuestion.code.in_(codes))))

    def create(self, user_id: int, questions: Sequence[AssessmentQuestion]) -> Assessment:
        assessment = Assessment(user_id=user_id)
        self.session.add(assessment)
        self.session.flush()
        for position, question in enumerate(questions, start=1):
            self.session.add(AssessmentItem(assessment_id=assessment.id, skill_id=question.skill_id,
                position=position, prompt=question.prompt, options=dict(question.options), correct_option=question.correct_option))
        self.session.flush()
        return assessment

    def get_items(self, assessment_id: int) -> list[AssessmentItem]:
        return list(self.session.scalars(select(AssessmentItem).where(AssessmentItem.assessment_id == assessment_id)
                    .order_by(AssessmentItem.position).execution_options(populate_existing=True)))

    def get_item(self, assessment_id: int, item_id: int) -> AssessmentItem | None:
        return self.session.scalar(select(AssessmentItem).where(AssessmentItem.assessment_id == assessment_id, AssessmentItem.id == item_id))

    def save_answer(self, item: AssessmentItem, selected_option: Option) -> None:
        item.selected_option = selected_option
        self.session.flush()

    def get_results(self, assessment_id: int) -> list[AssessmentResult]:
        return list(self.session.scalars(select(AssessmentResult).where(AssessmentResult.assessment_id == assessment_id)
                                        .order_by(AssessmentResult.skill_id)))

    def finish(self, assessment: Assessment, results: Sequence[AssessmentResult], completed_at: datetime) -> None:
        self.session.add_all(results)
        assessment.completed_at = completed_at
        self.session.flush()
