"""Ponto de entrada ASGI da aplicação CodeTrack."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.config import Settings
from app.core.errors import validation_error_handler
from app.modules.users.router import router as users_router

settings = Settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(users_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Informa que a aplicação está respondendo, sem consultar serviços externos."""
    return {"status": "ok"}
