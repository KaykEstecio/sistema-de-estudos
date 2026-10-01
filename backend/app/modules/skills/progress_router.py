"""Consulta exclusiva do progresso do usuário autenticado."""

from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.skills.service import SkillService
from app.modules.skills.progress_schemas import ProgressQuery, UserSkillPage

router = APIRouter(prefix="/api/v1/users/me/skills", tags=["skills"])


@router.get("", response_model=UserSkillPage)
def list_progress(query: Annotated[ProgressQuery, Query()],
                  user: Annotated[User, Depends(get_current_user)],
                  session: Annotated[Session, Depends(get_session)], response: Response) -> UserSkillPage:
    response.headers["Cache-Control"] = "no-store"
    return SkillService(session).list_owned_progress(user.id, query)
