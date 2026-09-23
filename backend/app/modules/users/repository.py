"""Consultas e persistência de usuários; transações pertencem ao chamador."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == func.lower(email.strip()))
        return self.session.scalar(statement)

    def create(self, *, name: str, email: str, password_hash: str) -> User:
        """Recebe dados validados e hash já calculado; não aceita senha em texto puro."""
        user = User(name=name, email=email, password_hash=password_hash)
        self.session.add(user)
        self.session.flush()
        return user
