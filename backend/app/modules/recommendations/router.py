"""Consulta autenticada, sem identidade fornecida pelo cliente."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.recommendations.schemas import RecommendationQuery, RecommendationResponse
from app.modules.recommendations.service import RecommendationService, RecommendationSkillUnavailable

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
def recommend(query: Annotated[RecommendationQuery, Query()],
              user: Annotated[User, Depends(get_current_user)],
              session: Annotated[Session, Depends(get_session)], response: Response) -> RecommendationResponse:
    response.headers["Cache-Control"] = "no-store"
    try:
        return RecommendationService(session).recommend(user.id, query)
    except RecommendationSkillUnavailable:
        raise HTTPException(status_code=404, detail="Skill indisponível para recomendação.",
                            headers={"Cache-Control": "no-store"}) from None
