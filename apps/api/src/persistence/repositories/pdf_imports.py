from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.bonus import PdfImport, PdfImportRow
from src.persistence.models.enums import PdfImportStatus


class PdfImportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, item: PdfImport) -> None:
        self._session.add(item)

    async def get_owned(
        self, user_id: UUID, import_id: UUID, lock: bool = False
    ) -> PdfImport | None:
        query = select(PdfImport).where(PdfImport.user_id == user_id, PdfImport.id == import_id)
        if lock:
            query = query.with_for_update()
        return await self._session.scalar(query)

    async def rows(self, user_id: UUID, import_id: UUID) -> list[PdfImportRow]:
        result = await self._session.scalars(
            select(PdfImportRow)
            .where(PdfImportRow.user_id == user_id, PdfImportRow.import_id == import_id)
            .order_by(PdfImportRow.source_row_number)
        )
        return list(result)

    async def selected_rows(self, user_id: UUID, import_id: UUID) -> list[PdfImportRow]:
        result = await self._session.scalars(
            select(PdfImportRow)
            .where(
                PdfImportRow.user_id == user_id,
                PdfImportRow.import_id == import_id,
                PdfImportRow.selected.is_(True),
                PdfImportRow.committed_meal_id.is_(None),
            )
            .order_by(PdfImportRow.source_row_number)
            .with_for_update()
        )
        return list(result)

    def add_rows(self, rows: list[PdfImportRow]) -> None:
        self._session.add_all(rows)

    async def count_successes_today(self, user_id: UUID) -> int:
        from datetime import UTC, datetime

        from sqlalchemy import func

        today = datetime.now(UTC).date()
        return int(
            (
                await self._session.scalar(
                    select(func.count())
                    .select_from(PdfImport)
                    .where(
                        PdfImport.user_id == user_id,
                        PdfImport.status.in_((PdfImportStatus.READY, PdfImportStatus.COMMITTED)),
                        PdfImport.created_at >= today,
                    )
                )
            )
            or 0
        )
