from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.shared.errors.api_error import ApiError


def validate_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ApiError(422, "VALIDATION_FAILED", "Timezone must be a valid IANA timezone.") from exc
    return value


def validate_zoned_datetime(value: datetime, timezone_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ApiError(422, "VALIDATION_FAILED", "occurredAt must include an explicit offset.")
    zone = ZoneInfo(validate_timezone(timezone_name))
    expected = value.astimezone(zone).utcoffset()
    if value.utcoffset() != expected:
        raise ApiError(422, "VALIDATION_FAILED", "occurredAt offset is inconsistent with timezone.")
    return value


def local_date(value: datetime, timezone_name: str) -> date:
    return value.astimezone(ZoneInfo(timezone_name)).date()
