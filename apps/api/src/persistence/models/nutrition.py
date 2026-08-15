from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Identity, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.persistence.base import Base
from src.persistence.models.enums import NutrientCategory

if TYPE_CHECKING:
    from src.persistence.models.goal import GoalNutrientTarget
    from src.persistence.models.meal import MealEntryNutrient


class NutrientDefinition(Base):
    __tablename__ = "nutrient_definition"
    __table_args__ = (
        CheckConstraint(
            "category IN ('ENERGY','MACRO','VITAMIN','MINERAL')", name="nutrient_category"
        ),
        CheckConstraint("canonical_unit IN ('kcal','g','mg','mcg')", name="nutrient_unit"),
    )

    id: Mapped[int] = mapped_column(SmallInteger, Identity(always=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[NutrientCategory] = mapped_column(String(12))
    canonical_unit: Mapped[str] = mapped_column(String(12))
    display_order: Mapped[int] = mapped_column(SmallInteger, default=0, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    goal_targets: Mapped[list[GoalNutrientTarget]] = relationship(lazy="raise")
    meal_nutrients: Mapped[list[MealEntryNutrient]] = relationship(lazy="raise")
