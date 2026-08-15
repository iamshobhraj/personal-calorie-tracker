from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.bootstrap.dependencies import settings_dependency
from src.modules.auth.application.service import AuthService
from src.persistence.repositories.auth import AuthRepository
from src.persistence.repositories.users import UserRepository
from src.transport.http.requests.auth import LoginRequest, SignupRequest


def _service(session: AsyncSession) -> AuthService:
    return AuthService(UserRepository(session), AuthRepository(session), settings_dependency())


async def signup(session: AsyncSession, request: SignupRequest) -> dict[str, object]:
    user = await _service(session).signup(
        request.email, request.password.get_secret_value(), request.display_name, request.timezone
    )
    return {"userId": user.id, "status": "ACTIVE"}


async def login(
    session: AsyncSession, request: LoginRequest, user_agent: str | None
) -> tuple[dict[str, object], str]:
    user, access, refresh = await _service(session).login(
        request.email, request.password.get_secret_value(), user_agent
    )
    return {
        "accessToken": access,
        "expiresIn": settings_dependency().access_token_ttl_seconds,
        "tokenType": "Bearer",
        "user": {"id": user.id, "displayName": user.display_name, "timezone": user.timezone_name},
    }, refresh


async def refresh(
    session: AsyncSession, token: str, user_agent: str | None
) -> tuple[dict[str, object], str]:
    access, replacement = await _service(session).refresh(token, user_agent)
    return {
        "accessToken": access,
        "expiresIn": settings_dependency().access_token_ttl_seconds,
        "tokenType": "Bearer",
    }, replacement


async def logout(session: AsyncSession, user_id: UUID, token: str | None) -> None:
    await _service(session).logout(user_id, token)
