"""Leitura é privada por conta e não gera evidências de desempenho."""
import secrets
import httpx
import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.config import JWTSettings
from app.core.tokens import create_access_token
from app.modules.users.models import User, UserRole
from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill, SkillEvidence
from app.modules.study.models import StudyCompletion


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_study_access_and_completion(migrated_database, monkeypatch):
    engine, alembic = migrated_database
    alembic('check')
    with Session(engine) as session:
        users = [User(name='Study test', email=f'study{i}@example.com', password_hash='unused', role=role)
                 for i, role in enumerate([UserRole.ADMIN, UserRole.STUDENT, UserRole.STUDENT])]
        category = Category(name='Study', slug='study')
        session.add_all([category, *users]); session.flush()
        skill = Skill(name='Python', slug='python', category_id=category.id)
        session.add(skill); session.commit()
        ids = [user.id for user in users]; skill_id = skill.id
    monkeypatch.setenv('DATABASE_URL', 'postgresql+psycopg://localhost:1/test')
    from app.main import app
    from app.database.connection import get_session
    from app.modules.users.dependencies import get_jwt_settings
    settings = JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))
    def sessions():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = sessions
    app.dependency_overrides[get_jwt_settings] = lambda: settings
    admin, student, other = [{'Authorization': 'Bearer ' + create_access_token(id, settings)} for id in ids]
    payload = dict(skill_id=skill_id, title='Soma', explanation='<b>Texto literal</b>',
                   code_example='  print(1 + 1)\n', common_mistakes='Não confundir soma com concatenação.')
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            assert (await client.get('/api/v1/study')).status_code == 401
            assert (await client.post('/api/v1/study', headers=student, json=payload)).status_code == 403
            for changes in ({'skill_id': True}, {'score': 999}, {'title': ' '}, {'code_example': ' \n '}, {'common_mistakes': 'x' * 6001}):
                assert (await client.post('/api/v1/study', headers=admin, json={**payload, **changes})).status_code == 422
            created = await client.post('/api/v1/study', headers=admin, json=payload)
            assert created.status_code == 201 and created.headers['cache-control'] == 'no-store'
            content = created.json(); cid = content['id']
            assert content['code_example'] == payload['code_example']
            assert content['completed_at'] is None
            page = (await client.get(f'/api/v1/study?skill_id={skill_id}', headers=student)).json()
            assert page['total'] == 1 and page['items'][0]['id'] == cid
            assert 'explanation' not in page['items'][0]
            assert (await client.get('/api/v1/study?offset=10', headers=student)).json()['items'] == []
            for query in ('limit=0', 'limit=51', 'offset=-1', 'user_id=1'):
                assert (await client.get('/api/v1/study?' + query, headers=student)).status_code == 422
            first = await client.put(f'/api/v1/study/{cid}/completion', headers=student)
            assert first.status_code == 200 and first.json()['completed_at'] is not None
            repeated = await client.put(f'/api/v1/study/{cid}/completion', headers=student)
            assert repeated.json() == first.json()
            assert (await client.get(f'/api/v1/study/{cid}', headers=other)).json()['completed_at'] is None
            assert (await client.get('/api/v1/study', headers=other)).json()['items'][0]['completed_at'] is None
            assert (await client.get(f'/api/v1/study/{cid}?user_id={ids[1]}', headers=other)).status_code == 422
            assert (await client.put('/api/v1/study/2147483647/completion', headers=student)).status_code == 404
            with Session(engine) as session:
                assert session.scalar(select(func.count()).select_from(StudyCompletion)) == 1
                assert session.scalar(select(func.count()).select_from(UserSkill)) == 0
                assert session.scalar(select(func.count()).select_from(SkillEvidence)) == 0
                session.get(Skill, skill_id).is_active = False
                session.get(User, ids[0]).role = UserRole.STUDENT
                session.commit()
            assert (await client.get('/api/v1/study', headers=student)).json()['total'] == 0
            assert (await client.get(f'/api/v1/study/{cid}', headers=student)).status_code == 404
            assert (await client.put(f'/api/v1/study/{cid}/completion', headers=other)).status_code == 404
            assert (await client.post('/api/v1/study', headers=admin, json=payload)).status_code == 403
    finally:
        app.dependency_overrides.clear()
