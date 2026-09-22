"""Base declarativa compartilhada pelos futuros models e pelo Alembic."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Reúne metadados ORM sem criar tabelas automaticamente."""
