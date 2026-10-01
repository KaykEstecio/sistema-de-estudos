"""Resumo somente da identidade autenticada, inclusive para ADMIN."""

from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.dashboard.schemas import DashboardQuery, DashboardRead
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardRead)
def dashboard(query: Annotated[DashboardQuery, Query()],
              user: Annotated[User, Depends(get_current_user)],
              session: Annotated[Session, Depends(get_session)], response: Response) -> DashboardRead:
    response.headers["Cache-Control"] = "no-store"
    return DashboardService(session).get_owned(user.id, query)
