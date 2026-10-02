"""Contratos de execução pytest, sem dados pessoais nem banco de desenvolvimento."""

from pathlib import Path

import pytest


@pytest.fixture
def quality_runner(pytester, monkeypatch):
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    monkeypatch.delenv("CODETRACK_TEST_ADMIN_URL", raising=False)
    source = Path(__file__).with_name("conftest.py").read_text(encoding="utf-8")
    pytester.makeconftest(source)
    return pytester


def test_fast_deselects_transitive_database_fixture(quality_runner):
    quality_runner.makepyfile('''
import pytest
@pytest.fixture
def context(migrated_database):
    raise AssertionError("Não pode preparar banco no modo fast")
def test_database(context):
    assert False
def test_pure():
    assert True
''')
    result = quality_runner.runpytest_subprocess("--quality-mode=fast", "-q")
    result.assert_outcomes(passed=1, deselected=1)
    assert result.ret == pytest.ExitCode.OK


def test_complete_requires_configuration(quality_runner):
    quality_runner.makepyfile("def test_not_run(): assert False")
    result = quality_runner.runpytest_subprocess("--quality-mode=complete", "-q")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "exige CODETRACK_TEST_ADMIN_URL" in result.stderr.str()
    assert "test_not_run" not in result.stdout.str()


@pytest.mark.parametrize("url", ["not-a-url-secret-sentinel", "sqlite:///secret-sentinel", "postgresql+psycopg://user:secret-sentinel@127.0.0.1:1/test"])
def test_complete_rejects_bad_or_unavailable_database(quality_runner, monkeypatch, url):
    monkeypatch.setenv("CODETRACK_TEST_ADMIN_URL", url)
    quality_runner.makepyfile("def test_not_run(): assert False")
    result = quality_runner.runpytest_subprocess("--quality-mode=complete", "-q")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "banco indisponível" in result.stderr.str()
    output = result.stdout.str() + result.stderr.str()
    assert "secret-sentinel" not in output and "Traceback" not in output


@pytest.mark.parametrize("skip_source", [
    "import pytest\ndef test_skip(): pytest.skip('intentional')",
    "import pytest\npytest.skip('collection skipped', allow_module_level=True)",
])
def test_complete_fails_on_skip(quality_runner, skip_source):
    # Preflight is tested separately; this isolates pytest's exit-code handling.
    quality_runner.makeconftest(Path(__file__).with_name("conftest.py").read_text(encoding="utf-8")
                               + "\ndef verify_quality_database(): pass\n")
    quality_runner.makepyfile(test_skipped=skip_source, test_passed="def test_pass(): assert True")
    result = quality_runner.runpytest_subprocess("--quality-mode=complete", "-q")
    result.assert_outcomes(passed=1, skipped=1)
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    assert "Modo complete reprovado" in result.stdout.str()


def test_legacy_mode_keeps_optional_integration(quality_runner):
    quality_runner.makepyfile("def test_database(migrated_database): assert False\ndef test_pure(): assert True")
    result = quality_runner.runpytest_subprocess("-q")
    result.assert_outcomes(passed=1, skipped=1)
    assert result.ret == pytest.ExitCode.OK
