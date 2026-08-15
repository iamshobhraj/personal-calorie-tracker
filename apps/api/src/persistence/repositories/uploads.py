from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import UploadStatus
from src.persistence.models.upload import UploadObject


class UploadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, upload: UploadObject) -> None:
        self._session.add(upload)

    async def get_owned(self, user_id: UUID, upload_id: UUID) -> UploadObject | None:
        return await self._session.scalar(
            select(UploadObject).where(
                UploadObject.id == upload_id, UploadObject.user_id == user_id
            )
        )

    async def mark_deleted(self, user_id: UUID, upload_id: UUID) -> bool:
        upload = await self.get_owned(user_id, upload_id)
        if upload is None:
            return False
        upload.status = UploadStatus.DELETED
        return True
