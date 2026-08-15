from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.bootstrap.dependencies import current_user_id, tenant_transaction
from src.transport.http.controllers import profile as controller
from src.transport.http.requests.profile import ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["profile"])


def _envelope(request: Request, data: object) -> dict[str, object]:
    return {"data": data, "meta": {"requestId": request.state.request_id}}


@router.get("", operation_id="getProfile")
async def get_profile(
    request: Request, user_id: UUID = Depends(current_user_id)
) -> dict[str, object]:
    async with tenant_transaction(user_id) as session:
        data = await controller.get_profile(session, user_id)
    return _envelope(request, data)


@router.put("", operation_id="updateProfile")
async def update_profile(
    request: Request,
    payload: ProfileUpdateRequest,
    user_id: UUID = Depends(current_user_id),
) -> dict[str, object]:
    async with tenant_transaction(user_id) as session:
        data = await controller.update_profile(session, user_id, payload)
    return _envelope(request, data)
