from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import NutrientCategory
from src.persistence.models.nutrition import NutrientDefinition


class NutrientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(
        self, category: NutrientCategory | None, page: int, limit: int
    ) -> list[NutrientDefinition]:
        statement = select(NutrientDefinition).where(NutrientDefinition.is_active.is_(True))
        if category is not None:
            statement = statement.where(NutrientDefinition.category == category)
        statement = (
            statement.order_by(NutrientDefinition.display_order, NutrientDefinition.id)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list((await self._session.scalars(statement)).all())

    async def count_active(self, category: NutrientCategory | None) -> int:
        statement = (
            select(func.count())
            .select_from(NutrientDefinition)
            .where(NutrientDefinition.is_active.is_(True))
        )
        if category is not None:
            statement = statement.where(NutrientDefinition.category == category)
        return int((await self._session.scalar(statement)) or 0)

    async def get_mapping_by_codes(self, codes: Iterable[str]) -> dict[str, NutrientDefinition]:
        rows = await self._session.scalars(
            select(NutrientDefinition).where(NutrientDefinition.code.in_(set(codes)))
        )
        return {nutrient.code: nutrient for nutrient in rows}

    async def get_by_code(self, code: str) -> NutrientDefinition | None:
        return await self._session.scalar(
            select(NutrientDefinition).where(NutrientDefinition.code == code)
        )
