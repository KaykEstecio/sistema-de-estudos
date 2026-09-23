"""Erros de entrada sem reproduzir conteúdo fornecido pelo cliente."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # input, ctx e mensagens de validadores podem incluir credenciais.
    errors = [
        {"loc": (error["loc"][:-1] if error["type"] == "extra_forbidden" else error["loc"]),
         "type": error["type"], "msg": "Entrada inválida."}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})
