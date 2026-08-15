from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.persistence.models.enums import MealType


class AiQuantity(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    value: Decimal = Field(gt=0)
    unit: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=200)


class AiNutrient(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    amount: Decimal = Field(ge=0)
    unit: Literal["kcal", "g", "mg", "mcg"]
    confidence: Decimal = Field(ge=0, le=1)


class AiNutritionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    image_kind: Literal["LABEL", "PLATE"] = Field(alias="imageKind")
    food_name: str = Field(alias="foodName", min_length=1, max_length=200)
    quantity: AiQuantity
    suggested_meal_type: MealType | None = Field(default=None, alias="suggestedMealType")
    nutrients: list[AiNutrient] = Field(min_length=1, max_length=25)
    overall_confidence: Decimal = Field(alias="overallConfidence", ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=20)
    requires_user_confirmation: Literal[True] = Field(alias="requiresUserConfirmation")
