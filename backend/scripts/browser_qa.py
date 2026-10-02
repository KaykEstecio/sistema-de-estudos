"""Jornada Playwright em serviços próprios e PostgreSQL descartável."""

import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))


class QAError(Exception):
    """Mensagem de configuração segura, sem dados do ambiente."""


def check_ports() -> None:
    for port in (4173, 8100):
        with socket.socket() as listener:
            try:
                listener.bind(('127.0.0.1', port))
            except OSError:
                raise QAError(f'Porta de QA {port} ocupada. Encerre seu serviço ou libere a porta.') from None


def spawn(command: list[str], environment: dict[str, str], *, quiet: bool = True, cwd: Path = ROOT) -> subprocess.Popen:
    options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
    return subprocess.Popen(command, cwd=cwd, env=environment,
                            stdout=subprocess.DEVNULL if quiet else None, stderr=subprocess.DEVNULL if quiet else None, **options)


def stop(process: subprocess.Popen) -> None:
    if os.name == 'nt':
        if process.poll() is None:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=15)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            if os.name != 'nt':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait(timeout=5)


def ready(url: str, process: subprocess.Popen) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise QAError('Serviço de QA não iniciou. Confira dependências e portas.')
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(.2)
    raise QAError('Timeout ao aguardar serviço de QA.')


def seed(engine, password: str) -> tuple[int, int]:
    # Importar main registra todos os models referenciados por FKs.
    from app.main import app  # noqa: F401
    from sqlalchemy.orm import Session
    from app.core.security import hash_password
    from app.modules.users.models import User, UserRole
    from app.modules.categories.models import Category
    from app.modules.skills.models import Skill
    from app.modules.onboarding.models import UserInterest
    from app.modules.challenges.models import Challenge, ChallengeSkill
    with Session(engine) as session:
        users = [User(name='QA ' + label, email=label + '@qa.example', password_hash=hash_password(password),
                      role=UserRole.ADMIN if label == 'reviewer' else UserRole.STUDENT,
                      onboarding_completed=True, declared_experience='BEGINNER') for label in ('owner', 'reviewer', 'other')]
        category = Category(name='Programming', slug='programming')
        session.add_all([*users, category]); session.flush()
        skill = Skill(name='Python', slug='python', category_id=category.id)
        session.add(skill); session.flush()
        session.add(UserInterest(user_id=users[0].id, category_id=category.id))
        challenge = Challenge(title='First practice', description='Explain addition. <b>Literal text</b>', challenge_type='CODE',
                              difficulty='EASY', difficulty_score=100, estimated_minutes=15, is_active=True, starter_code='print(1 + 1)')
        session.add(challenge); session.flush()
        session.add(ChallengeSkill(challenge_id=challenge.id, skill_id=skill.id, weight=100))
        session.commit()
        return challenge.id, skill.id


