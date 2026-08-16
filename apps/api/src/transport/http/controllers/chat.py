from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.persistence.models.bonus import ChatMessage, ChatSession
from src.persistence.models.enums import ChatRole
from src.persistence.repositories.chat import ChatRepository
from src.services.ai.chat_service import NutritionChatProvider
from src.services.ai.limiter import AI_REQUEST_LIMITER
from src.shared.errors.api_error import ApiError


def session_resource(item: ChatSession) -> dict[str, object]:
    return {
        "id": item.id,
        "title": item.title,
        "createdAt": item.created_at,
        "updatedAt": item.updated_at,
    }


def message_resource(item: ChatMessage) -> dict[str, object]:
    return {
        "id": item.id,
        "role": item.role,
        "content": item.content,
        "createdAt": item.created_at,
        "actions": [],
    }


async def create_session(
    session: AsyncSession, user_id: UUID, title: str | None
) -> dict[str, object]:
    item = ChatSession(user_id=user_id, title=title)
    ChatRepository(session).add(item)
    await session.flush()
    return session_resource(item)


async def create_message(
    session: AsyncSession, user_id: UUID, session_id: UUID, message: str, settings: Settings
) -> dict[str, object]:
    repo = ChatRepository(session)
    item = await repo.session(user_id, session_id)
    if item is None:
        raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
    history = await repo.messages(user_id, session_id)
    user_message = ChatMessage(
        user_id=user_id, session_id=session_id, role=ChatRole.USER, content=message
    )
    repo.add(user_message)
    await session.flush()
    compact = [
        (row.role.lower(), row.content)
        for row in [*history, user_message]
        if row.role != ChatRole.TOOL
    ]
    total = 0
    context: list[tuple[str, str]] = []
    for role, content in reversed(compact[-20:]):
        remaining = 12_000 - total
        if remaining <= 0:
            break
        context.append((role, content[-remaining:]))
        total += min(len(content), remaining)
    response = await NutritionChatProvider(settings, AI_REQUEST_LIMITER).respond(
        list(reversed(context))
    )
    assistant = ChatMessage(
        user_id=user_id, session_id=session_id, role=ChatRole.ASSISTANT, content=response
    )
    repo.add(assistant)
    item.updated_at = datetime.now(UTC)
    await session.flush()
    return {
        "userMessageId": user_message.id,
        "assistantMessage": message_resource(assistant),
        "actions": [],
    }
