from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from src.bootstrap.dependencies import (
    current_user_id,
    execute_idempotent,
    idempotency_key,
    tenant_transaction,
)
from src.config.settings import get_settings
from src.persistence.repositories.chat import ChatRepository
from src.shared.errors.api_error import ApiError
from src.transport.http.controllers import chat as controller
from src.transport.http.requests.chat import ChatMessageCreateRequest, ChatSessionCreateRequest

router = APIRouter(prefix="/chat/sessions", tags=["chat"])


def _guard() -> None:
    if not get_settings().enable_chat:
        raise ApiError(404, "FEATURE_DISABLED", "Chat is not enabled.")


def _env(request: Request, data: object) -> dict[str, object]:
    return {"data": data, "meta": {"requestId": request.state.request_id}}


@router.post("", status_code=201, operation_id="createChatSession")
async def create_session(
    request: Request,
    response: Response,
    payload: ChatSessionCreateRequest,
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    _guard()

    async def work(session):
        return 201, _env(request, await controller.create_session(session, user_id, payload.title))

    status, body, replay = await execute_idempotent(
        user_id, key, "POST", request.url.path, payload.model_dump(mode="json"), work
    )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
    return body


@router.get("", operation_id="listChatSessions")
async def list_sessions(request: Request, user_id=Depends(current_user_id)):
    _guard()
    async with tenant_transaction(user_id) as session:
        return _env(
            request,
            [
                controller.session_resource(item)
                for item in await ChatRepository(session).sessions(user_id)
            ],
        )


@router.get("/{session_id}/messages", operation_id="listChatMessages")
async def list_messages(request: Request, session_id: UUID, user_id=Depends(current_user_id)):
    _guard()
    async with tenant_transaction(user_id) as session:
        repo = ChatRepository(session)
        if await repo.session(user_id, session_id) is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        return _env(
            request,
            [
                controller.message_resource(item)
                for item in await repo.messages(user_id, session_id)
                if item.role != "TOOL"
            ],
        )


@router.post("/{session_id}/messages", operation_id="createChatMessage")
async def create_message(
    request: Request,
    response: Response,
    session_id: UUID,
    payload: ChatMessageCreateRequest,
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    _guard()
    settings = get_settings()

    async def work(session):
        return 200, _env(
            request,
            await controller.create_message(
                session, user_id, session_id, payload.message, settings
            ),
        )

    status, body, replay = await execute_idempotent(
        user_id, key, "POST", request.url.path, payload.model_dump(mode="json"), work
    )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
    return body


@router.delete("/{session_id}", operation_id="deleteChatSession")
async def delete_session(request: Request, session_id: UUID, user_id=Depends(current_user_id)):
    _guard()
    async with tenant_transaction(user_id) as session:
        item = await ChatRepository(session).session(user_id, session_id)
        if item is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        await session.delete(item)
        return _env(request, {"id": session_id, "status": "DELETED"})
