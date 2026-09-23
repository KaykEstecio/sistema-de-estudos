"""Regras de cadastro e controle da transação de usuários."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserRead


class EmailAlreadyRegistered(Exception):
    """O índice único recusou um endereço já cadastrado."""


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = UserRepository(session)

    def register(self, data: UserCreate) -> UserRead:
        try:
            user = self.repository.create(
                name=data.name, email=data.email,
                password_hash=hash_password(data.password.get_secret_value()),
            )
            result = UserRead.model_validate(user)
            self.session.commit()
            return result
        except IntegrityError as exc:
            self.session.rollback()
            diagnostic = getattr(exc.orig, "diag", None)
            if (getattr(exc.orig, "sqlstate", None) == "23505"
                    and getattr(diagnostic, "constraint_name", None) == "ux_users_email_lower"):
                raise EmailAlreadyRegistered() from None
            raise
        except Exception:
            self.session.rollback()
            raise
