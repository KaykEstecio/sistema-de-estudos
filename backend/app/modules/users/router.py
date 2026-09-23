"""Contratos HTTP de cadastro e login."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database.connection import get_session
from app.core.config import JWTSettings
from app.modules.users.auth_service import AuthService, InvalidCredentials
from app.modules.users.schemas import LoginRequest, TokenResponse
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import EmailAlreadyRegistered, UserService
from app.modules.users.dependencies import get_current_user, get_jwt_settings
from app.modules.users.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/me", response_model=UserRead)
def me(response: Response, user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    response.headers["Cache-Control"] = "no-store"
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[JWTSettings, Depends(get_jwt_settings)],
) -> TokenResponse:
    try:
        result = AuthService(session, settings).login(data)
    except InvalidCredentials:
        raise HTTPException(
            status_code=401, detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer", "Cache-Control": "no-store"},
        ) from None
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return result


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, session: Annotated[Session, Depends(get_session)]) -> UserRead:
    try:
        return UserService(session).register(data)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.") from None
