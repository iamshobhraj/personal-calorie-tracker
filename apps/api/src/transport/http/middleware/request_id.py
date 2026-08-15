from __future__ import annotations

import re
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._~-]{1,128}$")
logger = structlog.get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a safe correlation identifier to each HTTP request and response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming_request_id = request.headers.get("X-Request-Id", "")
        request_id = (
            incoming_request_id if _SAFE_REQUEST_ID.fullmatch(incoming_request_id) else str(uuid4())
        )
        request.state.request_id = request_id
        with structlog.contextvars.bound_contextvars(request_id=request_id):
            response = await call_next(request)
            logger.info(
                "http_request_completed",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
            )
        response.headers["X-Request-Id"] = request_id
        return response
