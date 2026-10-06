"""Revisão administrativa separada da consulta exclusiva do dono."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.evaluation.schemas import EvaluationCreate, EvaluationRead, ReviewRead, ReviewPage
from app.modules.attempts.schemas import AttemptQuery
from app.modules.evaluation.service import EvaluationService


class EmptyQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")


def query_and_cache(response: Response, query: Annotated[EmptyQuery, Query()]) -> None:
    response.headers["Cache-Control"] = "no-store"


router = APIRouter(prefix="/api/v1", tags=["evaluation"], dependencies=[Depends(get_current_user)])
UserDep = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_session)]
IdPath = Annotated[int, Path(ge=1, le=2147483647)]


@router.get("/reviews/attempts", response_model=ReviewPage)
def pending(query: Annotated[AttemptQuery, Query()], user: UserDep, session: SessionDep, response: Response) -> ReviewPage:
    response.headers["Cache-Control"] = "no-store"
    return EvaluationService(session).list_pending(user.id, query.limit, query.offset)


@router.get("/reviews/attempts/{id}", response_model=ReviewRead, dependencies=[Depends(query_and_cache)])
def review(id: IdPath, user: UserDep, session: SessionDep) -> ReviewRead:
    return EvaluationService(session).review(user.id, id)


@router.post("/reviews/attempts/{id}/evaluation", response_model=EvaluationRead, status_code=201,
             responses={200: {"model": EvaluationRead}}, dependencies=[Depends(query_and_cache)])
def evaluate(id: IdPath, data: EvaluationCreate, user: UserDep, session: SessionDep, response: Response) -> EvaluationRead:
    result, created = EvaluationService(session).evaluate(user.id, id, data)
    response.status_code = 201 if created else 200
    return result


@router.get("/attempts/{id}/evaluation", response_model=EvaluationRead, dependencies=[Depends(query_and_cache)])
def get_owned(id: IdPath, user: UserDep, session: SessionDep) -> EvaluationRead:
    return EvaluationService(session).get_owned(user.id, id)
