"""Contrato HTTP de liveness, independente do PostgreSQL e do .env local."""

from collections.abc import AsyncIterator

import httpx
import psycopg
import pytest

from app.core.config import Settings


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[httpx.AsyncClient]:
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("APP_NAME", "CodeTrack")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("CODETRACK_DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:1/test")

    def reject_database_connection(*args: object, **kwargs: object) -> None:
        raise AssertionError("/health não deve acessar o banco.")

    monkeypatch.setattr(psycopg, "connect", reject_database_connection)
    monkeypatch.setattr(psycopg.Connection, "connect", reject_database_connection)

    from app.main import app

    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as test_client:
            yield test_client


@pytest.mark.anyio
async def test_health_returns_ok_without_database(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_health_rejects_post(client: httpx.AsyncClient) -> None:
    response = await client.post("/health")

    assert response.status_code == 405
