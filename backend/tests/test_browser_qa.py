"""Falhas do harness não encerram serviços alheios nem deixam banco de QA."""

import os
from types import SimpleNamespace

import pytest
from sqlalchemy import event, text

from scripts import browser_qa as qa


def test_occupied_port_refuses_before_start(monkeypatch):
    class OccupiedSocket:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def bind(self, address): raise OSError('occupied')
    monkeypatch.setattr(qa.socket, 'socket', OccupiedSocket)
    monkeypatch.setattr(qa, 'spawn', lambda *args, **kwargs: pytest.fail('Não iniciar processos'))
    with pytest.raises(qa.QAError, match='4173 ocupada'):
        qa.run(False)


def test_missing_configuration_does_not_connect(monkeypatch):
    monkeypatch.setattr(qa, 'check_ports', lambda: None)
    monkeypatch.setattr(qa.shutil, 'which', lambda _: 'node')
    monkeypatch.setattr(qa.Path, 'is_file', lambda _: True)
    monkeypatch.delenv('CODETRACK_TEST_ADMIN_URL', raising=False)
    monkeypatch.setattr(qa, 'create_engine', lambda *args, **kwargs: pytest.fail('Não conectar'))
    with pytest.raises(qa.QAError, match='Configure CODETRACK_TEST_ADMIN_URL'):
        qa.run(False)


@pytest.mark.parametrize('failure', ['migration', 'readiness'])
def test_failure_removes_only_generated_database(migrated_database, monkeypatch, failure):
    engine, _ = migrated_database
    monkeypatch.setenv('CODETRACK_TEST_ADMIN_URL', engine.url.render_as_string(hide_password=False))
    monkeypatch.setattr(qa, 'check_ports', lambda: None)
    monkeypatch.setattr(qa.shutil, 'which', lambda _: 'node')
    monkeypatch.setattr(qa.Path, 'is_file', lambda _: True)
    before_environment = {key: os.environ.get(key) for key in ('DATABASE_URL', 'JWT_SECRET_KEY', 'ENVIRONMENT', 'CODETRACK_DEBUG')}
    created = []
    original_engine = qa.create_engine
    def engines(*args, **kwargs):
        result = original_engine(*args, **kwargs)
        def record(connection, cursor, statement, parameters, context, executemany):
            if statement.startswith('CREATE DATABASE "codetrack_test_'):
                created.append(statement.split('"')[1])
        event.listen(result, 'before_cursor_execute', record)
        return result
    monkeypatch.setattr(qa, 'create_engine', engines)
    stopped = []
    own_process = object()
    monkeypatch.setattr(qa, 'spawn', lambda *args, **kwargs: own_process)
    monkeypatch.setattr(qa, 'stop', stopped.append)
    if failure == 'migration':
        monkeypatch.setattr(qa.subprocess, 'run', lambda *args, **kwargs: SimpleNamespace(returncode=1))
    else:
        def unavailable(*args): raise qa.QAError('readiness failed')
        monkeypatch.setattr(qa, 'ready', unavailable)
    with pytest.raises(qa.QAError):
        qa.run(False)
    assert len(created) == 1 and created[0] != engine.url.database
    with engine.connect() as connection:
        assert connection.scalar(text('SELECT count(*) FROM pg_database WHERE datname=:name'), {'name': created[0]}) == 0
        assert connection.scalar(text('SELECT current_database()')) == engine.url.database
    assert stopped == ([] if failure == 'migration' else [own_process])
    assert {key: os.environ.get(key) for key in before_environment} == before_environment
