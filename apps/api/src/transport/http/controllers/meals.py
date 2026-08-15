from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.meals.application.service import MealService
from src.persistence.models.enums import MealType
from src.persistence.models.meal import MealEntry
from src.persistence.repositories.extractions import ExtractionRepository
from src.persistence.repositories.meals import MealRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.shared.errors.api_error import ApiError
from src.transport.http.requests.meals import MealUpsertRequest


def meal_resource(meal: MealEntry) -> dict[str, object]:
    return {
        "id": meal.id,
        "mealType": meal.meal_type,
        "foodName": meal.food_name,
        "quantity": {
            "value": meal.quantity,
            "unit": meal.quantity_unit,
            "description": meal.portion_description,
        },
        "occurredAt": meal.occurred_at,
        "timezone": meal.entry_timezone,
        "localDate": meal.local_date,
        "source": meal.source,
        "sourceExtractionId": meal.source_extraction_id,
        "notes": meal.notes,
        "nutrients": [
            {
                "code": item.nutrient.code,
                "name": item.nutrient.name,
                "category": item.nutrient.category,
                "amount": item.amount,
                "unit": item.nutrient.canonical_unit,
                "confidence": item.confidence,
                "provenance": item.provenance,
            }
            for item in meal.nutrients
        ],
        "createdAt": meal.created_at,
        "updatedAt": meal.updated_at,
    }


def _service(session: AsyncSession) -> MealService:
    return MealService(
        MealRepository(session), NutrientRepository(session), ExtractionRepository(session)
    )


async def create_meal(
    session: AsyncSession, user_id: UUID, request: MealUpsertRequest
) -> dict[str, object]:
    return meal_resource(await _service(session).create(user_id, request))


async def replace_meal(
    session: AsyncSession, user_id: UUID, meal_id: UUID, request: MealUpsertRequest
) -> dict[str, object]:
    return meal_resource(await _service(session).replace(user_id, meal_id, request))


async def get_meal(session: AsyncSession, user_id: UUID, meal_id: UUID) -> dict[str, object]:
    meal = await MealRepository(session).get_owned(user_id, meal_id)
    if meal is None:
        raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
    return meal_resource(meal)


async def list_meals(
    session: AsyncSession,
    user_id: UUID,
    date_from: date,
    date_to: date,
    types: list[MealType],
    page: int,
    limit: int,
) -> tuple[list[dict[str, object]], int]:
    repository = MealRepository(session)
    rows = await repository.list_range(user_id, date_from, date_to, types or None, page, limit)
    return [meal_resource(row) for row in rows], await repository.count_range(
        user_id, date_from, date_to, types or None
    )


async def delete_meal(session: AsyncSession, user_id: UUID, meal_id: UUID) -> dict[str, object]:
    if not await MealRepository(session).delete_owned(user_id, meal_id):
        raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
    return {"id": meal_id, "status": "DELETED"}
