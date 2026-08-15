from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer

T = TypeVar("T")


class ResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @field_serializer("*", when_used="json")
    def serialize_decimal(self, value: object) -> object:
        return float(value) if isinstance(value, Decimal) else value


class Meta(ResponseModel):
    request_id: str = Field(alias="requestId")
    timezone: str | None = None
    filters: dict[str, object] | None = None


class Envelope(ResponseModel, Generic[T]):
    data: T
    meta: Meta


class Pagination(ResponseModel):
    page: int
    limit: int
    total_items: int = Field(alias="totalItems")
    total_pages: int = Field(alias="totalPages")
    has_next: bool = Field(alias="hasNext")
    has_previous: bool = Field(alias="hasPrevious")


class PageEnvelope(ResponseModel, Generic[T]):
    data: list[T]
    pagination: Pagination
    meta: Meta


class ErrorDetail(ResponseModel):
    field: str | None = None
    code: str
    message: str


class ErrorBody(ResponseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorEnvelope(ResponseModel):
    error: ErrorBody
    meta: Meta
