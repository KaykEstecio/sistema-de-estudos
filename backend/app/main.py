"""Ponto de entrada ASGI da aplicação CodeTrack."""

from fastapi import FastAPI
from app.modules.assessments.router import router as assessments_router
from app.modules.assessments.service import AssessmentNotFound, AssessmentConflict
from app.core.errors import assessment_error_handler
from app.modules.onboarding.router import router as onboarding_router
from app.core.errors import onboarding_error_handler
from app.modules.onboarding.service import OnboardingAlreadyCompleted, OnboardingNotCompleted, InterestCategoryNotFound
from app.modules.users.auth_service import InvalidCredentials
from fastapi.exceptions import RequestValidationError

from app.core.config import Settings
from app.core.errors import validation_error_handler
from app.core.errors import catalog_error_handler
from app.modules.categories.service import CategoryNotFound, CategorySlugConflict
from app.modules.skills.service import SkillNotFound, SkillSlugConflict
from app.modules.users.router import router as users_router
from app.modules.categories.router import router as categories_router
from app.modules.skills.router import router as skills_router
from app.modules.skills.progress_router import router as progress_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.dashboard.router import router as dashboard_router

from app.modules.challenges.router import router as challenges_router
from app.modules.challenges.service import ChallengeNotFound, ChallengeConflict
from app.modules.users.auth_service import PermissionDenied
from app.core.errors import challenge_error_handler
from app.modules.attempts.router import router as attempts_router
from app.modules.attempts.service import AttemptNotFound, AttemptConflict
from app.core.errors import attempt_error_handler
from app.modules.evaluation.router import router as evaluation_router
from app.modules.evaluation.service import EvaluationNotFound, EvaluationConflict, EvaluationSkillsMismatch
from app.core.errors import evaluation_error_handler
settings = Settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)
app.add_exception_handler(RequestValidationError, validation_error_handler)
for error_type in (CategoryNotFound, CategorySlugConflict, SkillNotFound, SkillSlugConflict):
    app.add_exception_handler(error_type, catalog_error_handler)
app.include_router(users_router)
app.include_router(evaluation_router)
for error_type in (EvaluationNotFound, EvaluationConflict, EvaluationSkillsMismatch):
    app.add_exception_handler(error_type, evaluation_error_handler)
app.include_router(attempts_router)
for error_type in (AttemptNotFound, AttemptConflict):
    app.add_exception_handler(error_type, attempt_error_handler)
app.include_router(assessments_router)
for error_type in (AssessmentNotFound, AssessmentConflict):
    app.add_exception_handler(error_type, assessment_error_handler)
app.include_router(onboarding_router)
for error_type in (OnboardingAlreadyCompleted, OnboardingNotCompleted, InterestCategoryNotFound, InvalidCredentials):
    app.add_exception_handler(error_type, onboarding_error_handler)
app.include_router(categories_router)
app.include_router(skills_router)
app.include_router(progress_router)
app.include_router(recommendations_router)
app.include_router(dashboard_router)
app.include_router(challenges_router)
for error_type in (ChallengeNotFound, ChallengeConflict, PermissionDenied):
    app.add_exception_handler(error_type, challenge_error_handler)


@app.get("/health")
def health() -> dict[str, str]:
    """Informa que a aplicação está respondendo, sem consultar serviços externos."""
    return {"status": "ok"}
