from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, Response
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.study.service import StudyService
from app.modules.study.schemas import StudyCreate, StudyQuery, StudyRead, StudyPage
from pydantic import BaseModel, ConfigDict


class EmptyQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')


def query_and_cache(query: Annotated[EmptyQuery, Query()]) -> None:
    pass


def no_store(response: Response) -> None:
    response.headers['Cache-Control'] = 'no-store'


router = APIRouter(prefix='/api/v1/study', tags=['study'], dependencies=[Depends(get_current_user), Depends(no_store)])
UserDep = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_session)]
Id = Annotated[int, Path(ge=1, le=2147483647)]


@router.get('', response_model=StudyPage)
def list_contents(user: UserDep, session: SessionDep, query: Annotated[StudyQuery, Query()]) -> StudyPage:
    return StudyService(session).list_page(user, query)


@router.post('', response_model=StudyRead, status_code=201, dependencies=[Depends(query_and_cache)])
def create(data: StudyCreate, user: UserDep, session: SessionDep) -> StudyRead:
    return StudyService(session).create(user, data)


@router.get('/{id}', response_model=StudyRead, dependencies=[Depends(query_and_cache)])
def get(id: Id, user: UserDep, session: SessionDep) -> StudyRead:
    return StudyService(session).get(user, id)


@router.put('/{id}/completion', response_model=StudyRead, dependencies=[Depends(query_and_cache)])
def complete(id: Id, user: UserDep, session: SessionDep) -> StudyRead:
    return StudyService(session).complete(user, id)
