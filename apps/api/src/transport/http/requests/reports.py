from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from src.shared.time.timezone import validate_timezone
from src.transport.http.requests.meals import PageQuery


class ReportQuery(PageQuery):
    date_from: date = Field(alias="dateFrom")
    date_to: date = Field(alias="dateTo")
    interval: Literal["DAY", "WEEK"] = "DAY"
    timezone: str | None = None

    @model_validator(mode="after")
    def valid_range(self) -> "ReportQuery":
        if self.date_to < self.date_from or (self.date_to - self.date_from).days > 366:
            raise ValueError("date range must be ordered and no longer than 366 days")
        if self.timezone:
            validate_timezone(self.timezone)
        return self
