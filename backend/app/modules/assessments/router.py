"""Início, consulta e respostas do diagnóstico autenticado."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Response, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.assessments.schemas import AssessmentCreate, AssessmentRead, AssessmentItemRead, AnswerCreate
from app.modules.assessments.service import AssessmentService


class AssessmentQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")


def query_and_cache(response: Response, query: Annotated[AssessmentQuery, Query()]) -> None:
    response.headers["Cache-Control"] = "no-store"


router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"],
    dependencies=[Depends(get_current_user), Depends(query_and_cache)])


@router.post("", response_model=AssessmentRead, status_code=201)
def create(data: AssessmentCreate, user: Annotated[User, Depends(get_current_user)],
           session: Annotated[Session, Depends(get_session)]) -> AssessmentRead:
    return AssessmentService(session).create(user.id, data)


@router.get("/{id}", response_model=AssessmentRead)
def get(id: Annotated[int, Path(ge=1, le=2147483647)], user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]) -> AssessmentRead:
    return AssessmentService(session).get(user.id, id)


@router.post("/{id}/answers", response_model=AssessmentItemRead)
def answer(id: Annotated[int, Path(ge=1, le=2147483647)], data: AnswerCreate,
           user: Annotated[User, Depends(get_current_user)],
           session: Annotated[Session, Depends(get_session)]) -> AssessmentItemRead:
    return AssessmentService(session).answer(user.id, id, data)


async def empty_body(request: Request) -> None:
    if await request.body():
        raise RequestValidationError([{"loc": ("body",), "type": "extra_forbidden", "msg": "Corpo não permitido."}])


@router.post("/{id}/finish", response_model=AssessmentRead, dependencies=[Depends(empty_body)])
def finish(id: Annotated[int, Path(ge=1, le=2147483647)], user: Annotated[User, Depends(get_current_user)],
           session: Annotated[Session, Depends(get_session)]) -> AssessmentRead:
    return AssessmentService(session).finish(user.id, id)
