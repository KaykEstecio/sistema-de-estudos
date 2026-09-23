"""Adaptação HTTP das regras de autenticação e autorização."""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import JWTSettings
from app.core.tokens import InvalidAccessToken
from app.database.connection import get_session
from app.modules.users.auth_service import AuthService, InvalidCredentials, PermissionDenied
from app.modules.users.models import User

bearer = HTTPBearer(auto_error=False)


def get_jwt_settings() -> JWTSettings:
    return JWTSettings()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[JWTSettings, Depends(get_jwt_settings)],
) -> User:
    try:
        if credentials is None:
            raise InvalidCredentials()
        return AuthService(session, settings).authenticate(credentials.credentials)
    except (InvalidCredentials, InvalidAccessToken):
        raise HTTPException(
            status_code=401, detail="Autenticação inválida ou ausente.",
            headers={"WWW-Authenticate": "Bearer", "Cache-Control": "no-store"},
        ) from None


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    try:
        AuthService.require_admin(user)
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permissão insuficiente.") from None
    return user
