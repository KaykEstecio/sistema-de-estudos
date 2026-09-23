"""Banco PostgreSQL descartável compartilhado pelos testes de integração."""

import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

@pytest.fixture
def migrated_database():
    admin_url = os.environ.get("CODETRACK_TEST_ADMIN_URL")
    if not admin_url:
        pytest.skip("Defina CODETRACK_TEST_ADMIN_URL para testar em PostgreSQL isolado.")

    database_name = "codetrack_test_" + uuid4().hex
    admin = create_engine(admin_url, isolation_level="AUTOCOMMIT", hide_parameters=True)
    url = make_url(admin_url).set(database=database_name)
    engine = create_engine(url, hide_parameters=True)
    created = False
    backend = Path(__file__).resolve().parents[1]
    environment = dict(os.environ, DATABASE_URL=url.render_as_string(hide_password=False))

    def alembic(*args: str) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", str(backend / "alembic.ini"), *args],
            cwd=backend, env=environment, capture_output=True, text=True,
        )
        # Não incluir saída que possa conter configuração sensível no relatório.
        assert result.returncode == 0, f"Alembic {' '.join(args)} falhou."

    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        created = True
        alembic("upgrade", "head")
        yield engine, alembic
    finally:
        engine.dispose()
        if created:
            # Nome gerado internamente; nunca remove um banco previamente existente.
            with admin.connect() as connection:
                connection.execute(text(f'DROP DATABASE "{database_name}"'))
        admin.dispose()
