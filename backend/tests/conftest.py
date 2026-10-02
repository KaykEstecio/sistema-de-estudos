"""Banco PostgreSQL descartável compartilhado pelos testes de integração."""

import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

pytest_plugins = ("pytester",)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--quality-mode", choices=("fast", "complete"), default=None,
                     help="fast: sem PostgreSQL; complete: banco obrigatório e nenhum skip.")


def verify_quality_database() -> None:
    admin_url = os.environ.get("CODETRACK_TEST_ADMIN_URL")
    if not admin_url:
        raise pytest.UsageError("Modo complete exige CODETRACK_TEST_ADMIN_URL. Configure o PostgreSQL de testes.")
    engine = None
    try:
        url = make_url(admin_url)
        if url.drivername != "postgresql+psycopg":
            raise ValueError("Driver inválido")
        engine = create_engine(url, hide_parameters=True,
                               connect_args={"connect_timeout": 5, "options": "-c statement_timeout=5000"})
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        raise pytest.UsageError("Modo complete: configuração PostgreSQL inválida ou banco indisponível. "
                                "Confira CODETRACK_TEST_ADMIN_URL e inicie o banco de testes.") from None
    finally:
        if engine is not None:
            engine.dispose()


class QualityChecks:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.skipped = False

    def pytest_sessionstart(self, session: pytest.Session) -> None:
        if self.mode == "complete":
            verify_quality_database()

    def pytest_collection_modifyitems(self, config: pytest.Config, items: list[pytest.Item]) -> None:
        if self.mode != "fast":
            return
        database_items = [item for item in items if "migrated_database" in getattr(item, "fixturenames", ())]
        items[:] = [item for item in items if item not in database_items]
        config.hook.pytest_deselected(items=database_items)

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        self.skipped |= report.skipped

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        self.skipped |= report.skipped

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        if self.mode == "complete" and self.skipped and exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED

    def pytest_terminal_summary(self, terminalreporter):
        if self.mode == "complete" and self.skipped:
            terminalreporter.write_sep("=", "Modo complete reprovado: existem testes skipped.")


def pytest_configure(config: pytest.Config) -> None:
    mode = config.getoption("quality_mode")
    if mode is not None:
        config.pluginmanager.register(QualityChecks(mode), "codetrack-quality")

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
