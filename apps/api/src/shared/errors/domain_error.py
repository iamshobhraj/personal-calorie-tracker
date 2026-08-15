from src.shared.errors.api_error import ApiError


class DomainError(ApiError):
    """Business-rule failure that can be translated directly at the boundary."""
