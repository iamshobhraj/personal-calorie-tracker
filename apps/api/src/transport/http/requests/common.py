from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class StrictRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)


def _finite_decimal(value: Decimal) -> Decimal:
    if not value.is_finite():
        raise ValueError("must be finite")
    return value


FiniteDecimal = Annotated[Decimal, Field(strict=True)]
