from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.auth import AuthCredential, RefreshSession


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add_credential(self, credential: AuthCredential) -> None:
        self._session.add(credential)

    async def get_credential(self, user_id: UUID) -> AuthCredential | None:
        return await self._session.get(AuthCredential, user_id)

    async def record_failed_login(self, user_id: UUID, locked_until: datetime | None) -> None:
        credential = await self.get_credential(user_id)
        if credential is not None:
            credential.failed_login_count += 1
            credential.locked_until = locked_until

    async def reset_failed_login(self, user_id: UUID) -> None:
        credential = await self.get_credential(user_id)
        if credential is not None:
            credential.failed_login_count = 0
            credential.locked_until = None

    def add_refresh_session(self, refresh_session: RefreshSession) -> None:
        self._session.add(refresh_session)

    async def get_refresh_session(self, token_hash: str) -> RefreshSession | None:
        return await self._session.scalar(
            select(RefreshSession).where(RefreshSession.token_hash == token_hash)
        )

    async def lookup_refresh_session(self, token_hash: str) -> tuple[UUID, UUID] | None:
        """Use the narrowly-scoped database function before a refresh token reveals its tenant."""
        row = (
            await self._session.execute(
                text("SELECT id, user_id FROM refresh_session_lookup(:token_hash)"),
                {"token_hash": token_hash},
            )
        ).first()
        return (row.id, row.user_id) if row is not None else None

    async def revoke_refresh_session(self, session_id: UUID, revoked_at: datetime) -> bool:
        refresh_session = await self._session.get(RefreshSession, session_id)
        if refresh_session is None:
            return False
        refresh_session.revoked_at = revoked_at
        return True

    async def revoke_all_active(self, user_id: UUID, revoked_at: datetime) -> None:
        await self._session.execute(
            update(RefreshSession)
            .where(RefreshSession.user_id == user_id, RefreshSession.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
