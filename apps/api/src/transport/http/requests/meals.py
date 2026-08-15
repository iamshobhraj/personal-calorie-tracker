from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from src.persistence.models.enums import MealSource, MealType, NutrientProvenance
from src.shared.time.timezone import validate_timezone, validate_zoned_datetime
from src.transport.http.requests.common import StrictRequestModel


class QuantityInput(StrictRequestModel):
    value: Decimal = Field(gt=0, max_digits=12, decimal_places=4)
    unit: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=200)


class MealNutrientInput(StrictRequestModel):
    code: str = Field(min_length=1, max_length=40)
    amount: Decimal = Field(ge=0, max_digits=14, decimal_places=4)
    confidence: Decimal | None = Field(default=None, ge=0, le=1, max_digits=5, decimal_places=4)
    provenance: NutrientProvenance | None = None


class MealUpsertRequest(StrictRequestModel):
    meal_type: MealType = Field(alias="mealType")
    food_name: str = Field(alias="foodName", min_length=1, max_length=200)
    quantity: QuantityInput
    occurred_at: datetime = Field(alias="occurredAt")
    timezone: str
    source: MealSource = MealSource.MANUAL
    source_extraction_id: UUID | None = Field(default=None, alias="sourceExtractionId")
    notes: str | None = Field(default=None, max_length=1000)
    nutrients: list[MealNutrientInput] = Field(min_length=1, max_length=25)

    @model_validator(mode="after")
    def valid_meal(self) -> "MealUpsertRequest":
        validate_timezone(self.timezone)
        validate_zoned_datetime(self.occurred_at, self.timezone)
        codes = [nutrient.code for nutrient in self.nutrients]
        if len(codes) != len(set(codes)):
            raise ValueError("nutrients must not contain duplicate codes")
        if "ENERGY_KCAL" not in codes:
            raise ValueError("ENERGY_KCAL is required")
        if self.source is MealSource.IMAGE and self.source_extraction_id is None:
            raise ValueError("image meals require sourceExtractionId")
        if self.source is not MealSource.IMAGE and self.source_extraction_id is not None:
            raise ValueError("sourceExtractionId is only allowed for image meals")
        if self.source is MealSource.MANUAL and any(
            n.provenance is not None for n in self.nutrients
        ):
            raise ValueError("manual meals cannot supply AI provenance")
        return self


class PageQuery(StrictRequestModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class MealListQuery(PageQuery):
    date_from: date | None = Field(default=None, alias="dateFrom")
    date_to: date | None = Field(default=None, alias="dateTo")
    meal_type: list[MealType] = Field(default_factory=list, alias="mealType")
    sort: Literal["occurredAt:desc"] = "occurredAt:desc"

    @model_validator(mode="after")
    def valid_range(self) -> "MealListQuery":
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("dateTo must not be before dateFrom")
        if self.date_from and self.date_to and (self.date_to - self.date_from).days > 366:
            raise ValueError("date range may not exceed 366 days")
        return self
