from uuid import UUID

from src.persistence.models.user import AppUser
from src.persistence.repositories.users import UserRepository
from src.shared.errors.api_error import ApiError


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def profile(self, user_id: UUID) -> AppUser:
        user = await self._repository.get_active(user_id)
        if user is None:
            raise ApiError(401, "UNAUTHORIZED", "A valid access token is required.")
        return user

    async def update_profile(self, user_id: UUID, display_name: str, timezone: str) -> AppUser:
        user = await self._repository.update_profile(user_id, display_name, timezone)
        if user is None:
            raise ApiError(401, "UNAUTHORIZED", "A valid access token is required.")
        return user
