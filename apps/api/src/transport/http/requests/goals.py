from datetime import date
from decimal import Decimal

from pydantic import Field, model_validator

from src.persistence.models.enums import GoalStatus, TargetKind
from src.transport.http.requests.common import StrictRequestModel


class GoalTargetInput(StrictRequestModel):
    nutrient_code: str = Field(alias="nutrientCode", min_length=1, max_length=40)
    target_amount: Decimal = Field(alias="targetAmount", ge=0, max_digits=12, decimal_places=4)
    target_kind: TargetKind = Field(alias="targetKind")


class GoalCreateRequest(StrictRequestModel):
    name: str = Field(min_length=1, max_length=100)
    effective_from: date = Field(alias="effectiveFrom")
    effective_to: date | None = Field(default=None, alias="effectiveTo")
    target_weight_kg: Decimal | None = Field(
        default=None, alias="targetWeightKg", gt=0, max_digits=6, decimal_places=2
    )
    targets: list[GoalTargetInput] = Field(min_length=1, max_length=25)

    @model_validator(mode="after")
    def valid_goal(self) -> "GoalCreateRequest":
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effectiveTo must be later than effectiveFrom")
        codes = [target.nutrient_code for target in self.targets]
        if len(codes) != len(set(codes)):
            raise ValueError("targets must not contain duplicate nutrient codes")
        return self


class GoalReplaceRequest(GoalCreateRequest):
    status: GoalStatus = GoalStatus.ACTIVE
