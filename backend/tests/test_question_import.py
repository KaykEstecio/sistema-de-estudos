"""Importação integral, sem sobrescrita e sem gabarito em erros."""

import pytest
import os
import subprocess
import sys
from pathlib import Path
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.assessments.models import AssessmentQuestion
from app.modules.assessments.schemas import QuestionCreate
from app.modules.assessments.import_service import QuestionImportService, QuestionImportError
from app.modules.categories.models import Category
from app.modules.skills.models import Skill


def test_question_import(migrated_database, tmp_path):
    engine, _ = migrated_database
    with Session(engine) as session:
        category = Category(name="Test", slug="test")
        session.add(category); session.flush()
        skill = Skill(name="Test", slug="test", category_id=category.id)
        session.add(skill); session.commit()
        def question(code, skill_id=None):
            return QuestionCreate(code=code, skill_id=skill.id if skill_id is None else skill_id,
                prompt="Synthetic fixture", options={"A": "one", "B": "two", "C": "three", "D": "four"}, correct_option="A")
        service = QuestionImportService(session)
        for batch in ([], [question("same"), question("same")], [question("ok"), question("bad", 2147483647)]):
            with pytest.raises(QuestionImportError):
                service.import_questions(batch)
            assert session.scalar(select(func.count()).select_from(AssessmentQuestion)) == 0
        assert service.import_questions([question("first")]) == 1
        with pytest.raises(QuestionImportError):
            service.import_questions([question("new"), question("first")])
        original = service.repository.create_question
        calls = 0
        def fail(data):
            nonlocal calls
            result = original(data)
            calls += 1
            if calls == 2:
                raise RuntimeError("simulated failure")
            return result
        service.repository.create_question = fail
        with pytest.raises(RuntimeError):
            service.import_questions([question("second"), question("third")])
        assert session.scalar(select(func.count()).select_from(AssessmentQuestion)) == 1
        session.rollback()
        fixture = tmp_path / "questions.json"
        fixture.write_text("[" + question("cli-question").model_dump_json() + "]", encoding="utf-8")
        environment = dict(os.environ, DATABASE_URL=engine.url.render_as_string(hide_password=False), ENVIRONMENT="development")
        command = [sys.executable, "-m", "app.modules.assessments.import_questions", str(fixture)]
        for expected in (0, 1):
            result = subprocess.run(command, cwd=Path(__file__).resolve().parents[1], env=environment,
                                    capture_output=True, text=True)
            assert result.returncode == expected
            assert "correct_option" not in result.stdout and "Traceback" not in result.stderr
