from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt

from src.config.settings import Settings
from src.shared.errors.api_error import ApiError


def constraints_hash(payload: object) -> str:
    from src.shared.idempotency import canonical_hash

    return canonical_hash("CHAT", "meal-confirmation", "", payload)


def _key(settings: Settings) -> str:
    return hashlib.sha256(
        (settings.jwt_secret.get_secret_value() + ":chat-confirmation:v1").encode()
    ).hexdigest()


def issue_confirmation(
    settings: Settings, user_id: UUID, session_id: UUID, action: str, digest: str
) -> tuple[str, UUID, datetime]:
    now = datetime.now(UTC)
    expires = now + timedelta(seconds=settings.chat_confirmation_ttl_seconds)
    jti = uuid4()
    token = jwt.encode(
        {
            "type": "chat_confirmation",
            "sub": str(user_id),
            "session_id": str(session_id),
            "action": action,
            "draft_constraints_hash": digest,
            "jti": str(jti),
            "iat": now,
            "exp": expires,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        _key(settings),
        algorithm="HS256",
    )
    return token, jti, expires


def decode_confirmation(settings: Settings, token: str) -> dict[str, object]:
    try:
        claims = jwt.decode(
            token,
            _key(settings),
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={
                "require": ["exp", "sub", "session_id", "action", "draft_constraints_hash", "jti"]
            },
        )
    except jwt.PyJWTError as exc:
        raise ApiError(
            401, "INVALID_CHAT_CONFIRMATION", "The chat confirmation is invalid or expired."
        ) from exc
    if claims.get("type") != "chat_confirmation":
        raise ApiError(
            401, "INVALID_CHAT_CONFIRMATION", "The chat confirmation is invalid or expired."
        )
    return claims
