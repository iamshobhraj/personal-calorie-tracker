from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.persistence.models.enums import MealType
from src.persistence.models.meal import MealEntry, MealEntryNutrient


class MealRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _with_nutrients(self) -> Any:
        return selectinload(MealEntry.nutrients).selectinload(MealEntryNutrient.nutrient)

    def add(self, meal: MealEntry) -> None:
        self._session.add(meal)

    async def get_owned(self, user_id: UUID, meal_id: UUID) -> MealEntry | None:
        return await self._session.scalar(
            select(MealEntry)
            .options(self._with_nutrients())
            .where(MealEntry.id == meal_id, MealEntry.user_id == user_id)
        )

    async def list_range(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
        meal_types: Iterable[MealType] | None,
        page: int,
        limit: int,
    ) -> list[MealEntry]:
        statement = (
            select(MealEntry)
            .options(self._with_nutrients())
            .where(
                MealEntry.user_id == user_id,
                MealEntry.local_date >= date_from,
                MealEntry.local_date <= date_to,
            )
        )
        if meal_types is not None:
            statement = statement.where(MealEntry.meal_type.in_(tuple(meal_types)))
        statement = (
            statement.order_by(
                MealEntry.local_date.desc(), MealEntry.occurred_at.desc(), MealEntry.id.desc()
            )
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list((await self._session.scalars(statement)).unique().all())

    async def count_range(
        self, user_id: UUID, date_from: date, date_to: date, meal_types: Iterable[MealType] | None
    ) -> int:
        statement = (
            select(func.count())
            .select_from(MealEntry)
            .where(
                MealEntry.user_id == user_id,
                MealEntry.local_date >= date_from,
                MealEntry.local_date <= date_to,
            )
        )
        if meal_types is not None:
            statement = statement.where(MealEntry.meal_type.in_(tuple(meal_types)))
        return int((await self._session.scalar(statement)) or 0)

    async def replace_owned(
        self, user_id: UUID, meal_id: UUID, replacement: MealEntry
    ) -> MealEntry | None:
        meal = await self.get_owned(user_id, meal_id)
        if meal is None:
            return None
        meal.meal_type = replacement.meal_type
        meal.food_name = replacement.food_name
        meal.quantity = replacement.quantity
        meal.quantity_unit = replacement.quantity_unit
        meal.portion_description = replacement.portion_description
        meal.occurred_at = replacement.occurred_at
        meal.entry_timezone = replacement.entry_timezone
        meal.local_date = replacement.local_date
        meal.notes = replacement.notes
        meal.nutrients = replacement.nutrients
        return meal

    async def delete_owned(self, user_id: UUID, meal_id: UUID) -> bool:
        result = await self._session.execute(
            delete(MealEntry).where(MealEntry.id == meal_id, MealEntry.user_id == user_id)
        )
        return getattr(result, "rowcount", 0) == 1

    async def owns_extraction(self, user_id: UUID, extraction_id: UUID) -> bool:
        statement = (
            select(MealEntry.id)
            .where(MealEntry.user_id == user_id, MealEntry.source_extraction_id == extraction_id)
            .limit(1)
        )
        return await self._session.scalar(statement) is not None
