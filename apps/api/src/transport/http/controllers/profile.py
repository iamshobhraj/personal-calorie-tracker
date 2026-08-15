from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.application.service import UserService
from src.persistence.models.user import AppUser
from src.persistence.repositories.users import UserRepository
from src.transport.http.requests.profile import ProfileUpdateRequest


def profile_resource(user: AppUser) -> dict[str, object]:
    return {
        "id": user.id,
        "email": user.email,
        "displayName": user.display_name,
        "timezone": user.timezone_name,
    }


async def get_profile(session: AsyncSession, user_id: UUID) -> dict[str, object]:
    return profile_resource(await UserService(UserRepository(session)).profile(user_id))


async def update_profile(
    session: AsyncSession, user_id: UUID, request: ProfileUpdateRequest
) -> dict[str, object]:
    return profile_resource(
        await UserService(UserRepository(session)).update_profile(
            user_id, request.display_name, request.timezone
        )
    )
