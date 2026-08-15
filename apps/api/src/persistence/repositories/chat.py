from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.bonus import ChatConfirmation, ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, item: ChatSession | ChatMessage | ChatConfirmation) -> None:
        self._session.add(item)

    async def session(self, user_id: UUID, session_id: UUID) -> ChatSession | None:
        return await self._session.scalar(
            select(ChatSession).where(ChatSession.user_id == user_id, ChatSession.id == session_id)
        )

    async def sessions(self, user_id: UUID) -> list[ChatSession]:
        return list(
            await self._session.scalars(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
            )
        )

    async def messages(self, user_id: UUID, session_id: UUID) -> list[ChatMessage]:
        return list(
            await self._session.scalars(
                select(ChatMessage)
                .where(ChatMessage.user_id == user_id, ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at)
            )
        )

    async def consume_confirmation(
        self, user_id: UUID, session_id: UUID, jti: UUID, action: str, digest: str
    ) -> bool:
        row = await self._session.scalar(
            select(ChatConfirmation)
            .where(
                ChatConfirmation.user_id == user_id,
                ChatConfirmation.session_id == session_id,
                ChatConfirmation.jti == jti,
                ChatConfirmation.action == action,
                ChatConfirmation.draft_constraints_hash == digest,
            )
            .with_for_update()
        )
        if row is None or row.consumed_at is not None or row.expires_at <= datetime.now(UTC):
            return False
        row.consumed_at = datetime.now(UTC)
        return True
