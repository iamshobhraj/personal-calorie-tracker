from typing import Protocol
from uuid import UUID

from src.persistence.models.user import AppUser


class UserRepositoryPort(Protocol):
    async def get_active(self, user_id: UUID) -> AppUser | None: ...
