from enum import StrEnum

from pydantic import Field

from src.transport.http.requests.common import StrictRequestModel
from src.transport.http.requests.meals import MealUpsertRequest


class PdfImportValidity(StrEnum):
    ALL = "ALL"
    VALID = "VALID"
    INVALID = "INVALID"


class PdfRowUpdateRequest(StrictRequestModel):
    selected: bool
    parsed_meal: MealUpsertRequest = Field(alias="parsedMeal")


class PdfCommitRequest(StrictRequestModel):
    selected_row_ids: list[int] | None = Field(default=None, alias="selectedRowIds", max_length=500)
