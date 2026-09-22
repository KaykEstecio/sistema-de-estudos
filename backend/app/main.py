"""Ponto de entrada ASGI da aplicação CodeTrack."""

from fastapi import FastAPI

from app.core.config import Settings

settings = Settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/health")
def health() -> dict[str, str]:
    """Informa que a aplicação está respondendo, sem consultar serviços externos."""
    return {"status": "ok"}