def run(local_env: bool) -> int:
    check_ports()
    if not shutil.which('node') or any(not path.is_file() for path in (
            ROOT/'frontend/node_modules/vite/bin/vite.js', ROOT/'frontend/node_modules/@playwright/test/cli.js')):
        raise QAError('Dependências de QA ausentes. Execute npm --prefix frontend ci e instale Chromium pelo Playwright.')
    admin_url = os.environ.get('CODETRACK_TEST_ADMIN_URL')
    if not admin_url and local_env:
        from dotenv import dotenv_values
        admin_url = dotenv_values(ROOT / 'backend/.env').get('DATABASE_URL')
    if not admin_url:
        raise QAError('Configure CODETRACK_TEST_ADMIN_URL ou use --local-env para ler backend/.env explicitamente.')
    try:
        url = make_url(admin_url)
        if url.drivername != 'postgresql+psycopg':
            raise ValueError()
    except Exception:
        raise QAError('URL administrativa PostgreSQL inválida.') from None
    name = 'codetrack_test_' + uuid4().hex
    admin = create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True, connect_args={'connect_timeout': 5})
    database_url = url.set(database=name)
    created = False
    engine = None
    processes: list[subprocess.Popen] = []
    changed_keys = ('DATABASE_URL', 'JWT_SECRET_KEY', 'ENVIRONMENT', 'CODETRACK_DEBUG')
    previous_environment = {key: os.environ.get(key) for key in changed_keys}
    try:
        try:
            with admin.connect() as connection:
                connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        except Exception:
            raise QAError('Banco de testes indisponível ou sem permissão para criar banco descartável.') from None
        environment = dict(os.environ, DATABASE_URL=database_url.render_as_string(hide_password=False), JWT_SECRET_KEY=secrets.token_urlsafe(48),
                           ENVIRONMENT='test', CODETRACK_DEBUG='false', CODETRACK_QA_API_PROXY='http://127.0.0.1:8100', CODETRACK_QA_SERVER_STARTED='1')
        migration = subprocess.run([sys.executable, '-m', 'alembic', '-c', str(ROOT/'backend/alembic.ini'), 'upgrade', 'head'],
                                   cwd=ROOT/'backend', env=environment, capture_output=True, timeout=60)
        if migration.returncode:
            raise QAError('Migration do banco descartável falhou.')
        os.environ.update({key: environment[key] for key in ('DATABASE_URL', 'JWT_SECRET_KEY', 'ENVIRONMENT', 'CODETRACK_DEBUG')})
        password = secrets.token_urlsafe(24)
        engine = create_engine(database_url, hide_parameters=True)
        challenge_id, skill_id = seed(engine, password)
        environment.update(QA_PASSWORD=password, QA_CHALLENGE_ID=str(challenge_id), QA_SKILL_ID=str(skill_id), CODETRACK_QA_DISPOSABLE='1')
        api = spawn([sys.executable, '-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', '8100'], environment)
        processes.append(api); ready('http://127.0.0.1:8100/health', api)
        frontend = spawn(['node', str(ROOT/'frontend/node_modules/vite/bin/vite.js'), '--host', '127.0.0.1', '--port', '4173', '--strictPort'], environment, cwd=ROOT/'frontend')
        processes.append(frontend)
        ready('http://127.0.0.1:4173', frontend)
        typing = subprocess.run(['node', str(ROOT/'frontend/node_modules/typescript/bin/tsc'), '--noEmit', '-p',
                                 str(ROOT/'frontend/tsconfig.e2e.json')], cwd=ROOT, env=environment, capture_output=True, timeout=30)
        if typing.returncode:
            raise QAError('Tipagem dos testes falhou. Execute npm --prefix frontend run typecheck:e2e para detalhes.')
        runner = spawn(['node', str(ROOT/'frontend/node_modules/@playwright/test/cli.js'), 'test', '--config', str(ROOT/'frontend/playwright.config.ts')], environment)
        processes.append(runner)
        code = runner.wait(timeout=180)
        report = ROOT/'frontend/test-results/results.json'
        if code == 0:
            stats = json.loads(report.read_text(encoding='utf-8'))['stats']
            if stats['skipped'] or stats['unexpected'] or not stats['expected']:
                raise QAError('Relatório de QA contém skips/falhas ou nenhum teste aprovado.')
            print(f"Playwright: {stats['expected']} testes aprovados, nenhum skip/falha.")
        else:
            print('Playwright reprovado. Consulte o relatório local ignorado em frontend/test-results/results.json.')
        return code
    finally:
        cleanup_failed = False
        for process in reversed(processes):
            try:
                stop(process)
            except Exception:
                cleanup_failed = True
        if engine is not None:
            try:
                engine.dispose()
            except Exception:
                cleanup_failed = True
        if created:
            try:
                with admin.connect() as connection:
                    connection.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
            except Exception:
                cleanup_failed = True
        admin.dispose()
        for key, value in previous_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        if cleanup_failed:
            raise QAError('Cleanup incompleto: verifique processos de QA e bancos codetrack_test_*. Nenhum banco local deve ser removido.') from None
        if created:
            print('Cleanup confirmado: serviços próprios encerrados e banco descartável removido.')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-env', action='store_true', help='Ler a URL administrativa de backend/.env explicitamente.')
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.local_env))
    except KeyboardInterrupt:
        print('QA interrompido; cleanup executado.', file=sys.stderr)
        raise SystemExit(130)
    except QAError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
    except Exception:
        # Não expor exceptions SQLAlchemy, payloads ou environment em falhas.
        print('QA falhou. Confira PostgreSQL, portas 4173/8100 e dependências npm/Chromium.', file=sys.stderr)
        raise SystemExit(1)
