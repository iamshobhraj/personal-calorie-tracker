from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from src.persistence.models.enums import (
    GoalStatus,
    MealSource,
    MealType,
    NutrientCategory,
    NutrientProvenance,
    TargetKind,
)
from src.transport.http.responses.common import ResponseModel


class ProfileResource(ResponseModel):
    id: UUID
    email: str
    display_name: str = Field(alias="displayName")
    timezone: str = Field(alias="timezone_name")


class NutrientCatalogResource(ResponseModel):
    code: str
    name: str
    category: NutrientCategory
    unit: str = Field(alias="canonical_unit")
    display_order: int = Field(alias="displayOrder")


class NutrientAmountResource(ResponseModel):
    code: str
    name: str
    category: NutrientCategory
    amount: Decimal
    unit: str
    confidence: Decimal | None
    provenance: NutrientProvenance


class GoalTargetResource(ResponseModel):
    nutrient_code: str = Field(alias="nutrientCode")
    target_amount: Decimal = Field(alias="targetAmount")
    unit: str
    target_kind: TargetKind = Field(alias="targetKind")


class GoalResource(ResponseModel):
    id: UUID
    name: str
    effective_from: date = Field(alias="effectiveFrom")
    effective_to: date | None = Field(alias="effectiveTo")
    target_weight_kg: Decimal | None = Field(alias="targetWeightKg")
    status: GoalStatus
    targets: list[GoalTargetResource]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class QuantityResource(ResponseModel):
    value: Decimal
    unit: str
    description: str | None


class MealEntryResource(ResponseModel):
    id: UUID
    meal_type: MealType = Field(alias="mealType")
    food_name: str = Field(alias="foodName")
    quantity: QuantityResource
    occurred_at: datetime = Field(alias="occurredAt")
    timezone: str
    local_date: date = Field(alias="localDate")
    source: MealSource
    source_extraction_id: UUID | None = Field(alias="sourceExtractionId")
    notes: str | None
    nutrients: list[NutrientAmountResource]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
