"""Onboarding do usuário autenticado; sem seleção de terceiros."""

from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.onboarding.schemas import OnboardingCreate, OnboardingUpdate, OnboardingRead
from app.modules.onboarding.service import OnboardingService


class OnboardingQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")


def no_query_parameters(query: Annotated[OnboardingQuery, Query()]) -> None:
    pass


router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"],
                   dependencies=[Depends(get_current_user), Depends(no_query_parameters)])


@router.get("", response_model=OnboardingRead)
def get_onboarding(response: Response, user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]) -> OnboardingRead:
    response.headers["Cache-Control"] = "no-store"
    return OnboardingService(session).get(user.id)


@router.post("", response_model=OnboardingRead, status_code=201)
def create_onboarding(data: OnboardingCreate, response: Response,
                      user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]) -> OnboardingRead:
    response.headers["Cache-Control"] = "no-store"
    return OnboardingService(session).create(user.id, data)


@router.patch("", response_model=OnboardingRead)
def update_onboarding(data: OnboardingUpdate, response: Response,
                      user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]) -> OnboardingRead:
    response.headers["Cache-Control"] = "no-store"
    return OnboardingService(session).update(user.id, data)
