from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import NutrientCategory
from src.persistence.repositories.nutrients import NutrientRepository


async def list_nutrients(
    session: AsyncSession, category: NutrientCategory | None, page: int, limit: int
) -> tuple[list[dict[str, object]], int]:
    repository = NutrientRepository(session)
    rows = await repository.list_active(category, page, limit)
    return [
        {
            "code": row.code,
            "name": row.name,
            "category": row.category,
            "unit": row.canonical_unit,
            "displayOrder": row.display_order,
        }
        for row in rows
    ], await repository.count_active(category)
