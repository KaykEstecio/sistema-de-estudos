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
            order_url = f'/api/v1/study/{cid}/order'
            assert (await client.put(order_url, json={'study_order': 1})).status_code == 401
            assert (await client.put(order_url, headers=student, json={'study_order': 1})).status_code == 403
            for invalid in ({}, {'study_order': True}, {'study_order': 0}, {'study_order': 10001}, {'study_order': '1'}, {'study_order': 1, 'score': 5}):
                assert (await client.put(order_url, headers=admin, json=invalid)).status_code == 422
            initial = (await client.get(f'/api/v1/study?skill_id={skill_id}', headers=student)).json()
            assert initial['has_sequence'] is False and initial['next_content'] is None
            ordered = await client.put(order_url, headers=admin, json={'study_order': 10})
            assert ordered.status_code == 200 and ordered.json()['study_order'] == 10
            assert ordered.headers['cache-control'] == 'no-store'
            assert (await client.put(order_url, headers=admin, json={'study_order': 10})).json() == ordered.json()
            second_content = await client.post('/api/v1/study', headers=admin, json={**payload, 'title': 'Depois da soma'})
            second_cid = second_content.json()['id']
            second_order_url = f'/api/v1/study/{second_cid}/order'
            await client.put(second_order_url, headers=admin, json={'study_order': 10})
            guide_url = f'/api/v1/study?skill_id={skill_id}&limit=1&offset=50'
            guide = (await client.get(guide_url, headers=student)).json()
            assert guide['items'] == [] and guide['has_sequence'] is True
            assert guide['next_content']['id'] == second_cid
            assert (await client.get(guide_url, headers=other)).json()['next_content']['id'] == cid
            ordered_page = (await client.get(f'/api/v1/study?skill_id={skill_id}', headers=student)).json()
            assert [item['id'] for item in ordered_page['items']] == [cid, second_cid]
            unfiltered = (await client.get('/api/v1/study', headers=student)).json()
            assert unfiltered['has_sequence'] is False and unfiltered['next_content'] is None
            assert [item['id'] for item in unfiltered['items']] == [second_cid, cid]
            await client.put(second_order_url, headers=admin, json={'study_order': None})
            guide = (await client.get(guide_url, headers=student)).json()
            assert guide['has_sequence'] is True and guide['next_content'] is None
            assert (await client.put(order_url + '?extra=1', headers=admin, json={'study_order': 1})).status_code == 422
            practice_url = f'/api/v1/study/{cid}/practice'
            assert (await client.get(practice_url, headers=student)).json() is None
            assert (await client.get(practice_url)).status_code == 401
            assert (await client.put(practice_url, headers=student, json={'challenge_id': None})).status_code == 403
            for invalid in ({}, {'challenge_id': True}, {'challenge_id': 0}, {'challenge_id': '1'}, {'challenge_id': None, 'score': 1}):
                assert (await client.put(practice_url, headers=admin, json=invalid)).status_code == 422
            assert (await client.get(practice_url + '?extra=1', headers=admin)).status_code == 422
            challenge_payload = dict(title='Prática', description='Explique a soma.', challenge_type='CODE',
                difficulty='EASY', difficulty_score=100, estimated_minutes=10,
                skills=[{'skill_id': skill_id, 'weight': 100}], is_active=True)
            response = await client.post('/api/v1/challenges', headers=admin, json=challenge_payload)
            assert response.status_code == 201
            challenge_id = response.json()['id']
            selected = await client.put(practice_url, headers=admin, json={'challenge_id': challenge_id})
            assert selected.status_code == 200 and selected.json()['id'] == challenge_id
            assert selected.headers['cache-control'] == 'no-store'
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': challenge_id})).json() == selected.json()
            assert (await client.get(practice_url, headers=student)).json()['id'] == challenge_id
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': 2147483647})).status_code == 409
            assert (await client.get(practice_url, headers=student)).json()['id'] == challenge_id
            await client.patch(f'/api/v1/challenges/{challenge_id}', headers=admin, json={'is_active': False})
            for actor in (student, admin):
                assert (await client.get(practice_url, headers=actor)).json() is None
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': challenge_id})).status_code == 409
            with Session(engine) as session:
                second = Skill(name='SQL', slug='sql', category_id=session.get(Skill, skill_id).category_id)
                session.add(second); session.commit(); second_id = second.id
            await client.patch(f'/api/v1/challenges/{challenge_id}', headers=admin,
                json={'is_active': True, 'skills': [{'skill_id': second_id, 'weight': 100}]})
            assert (await client.get(practice_url, headers=student)).json() is None
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': challenge_id})).status_code == 409
            await client.patch(f'/api/v1/challenges/{challenge_id}', headers=admin,
                json={'skills': [{'skill_id': skill_id, 'weight': 50}, {'skill_id': second_id, 'weight': 50}]})
            with Session(engine) as session:
                session.get(Skill, second_id).is_active = False; session.commit()
            assert (await client.get(practice_url, headers=student)).json() is None
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': challenge_id})).status_code == 409
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': None})).json() is None
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': None})).status_code == 200
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
            assert (await client.put(practice_url, headers=admin, json={'challenge_id': None})).status_code == 403
            assert (await client.get(practice_url, headers=student)).status_code == 404
            assert (await client.put(order_url, headers=admin, json={'study_order': 1})).status_code == 403
            hidden = (await client.get(guide_url, headers=student)).json()
            assert hidden['has_sequence'] is False and hidden['next_content'] is None
    finally:
        app.dependency_overrides.clear()
