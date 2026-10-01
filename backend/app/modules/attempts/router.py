"""Rotas autenticadas do ciclo de vida de tentativas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.connection import get_session
from app.modules.attempts.schemas import AttemptDraft, AttemptRead, AttemptPage, AttemptQuery
from app.modules.attempts.service import AttemptService
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User


class EmptyQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")


def cache(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


def empty_query(query: Annotated[EmptyQuery, Query()]) -> None:
    pass


async def empty_body(request: Request) -> None:
    if await request.body():
        raise RequestValidationError([{"loc": ("body",), "type": "extra_forbidden", "msg": "Corpo não permitido."}])


router = APIRouter(prefix="/api/v1", tags=["attempts"],
                   dependencies=[Depends(get_current_user), Depends(cache)])
UserDep = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_session)]
IdPath = Annotated[int, Path(ge=1, le=2147483647)]


@router.get("/attempts", response_model=AttemptPage)
def list_owned(query: Annotated[AttemptQuery, Query()], user: UserDep, session: SessionDep) -> AttemptPage:
    return AttemptService(session).list_owned(user.id, query)


@router.post("/challenges/{id}/attempts", response_model=AttemptRead, status_code=201,
             responses={200: {"model": AttemptRead}}, dependencies=[Depends(empty_body), Depends(empty_query)])
def start(id: IdPath, user: UserDep, session: SessionDep, response: Response) -> AttemptRead:
    result, created = AttemptService(session).start(user.id, id)
    response.status_code = 201 if created else 200
    return result


@router.get("/attempts/{id}", response_model=AttemptRead, dependencies=[Depends(empty_query)])
def get(id: IdPath, user: UserDep, session: SessionDep) -> AttemptRead:
    return AttemptService(session).get(user.id, id)


@router.patch("/attempts/{id}", response_model=AttemptRead, dependencies=[Depends(empty_query)])
def save(id: IdPath, data: AttemptDraft, user: UserDep, session: SessionDep) -> AttemptRead:
    return AttemptService(session).save_draft(user.id, id, data)


@router.post("/attempts/{id}/submit", response_model=AttemptRead, dependencies=[Depends(empty_body), Depends(empty_query)])
def submit(id: IdPath, user: UserDep, session: SessionDep) -> AttemptRead:
    return AttemptService(session).submit(user.id, id)
