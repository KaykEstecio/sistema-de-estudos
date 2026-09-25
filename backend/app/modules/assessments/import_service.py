"""Importação transacional de questões novas, sem alteração de conteúdo existente."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.assessments.repository import AssessmentRepository
from app.modules.assessments.schemas import QuestionCreate


class QuestionImportError(Exception):
    pass


class QuestionImportService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AssessmentRepository(session)

    def import_questions(self, questions: list[QuestionCreate]) -> int:
        try:
            codes = {question.code for question in questions}
            if not questions or len(codes) != len(questions):
                raise QuestionImportError("Lote vazio ou códigos repetidos.")
            if self.repository.existing_question_codes(codes):
                raise QuestionImportError("Código de questão já cadastrado.")
            skill_ids = {question.skill_id for question in questions}
            if self.repository.existing_skill_ids(skill_ids) != skill_ids:
                raise QuestionImportError("Skill não encontrada.")
            for question in questions:
                self.repository.create_question(question)
            self.session.commit()
            return len(questions)
        except IntegrityError as exc:
            self.session.rollback()
            constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            if constraint in {"uq_assessment_questions_code", "fk_assessment_questions_skill"}:
                raise QuestionImportError("Código duplicado ou skill indisponível; lote revertido.") from None
            raise
        except Exception:
            self.session.rollback()
            raise
