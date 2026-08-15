from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.enums import NutrientCategory
from src.persistence.models.nutrition import NutrientDefinition

NUTRIENTS: tuple[tuple[str, str, NutrientCategory, str, int], ...] = (
    ("ENERGY_KCAL", "Energy", NutrientCategory.ENERGY, "kcal", 10),
    ("PROTEIN", "Protein", NutrientCategory.MACRO, "g", 20),
    ("CARBOHYDRATE", "Carbohydrate", NutrientCategory.MACRO, "g", 30),
    ("FAT", "Fat", NutrientCategory.MACRO, "g", 40),
    ("FIBER", "Dietary fiber", NutrientCategory.MACRO, "g", 50),
    ("SUGAR", "Sugar", NutrientCategory.MACRO, "g", 60),
    ("VITAMIN_A", "Vitamin A", NutrientCategory.VITAMIN, "mcg", 110),
    ("VITAMIN_C", "Vitamin C", NutrientCategory.VITAMIN, "mg", 120),
    ("VITAMIN_D", "Vitamin D", NutrientCategory.VITAMIN, "mcg", 130),
    ("VITAMIN_E", "Vitamin E", NutrientCategory.VITAMIN, "mg", 140),
    ("VITAMIN_K", "Vitamin K", NutrientCategory.VITAMIN, "mcg", 150),
    ("THIAMIN_B1", "Thiamin (B1)", NutrientCategory.VITAMIN, "mg", 160),
    ("RIBOFLAVIN_B2", "Riboflavin (B2)", NutrientCategory.VITAMIN, "mg", 170),
    ("NIACIN_B3", "Niacin (B3)", NutrientCategory.VITAMIN, "mg", 180),
    ("VITAMIN_B6", "Vitamin B6", NutrientCategory.VITAMIN, "mg", 190),
    ("FOLATE_B9", "Folate (B9)", NutrientCategory.VITAMIN, "mcg", 200),
    ("VITAMIN_B12", "Vitamin B12", NutrientCategory.VITAMIN, "mcg", 210),
    ("CALCIUM", "Calcium", NutrientCategory.MINERAL, "mg", 310),
    ("IRON", "Iron", NutrientCategory.MINERAL, "mg", 320),
    ("MAGNESIUM", "Magnesium", NutrientCategory.MINERAL, "mg", 330),
    ("PHOSPHORUS", "Phosphorus", NutrientCategory.MINERAL, "mg", 340),
    ("POTASSIUM", "Potassium", NutrientCategory.MINERAL, "mg", 350),
    ("SODIUM", "Sodium", NutrientCategory.MINERAL, "mg", 360),
    ("ZINC", "Zinc", NutrientCategory.MINERAL, "mg", 370),
    ("SELENIUM", "Selenium", NutrientCategory.MINERAL, "mcg", 380),
)


async def seed_nutrients(session: AsyncSession) -> None:
    """Upsert the immutable catalog by nutrient code."""

    for code, name, category, unit, display_order in NUTRIENTS:
        statement = (
            insert(NutrientDefinition)
            .values(
                code=code,
                name=name,
                category=category,
                canonical_unit=unit,
                display_order=display_order,
            )
            .on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name": name,
                    "category": category,
                    "canonical_unit": unit,
                    "display_order": display_order,
                    "is_active": True,
                },
            )
        )
        await session.execute(statement)
