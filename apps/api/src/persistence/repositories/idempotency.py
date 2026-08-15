from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.idempotency import IdempotencyRecord


class IdempotencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def claim(self, record: IdempotencyRecord) -> bool:
        statement = (
            insert(IdempotencyRecord)
            .values(
                user_id=record.user_id,
                idempotency_key=record.idempotency_key,
                method=record.method,
                path=record.path,
                request_hash=record.request_hash,
                expires_at=record.expires_at,
            )
            .on_conflict_do_nothing(index_elements=["user_id", "idempotency_key"])
        )
        result = await self._session.execute(statement)
        return getattr(result, "rowcount", 0) == 1

    async def get(self, user_id: UUID, key: str) -> IdempotencyRecord | None:
        return await self._session.get(
            IdempotencyRecord, {"user_id": user_id, "idempotency_key": key}
        )

    async def fetch_completed_replay(
        self, user_id: UUID, key: str, request_hash: str
    ) -> IdempotencyRecord | None:
        record = await self.get(user_id, key)
        if record is None or record.request_hash != request_hash or record.response_status is None:
            return None
        return record

    async def complete(self, user_id: UUID, key: str, status: int, body: dict[str, Any]) -> bool:
        record = await self.get(user_id, key)
        if record is None:
            return False
        record.response_status = status
        record.response_body = body
        return True

    async def is_conflicting(self, user_id: UUID, key: str, request_hash: str) -> bool:
        record = await self.get(user_id, key)
        return record is not None and record.request_hash != request_hash

    async def purge_expired(self, before: datetime) -> int:
        result = await self._session.execute(
            delete(IdempotencyRecord).where(IdempotencyRecord.expires_at < before)
        )
        return int(getattr(result, "rowcount", 0) or 0)
