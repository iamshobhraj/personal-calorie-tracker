from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from src.bootstrap.dependencies import (
    current_user_id,
    idempotency_key,
    system_transaction,
    tenant_transaction,
)
from src.config.settings import get_settings
from src.transport.http.controllers import auth as controller
from src.transport.http.requests.auth import EmptyRequest, LoginRequest, SignupRequest

router = APIRouter(prefix="/auth", tags=["authentication"])


def _envelope(request: Request, data: object) -> dict[str, object]:
    return {"data": data, "meta": {"requestId": request.state.request_id}}


def _set_refresh(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        "refresh_token",
        token,
        max_age=settings.refresh_token_ttl_days * 86400,
        path=f"{settings.api_prefix}/auth",
        httponly=True,
        samesite="lax",
        secure=settings.refresh_cookie_secure,
    )


@router.post("/signup", status_code=201, operation_id="signup")
async def signup(
    request: Request, payload: SignupRequest, _: str = Depends(idempotency_key)
) -> dict[str, object]:
    async with system_transaction() as session:
        return _envelope(request, await controller.signup(session, payload))


@router.post("/login", operation_id="login")
async def login(request: Request, response: Response, payload: LoginRequest) -> dict[str, object]:
    async with system_transaction() as session:
        data, refresh = await controller.login(session, payload, request.headers.get("User-Agent"))
    _set_refresh(response, refresh)
    return _envelope(request, data)


@router.post("/refresh", operation_id="refresh")
async def refresh(request: Request, response: Response, _: EmptyRequest) -> dict[str, object]:
    token = request.cookies.get("refresh_token")
    if not token:
        from src.shared.errors.api_error import ApiError

        raise ApiError(401, "UNAUTHORIZED", "A valid refresh session is required.")
    # The session's user is resolved after its opaque token is hashed; RLS applies once it is known.
    async with system_transaction() as session:
        data, replacement = await controller.refresh(
            session, token, request.headers.get("User-Agent")
        )
    _set_refresh(response, replacement)
    return _envelope(request, data)


@router.post("/logout", operation_id="logout")
async def logout(
    request: Request,
    response: Response,
    _: EmptyRequest,
    user_id: UUID = Depends(current_user_id),
) -> dict[str, object]:
    async with tenant_transaction(user_id) as session:
        await controller.logout(session, user_id, request.cookies.get("refresh_token"))
    response.delete_cookie("refresh_token", path=f"{get_settings().api_prefix}/auth")
    return _envelope(request, {"status": "LOGGED_OUT"})
