"""Consulta autenticada de competências."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.auth_service import PermissionDenied
from app.modules.skills.schemas import SkillListQuery, SkillPage, SkillRead
from app.modules.skills.service import SkillNotFound, SkillService

from app.modules.users.dependencies import require_admin
from app.modules.skills.schemas import SkillCreate, SkillUpdate

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])



@router.post("", response_model=SkillRead, status_code=201, dependencies=[Depends(require_admin)])
def create_skill(data: SkillCreate, session: Annotated[Session, Depends(get_session)]) -> SkillRead:
    return SkillService(session).create(data)


@router.patch("/{id}", response_model=SkillRead, dependencies=[Depends(require_admin)])
def update_skill(id: Annotated[int, Path(ge=1, le=2147483647)], data: SkillUpdate,
                 session: Annotated[Session, Depends(get_session)]) -> SkillRead:
    return SkillService(session).update(id, data)


@router.get("", response_model=SkillPage)
def list_skills(query: Annotated[SkillListQuery, Query()],
                user: Annotated[User, Depends(get_current_user)],
                session: Annotated[Session, Depends(get_session)]) -> SkillPage:
    try:
        return SkillService(session).list_page(query, user.role)
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permissão insuficiente.") from None


@router.get("/{id}", response_model=SkillRead)
def get_skill(id: Annotated[int, Path(ge=1, le=2147483647)],
              user: Annotated[User, Depends(get_current_user)],
              session: Annotated[Session, Depends(get_session)]) -> SkillRead:
    try:
        return SkillService(session).get(id, user.role)
    except SkillNotFound:
        raise HTTPException(status_code=404, detail="Skill não encontrada.") from None
