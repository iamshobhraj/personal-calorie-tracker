from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import UserStatus
from src.persistence.models.user import AppUser


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self, user_id: UUID) -> AppUser | None:
        return await self._session.scalar(
            select(AppUser).where(AppUser.id == user_id, AppUser.status == UserStatus.ACTIVE)
        )

    async def get_active_by_email(self, email: str) -> AppUser | None:
        return await self._session.scalar(
            select(AppUser).where(
                func.lower(AppUser.email) == email.strip().lower(),
                AppUser.status == UserStatus.ACTIVE,
            )
        )

    def add(self, user: AppUser) -> None:
        self._session.add(user)

    async def update_profile(
        self, user_id: UUID, display_name: str | None, timezone_name: str
    ) -> AppUser | None:
        user = await self.get_active(user_id)
        if user is not None:
            user.display_name = display_name
            user.timezone_name = timezone_name
        return user
