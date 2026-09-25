"""HTTP do catálogo, com autorização administrativa no backend."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.connection import get_session
from app.modules.challenges.schemas import ChallengeCreate, ChallengeUpdate, ChallengeRead, ChallengeListQuery, ChallengePage
from app.modules.challenges.service import ChallengeService
from app.modules.users.dependencies import get_current_user, require_admin
from app.modules.users.models import User


class EmptyQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")


def no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


router = APIRouter(prefix="/api/v1/challenges", tags=["challenges"], dependencies=[Depends(no_store)])
SessionDep = Annotated[Session, Depends(get_session)]
IdPath = Annotated[int, Path(ge=1, le=2147483647)]


@router.get("", response_model=ChallengePage)
def list_challenges(query: Annotated[ChallengeListQuery, Query()],
                    user: Annotated[User, Depends(get_current_user)], session: SessionDep) -> ChallengePage:
    return ChallengeService(session).list_page(query, user.role)


@router.get("/{id}", response_model=ChallengeRead)
def get_challenge(id: IdPath, query: Annotated[EmptyQuery, Query()],
                  user: Annotated[User, Depends(get_current_user)], session: SessionDep) -> ChallengeRead:
    return ChallengeService(session).get(id, user.role)


@router.post("", response_model=ChallengeRead, status_code=201, dependencies=[Depends(require_admin)])
def create_challenge(data: ChallengeCreate, query: Annotated[EmptyQuery, Query()], session: SessionDep) -> ChallengeRead:
    return ChallengeService(session).create(data)


@router.patch("/{id}", response_model=ChallengeRead, dependencies=[Depends(require_admin)])
def update_challenge(id: IdPath, data: ChallengeUpdate, query: Annotated[EmptyQuery, Query()],
                     session: SessionDep) -> ChallengeRead:
    return ChallengeService(session).update(id, data)
