from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import ExtractionStatus
from src.persistence.models.upload import NutritionExtraction


class ExtractionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, extraction: NutritionExtraction) -> None:
        self._session.add(extraction)

    async def get_owned(self, user_id: UUID, extraction_id: UUID) -> NutritionExtraction | None:
        return await self._session.scalar(
            select(NutritionExtraction).where(
                NutritionExtraction.id == extraction_id, NutritionExtraction.user_id == user_id
            )
        )

    async def mark_succeeded(
        self, user_id: UUID, extraction_id: UUID, payload: dict[str, object], completed_at: datetime
    ) -> bool:
        extraction = await self.get_owned(user_id, extraction_id)
        if extraction is None:
            return False
        extraction.status = ExtractionStatus.SUCCEEDED
        extraction.extracted_payload = payload
        extraction.completed_at = completed_at
        return True

    async def mark_failed(
        self, user_id: UUID, extraction_id: UUID, failure_code: str, failure_message: str
    ) -> bool:
        extraction = await self.get_owned(user_id, extraction_id)
        if extraction is None:
            return False
        extraction.status = ExtractionStatus.FAILED
        extraction.failure_code = failure_code
        extraction.failure_message = failure_message
        return True

    async def count_successful_for_day(
        self, user_id: UUID, day_start: datetime, day_end: datetime
    ) -> int:
        statement = (
            select(func.count())
            .select_from(NutritionExtraction)
            .where(
                NutritionExtraction.user_id == user_id,
                NutritionExtraction.status == ExtractionStatus.SUCCEEDED,
                NutritionExtraction.completed_at >= day_start,
                NutritionExtraction.completed_at < day_end,
            )
        )
        return int((await self._session.scalar(statement)) or 0)
