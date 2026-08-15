import re
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from uuid import UUID

from fastapi import Header

from src.config.settings import Settings, get_settings
from src.persistence.models.idempotency import IdempotencyRecord
from src.persistence.repositories.idempotency import IdempotencyRepository
from src.persistence.session import get_session_factory
from src.persistence.transaction_manager import SqlAlchemyTransactionManager
from src.shared.errors.api_error import ApiError
from src.shared.idempotency import canonical_hash
from src.shared.security.jwt_tokens import decode_access_token


def settings_dependency() -> Settings:
    """Provide typed settings to routes that need configuration."""

    return get_settings()


_IDEMPOTENCY = re.compile(r"^[A-Za-z0-9._~:-]{1,100}$")


async def current_user_id(authorization: Annotated[str | None, Header()] = None) -> UUID:
    if authorization is None or not authorization.startswith("Bearer "):
        raise ApiError(401, "UNAUTHORIZED", "A valid access token is required.")
    return decode_access_token(authorization[7:], get_settings())


def idempotency_key(value: Annotated[str | None, Header(alias="Idempotency-Key")] = None) -> str:
    if value is None or _IDEMPOTENCY.fullmatch(value) is None:
        raise ApiError(
            400, "INVALID_IDEMPOTENCY_KEY", "Idempotency-Key is required and must be safe."
        )
    return value


async def execute_idempotent(
    user_id: UUID,
    key: str,
    method: str,
    path: str,
    body: object,
    work: Callable[[Any], Awaitable[tuple[int, dict[str, Any]]]],
) -> tuple[int, dict[str, Any], bool]:
    request_hash = canonical_hash(method, path, user_id, body)
    async with SqlAlchemyTransactionManager(get_session_factory(), user_id) as transaction:
        repository = IdempotencyRepository(transaction.session)
        existing = await repository.get(user_id, key)
        if existing is not None:
            if existing.request_hash != request_hash:
                raise ApiError(
                    409, "IDEMPOTENCY_CONFLICT", "This key was used with a different request."
                )
            if existing.response_body is None or existing.response_status is None:
                raise ApiError(
                    409, "IDEMPOTENCY_IN_PROGRESS", "The original request is still being processed."
                )
            return existing.response_status, existing.response_body, True
        record = IdempotencyRecord(
            user_id=user_id,
            idempotency_key=key,
            method=method,
            path=path,
            request_hash=request_hash,
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        transaction.session.add(record)
        status, response = await work(transaction.session)
        record.response_status, record.response_body = status, response
        return status, response, False


@asynccontextmanager
async def tenant_transaction(user_id: UUID) -> AsyncIterator[Any]:
    async with SqlAlchemyTransactionManager(get_session_factory(), user_id) as transaction:
        yield transaction.session


@asynccontextmanager
async def system_transaction() -> AsyncIterator[Any]:
    async with SqlAlchemyTransactionManager(get_session_factory(), None) as transaction:
        yield transaction.session
