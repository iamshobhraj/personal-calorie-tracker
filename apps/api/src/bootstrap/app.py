from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Environment, get_settings
from src.shared.logging.configure import configure_logging
from src.transport.http.middleware.error_handler import register_error_handlers
from src.transport.http.middleware.request_id import RequestIdMiddleware
from src.transport.http.routes.auth import router as auth_router
from src.transport.http.routes.extractions import router as extractions_router
from src.transport.http.routes.goals import router as goals_router
from src.transport.http.routes.health import router as health_router
from src.transport.http.routes.meals import router as meals_router
from src.transport.http.routes.nutrients import router as nutrients_router
from src.transport.http.routes.profile import router as profile_router
from src.transport.http.routes.reports import router as reports_router


def create_app() -> FastAPI:
    """Build the HTTP application and its cross-cutting transport policies."""

    settings = get_settings()
    configure_logging(settings.log_level)
    is_production = settings.environment is Environment.PRODUCTION
    app = FastAPI(
        title=settings.app_name,
        openapi_url=None if is_production else f"{settings.api_prefix}/openapi.json",
        docs_url=None if is_production else f"{settings.api_prefix}/docs",
        redoc_url=None if is_production else f"{settings.api_prefix}/redoc",
    )
    app.add_middleware(RequestIdMiddleware)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.cors_origins],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-Id"],
        )
    register_error_handlers(app)
    app.include_router(health_router, prefix=settings.api_prefix)
    for router in (
        auth_router,
        profile_router,
        nutrients_router,
        goals_router,
        meals_router,
        extractions_router,
        reports_router,
    ):
        app.include_router(router, prefix=settings.api_prefix)
    return app
