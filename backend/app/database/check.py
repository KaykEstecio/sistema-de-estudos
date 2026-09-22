"""Verificação manual de conexão: python -m app.database.check."""

import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def main() -> int:
    """Executa somente leitura e retorna erro sem revelar configuração sensível."""
    try:
        from app.database.connection import SessionLocal, engine

        try:
            with SessionLocal() as session:
                result = session.scalar(text("SELECT 1"))
            if result != 1:
                print("Falha: resposta inesperada do banco.", file=sys.stderr)
                return 1
        finally:
            engine.dispose()
    except (SQLAlchemyError, ValueError, OSError):
        print(
            "Falha na conexão PostgreSQL. Verifique o ambiente, as credenciais "
            "locais e o estado do Docker.",
            file=sys.stderr,
        )
        return 1

    print("Conexão PostgreSQL OK: SELECT 1 retornou 1 via SQLAlchemy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
