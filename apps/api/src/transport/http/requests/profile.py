from pydantic import Field, field_validator

from src.shared.time.timezone import validate_timezone
from src.transport.http.requests.common import StrictRequestModel


class ProfileUpdateRequest(StrictRequestModel):
    display_name: str = Field(alias="displayName", min_length=1, max_length=100)
    timezone: str

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        return validate_timezone(value)
