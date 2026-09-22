"""Regressões de configuração; executáveis com unittest e pytest."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from app.core.config import Settings


class DebugSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        environment = patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql+psycopg://localhost/codetrack"},
            clear=True,
        )
        environment.start()
        self.addCleanup(environment.stop)

    def test_external_debug_does_not_override_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("CODETRACK_DEBUG=false\n", encoding="utf-8")
            with patch.dict(os.environ, {"DEBUG": "external-tool:*"}):
                self.assertFalse(Settings(_env_file=env_file).debug)

    def test_project_variable_overrides_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("CODETRACK_DEBUG=false\n", encoding="utf-8")
            with patch.dict(os.environ, {"CODETRACK_DEBUG": "true"}):
                self.assertTrue(Settings(_env_file=env_file).debug)

    def test_debug_defaults_to_false(self) -> None:
        self.assertFalse(Settings(_env_file=None).debug)

    def test_invalid_project_debug_is_rejected(self) -> None:
        with patch.dict(os.environ, {"CODETRACK_DEBUG": "invalid"}):
            with self.assertRaises(ValidationError):
                Settings(_env_file=None)

    def test_debug_is_rejected_in_production(self) -> None:
        with patch.dict(
            os.environ, {"ENVIRONMENT": "production", "CODETRACK_DEBUG": "true"}
        ):
            with self.assertRaises(ValidationError):
                Settings(_env_file=None)

    def test_production_allows_debug_disabled(self) -> None:
        with patch.dict(
            os.environ, {"ENVIRONMENT": "production", "CODETRACK_DEBUG": "false"}
        ):
            self.assertFalse(Settings(_env_file=None).debug)
