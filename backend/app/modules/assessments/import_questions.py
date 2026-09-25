"""CLI local: python -m app.modules.assessments.import_questions arquivo.json."""

import argparse
from pathlib import Path
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import Settings
from app.modules.assessments.schemas import QuestionCreate
from app.modules.assessments.import_service import QuestionImportService, QuestionImportError


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa questões revisadas em transação única.")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    engine = None
    try:
        settings = Settings()
        from app.database.connection import SessionLocal, engine
        if settings.environment != "development" or engine.url.host not in {"localhost", "127.0.0.1", "::1"}:
            print("Importação disponível somente no banco local em development.")
            return 1
        questions = TypeAdapter(list[QuestionCreate]).validate_json(args.file.read_text(encoding="utf-8"))
        with SessionLocal() as session:
            count = QuestionImportService(session).import_questions(questions)
        print(f"Importadas {count} questões.")
        return 0
    except QuestionImportError as exc:
        print(str(exc))
        return 1
    except (OSError, UnicodeError, ValidationError, SQLAlchemyError):
        print("Falha na importação. Verifique arquivo, configuração e banco; nenhuma importação parcial foi salva.")
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
