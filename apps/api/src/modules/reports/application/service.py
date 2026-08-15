from datetime import date, timedelta
from decimal import Decimal
from typing import cast
from uuid import UUID

from src.persistence.models.enums import NutrientCategory
from src.persistence.models.meal import MealEntry
from src.persistence.repositories.meals import MealRepository
from src.persistence.repositories.nutrients import NutrientRepository


class ReportService:
    def __init__(self, meals: MealRepository, nutrients: NutrientRepository) -> None:
        self._meals, self._nutrients = meals, nutrients

    @staticmethod
    def periods(date_from: date, date_to: date, interval: str) -> list[tuple[date, date]]:
        if interval == "WEEK":
            cursor = date_from - timedelta(days=date_from.weekday())
            result = []
            while cursor <= date_to:
                result.append((max(cursor, date_from), min(cursor + timedelta(days=6), date_to)))
                cursor += timedelta(days=7)
            return result
        return [
            (date_from + timedelta(days=i), date_from + timedelta(days=i))
            for i in range((date_to - date_from).days + 1)
        ]

    async def _meals_in_range(
        self, user_id: UUID, date_from: date, date_to: date
    ) -> list[MealEntry]:
        return await self._meals.list_range(user_id, date_from, date_to, None, 1, 1000000)

    async def calorie_trend(
        self, user_id: UUID, date_from: date, date_to: date, interval: str
    ) -> list[dict[str, object]]:
        meals = await self._meals_in_range(user_id, date_from, date_to)
        result = []
        for start, end in self.periods(date_from, date_to, interval):
            rows = [meal for meal in meals if start <= meal.local_date <= end]
            calories = [
                row.amount
                for meal in rows
                for row in meal.nutrients
                if row.nutrient.code == "ENERGY_KCAL"
            ]
            result.append(
                {
                    "periodStart": start,
                    "periodEnd": end,
                    "calories": sum(calories, Decimal(0)) if calories else None,
                    "knownEntryCount": len(
                        {
                            meal.id
                            for meal in rows
                            if any(row.nutrient.code == "ENERGY_KCAL" for row in meal.nutrients)
                        }
                    ),
                    "totalEntryCount": len(rows),
                }
            )
        return cast(list[dict[str, object]], result)

    async def macros(
        self, user_id: UUID, date_from: date, date_to: date, interval: str
    ) -> list[dict[str, object]]:
        meals = await self._meals_in_range(user_id, date_from, date_to)
        result = []
        for start, end in self.periods(date_from, date_to, interval):
            rows = [meal for meal in meals if start <= meal.local_date <= end]
            amounts = {
                code: sum(
                    (n.amount for meal in rows for n in meal.nutrients if n.nutrient.code == code),
                    Decimal(0),
                )
                for code in ("PROTEIN", "CARBOHYDRATE", "FAT")
            }
            energy = {
                "PROTEIN": amounts["PROTEIN"] * 4,
                "CARBOHYDRATE": amounts["CARBOHYDRATE"] * 4,
                "FAT": amounts["FAT"] * 9,
            }
            total = sum(energy.values(), Decimal(0))
            result.append(
                {
                    "periodStart": start,
                    "periodEnd": end,
                    "totals": {
                        "protein": {"amount": amounts["PROTEIN"], "unit": "g"},
                        "carbohydrate": {"amount": amounts["CARBOHYDRATE"], "unit": "g"},
                        "fat": {"amount": amounts["FAT"], "unit": "g"},
                    },
                    "calorieContributionPercent": {
                        key.lower(): (value * 100 / total if total else None)
                        for key, value in energy.items()
                    },
                    "knownEntryCount": len(rows),
                    "totalEntryCount": len(rows),
                }
            )
        return result

    async def micronutrients(
        self, user_id: UUID, date_from: date, date_to: date, codes: list[str]
    ) -> list[dict[str, object]]:
        definitions = (
            await self._nutrients.get_mapping_by_codes(codes)
            if codes
            else {
                row.code: row
                for category in (NutrientCategory.VITAMIN, NutrientCategory.MINERAL)
                for row in await self._nutrients.list_active(category, 1, 100)
            }
        )
        meals = await self._meals_in_range(user_id, date_from, date_to)
        days = Decimal((date_to - date_from).days + 1)
        result = []
        for code, definition in definitions.items():
            observed = [
                (meal, n) for meal in meals for n in meal.nutrients if n.nutrient.code == code
            ]
            amount = sum((n.amount for _, n in observed), Decimal(0))
            known = len({meal.id for meal, _ in observed})
            result.append(
                {
                    "nutrientCode": code,
                    "name": definition.name,
                    "amount": amount,
                    "unit": definition.canonical_unit,
                    "dailyAverage": amount / days,
                    "knownEntryCount": known,
                    "totalEntryCount": len(meals),
                    "coveragePercent": Decimal(known * 100) / len(meals) if meals else Decimal(0),
                }
            )
        return result
