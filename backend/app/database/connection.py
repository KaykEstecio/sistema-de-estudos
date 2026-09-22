"""Engine e ciclo de vida das sessões PostgreSQL."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings

settings = Settings()
engine = create_engine(
    settings.database_url.get_secret_value(),
    pool_pre_ping=True,
    hide_parameters=True,
    connect_args={"connect_timeout": 5},
)
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Fornece sessão isolada; fechar reverte transações ainda não confirmadas."""
    with SessionLocal() as session:
        yield session
