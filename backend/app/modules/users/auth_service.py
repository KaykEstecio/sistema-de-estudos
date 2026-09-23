"""Autenticação por credenciais; não altera o cadastro ou as permissões."""

import secrets

from sqlalchemy.orm import Session

from app.core.config import JWTSettings
from app.core.security import hash_password, verify_password
from app.core.tokens import create_access_token, decode_access_token
from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import LoginRequest, TokenResponse

# Uma verificação Argon2 também ocorre quando o endereço não existe.
_dummy_hash = hash_password(secrets.token_urlsafe(32))


class InvalidCredentials(Exception):
    """Falha genérica sem identificar qual credencial está incorreta."""


class PermissionDenied(Exception):
    """Usuário autenticado não possui a role necessária."""


class AuthService:
    def __init__(self, session: Session, settings: JWTSettings) -> None:
        self.repository = UserRepository(session)
        self.settings = settings

    def authenticate(self, token: str) -> User:
        user_id = decode_access_token(token, self.settings)
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise InvalidCredentials()
        return user

    @staticmethod
    def require_admin(user: User) -> None:
        if user.role != UserRole.ADMIN:
            raise PermissionDenied()

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(data.email)
        password_hash = user.password_hash if user is not None else _dummy_hash
        valid = verify_password(data.password.get_secret_value(), password_hash)
        if user is None or not valid:
            raise InvalidCredentials()
        return TokenResponse(
            access_token=create_access_token(user.id, self.settings),
            expires_in=self.settings.jwt_access_token_minutes * 60,
        )
