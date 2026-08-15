from __future__ import annotations

import os

from pwdlib import PasswordHash
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.auth import AuthCredential
from src.persistence.models.enums import UserStatus
from src.persistence.models.user import AppUser


async def seed_reviewer(session: AsyncSession) -> bool:
    """Create a reviewer only when explicit non-empty environment values are supplied."""

    email = os.environ.get("SEED_REVIEWER_EMAIL", "").strip().lower()
    password = os.environ.get("SEED_REVIEWER_PASSWORD", "")
    if not email or not password:
        return False
    user = await session.scalar(select(AppUser).where(func.lower(AppUser.email) == email))
    if user is None:
        user = AppUser(
            email=email,
            display_name=os.environ.get("SEED_REVIEWER_NAME", "Reviewer"),
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        await session.flush()
    credential = await session.get(AuthCredential, user.id)
    if credential is None:
        session.add(
            AuthCredential(user_id=user.id, password_hash=PasswordHash.recommended().hash(password))
        )
    return True
