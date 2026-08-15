from __future__ import annotations

from fastapi import APIRouter, Request

from src.persistence.session import database_is_ready
from src.shared.errors.api_error import ApiError

router = APIRouter(prefix="/health", tags=["health"])


def _response(request: Request) -> dict[str, object]:
    return {"data": {"status": "ok"}, "meta": {"requestId": request.state.request_id}}


@router.get("/live")
async def live(request: Request) -> dict[str, object]:
    """Return process liveness without checking external dependencies."""

    return _response(request)


@router.get("/ready")
async def ready(request: Request) -> dict[str, object]:
    """Return readiness only after PostgreSQL is reachable."""

    if not await database_is_ready():
        raise ApiError(503, "DEPENDENCY_UNAVAILABLE", "A required dependency is unavailable.")
    return _response(request)
