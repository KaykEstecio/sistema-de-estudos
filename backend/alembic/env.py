"""Integra migrations aos metadados e à configuração do backend."""

from alembic import context
from alembic.util import CommandError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.database.base import Base
from app.modules.users.models import User  # Registra o model nos metadados.

# Adicionar imports de novos models conforme forem implementados.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera SQL sem abrir uma conexão com o banco."""
    settings = Settings()
    context.configure(
        url=settings.database_url.get_secret_value(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Reutiliza o engine configurado, fechando conexão e pool ao terminar."""
    from app.database.connection import engine

    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


try:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
except (SQLAlchemyError, ValueError, OSError):
    raise CommandError(
        "Falha no Alembic. Verifique a configuração local, o PostgreSQL "
        "e a migration em execução; credenciais não são exibidas."
    ) from None
