from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.reports.application.service import ReportService
from src.persistence.repositories.meals import MealRepository
from src.persistence.repositories.nutrients import NutrientRepository


def _service(session: AsyncSession) -> ReportService:
    return ReportService(MealRepository(session), NutrientRepository(session))


async def calorie_trend(
    session: AsyncSession, user_id: UUID, start: date, end: date, interval: str
) -> list[dict[str, object]]:
    return await _service(session).calorie_trend(user_id, start, end, interval)


async def macros(
    session: AsyncSession, user_id: UUID, start: date, end: date, interval: str
) -> list[dict[str, object]]:
    return await _service(session).macros(user_id, start, end, interval)


async def micronutrients(
    session: AsyncSession, user_id: UUID, start: date, end: date, codes: list[str]
) -> list[dict[str, object]]:
    return await _service(session).micronutrients(user_id, start, end, codes)
