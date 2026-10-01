"""Erros de entrada sem reproduzir conteúdo fornecido pelo cliente."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.modules.categories.service import CategoryNotFound, CategorySlugConflict
from app.modules.skills.service import SkillNotFound, SkillSlugConflict
from app.modules.onboarding.service import OnboardingAlreadyCompleted, OnboardingNotCompleted, InterestCategoryNotFound
from app.modules.users.auth_service import InvalidCredentials
from app.modules.assessments.service import AssessmentNotFound, AssessmentConflict
from app.modules.challenges.service import ChallengeNotFound, ChallengeConflict
from app.modules.users.auth_service import PermissionDenied
from app.modules.attempts.service import AttemptNotFound, AttemptConflict
from app.modules.evaluation.service import EvaluationNotFound, EvaluationConflict, EvaluationSkillsMismatch


async def evaluation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, EvaluationNotFound):
        status, detail = 404, "Avaliação ou tentativa não encontrada."
    elif isinstance(exc, EvaluationSkillsMismatch):
        status, detail = 422, "Informe exatamente as skills do contexto da tentativa."
    else:
        status, detail = 409, str(exc)
    return JSONResponse(status_code=status, content={"detail": detail}, headers={"Cache-Control": "no-store"})


async def attempt_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404 if isinstance(exc, AttemptNotFound) else 409,
                        content={"detail": "Recurso não encontrado." if isinstance(exc, AttemptNotFound) else str(exc)},
                        headers={"Cache-Control": "no-store"})


async def challenge_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, PermissionDenied):
        status, detail = 403, "Permissão insuficiente."
    elif isinstance(exc, ChallengeNotFound):
        status, detail = 404, "Desafio não encontrado."
    else:
        status, detail = 409, str(exc)
    return JSONResponse(status_code=status, content={"detail": detail}, headers={"Cache-Control": "no-store"})


async def assessment_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404 if isinstance(exc, AssessmentNotFound) else 409,
                        content={"detail": str(exc)}, headers={"Cache-Control": "no-store"})


async def onboarding_error_handler(request: Request, exc: Exception) -> JSONResponse:
    errors = {
        OnboardingAlreadyCompleted: (409, "Onboarding já concluído."),
        OnboardingNotCompleted: (409, "Onboarding ainda não concluído."),
        InterestCategoryNotFound: (404, "Categoria de interesse não encontrada."),
        InvalidCredentials: (401, "Autenticação inválida ou ausente."),
    }
    status, detail = errors[type(exc)]
    headers = {"Cache-Control": "no-store"}
    if status == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(status_code=status, content={"detail": detail}, headers=headers)


async def catalog_error_handler(request: Request, exc: Exception) -> JSONResponse:
    errors = {
        CategoryNotFound: (404, "Categoria não encontrada."),
        SkillNotFound: (404, "Skill não encontrada."),
        CategorySlugConflict: (409, "Slug de categoria já cadastrado."),
        SkillSlugConflict: (409, "Slug de skill já cadastrado."),
    }
    status, detail = errors[type(exc)]
    return JSONResponse(status_code=status, content={"detail": detail})


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # input, ctx e mensagens de validadores podem incluir credenciais.
    errors = [
        {"loc": (error["loc"][:-1] if error["type"] == "extra_forbidden" else error["loc"]),
         "type": error["type"], "msg": "Entrada inválida."}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors}, headers={"Cache-Control": "no-store"})
