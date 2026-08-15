from datetime import date

from fastapi import APIRouter, Depends, Request, Response

from src.bootstrap.dependencies import (
    current_user_id,
    execute_idempotent,
    idempotency_key,
    tenant_transaction,
)
from src.shared.pagination.page import Page
from src.transport.http.controllers import goals as controller
from src.transport.http.requests.goals import GoalCreateRequest

router = APIRouter(prefix="/goals", tags=["goals"])


def _envelope(request: Request, data: object) -> dict[str, object]:
    return {"data": data, "meta": {"requestId": request.state.request_id}}


@router.get("/current", operation_id="getCurrentGoal")
async def current_goal(
    request: Request, onDate: date | None = None, user_id=Depends(current_user_id)
):
    async with tenant_transaction(user_id) as session:
        from src.modules.users.application.service import UserService
        from src.persistence.repositories.users import UserRepository

        await UserService(UserRepository(session)).profile(user_id)
        data = await controller.current_goal(session, user_id, onDate or date.today())
    return _envelope(request, data)


@router.get("", operation_id="listGoals")
async def list_goals(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    user_id=Depends(current_user_id),
):
    from src.persistence.models.enums import GoalStatus
    from src.persistence.repositories.goals import GoalRepository

    if page < 1 or not 1 <= limit <= 100:
        from src.shared.errors.api_error import ApiError

        raise ApiError(422, "VALIDATION_FAILED", "Pagination is invalid.")
    goal_status = GoalStatus(status) if status else None
    async with tenant_transaction(user_id) as session:
        repository = GoalRepository(session)
        goals = await repository.list(user_id, goal_status, page, limit)
        total = len(await repository.list(user_id, goal_status, 1, 1000000))
    result = Page(page, limit, total)
    return {
        "data": [controller.goal_resource(goal) for goal in goals],
        "pagination": {
            "page": page,
            "limit": limit,
            "totalItems": total,
            "totalPages": result.total_pages,
            "hasNext": result.has_next,
            "hasPrevious": result.has_previous,
        },
        "meta": {"requestId": request.state.request_id},
    }


@router.post("", status_code=201, operation_id="createGoal")
async def create_goal(
    request: Request,
    response: Response,
    payload: GoalCreateRequest,
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    async def work(session):
        return 201, _envelope(request, await controller.create_goal(session, user_id, payload))

    status, body, replay = await execute_idempotent(
        user_id, key, "POST", request.url.path, payload.model_dump(mode="json", by_alias=True), work
    )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
        body["meta"]["requestId"] = request.state.request_id
    return body


@router.put("/{goal_id}", operation_id="replaceGoal")
async def replace_goal(
    request: Request, goal_id: str, payload: GoalCreateRequest, user_id=Depends(current_user_id)
):
    from uuid import UUID

    async with tenant_transaction(user_id) as session:
        data = await controller.replace_goal(session, user_id, UUID(goal_id), payload)
    return _envelope(request, data)


@router.delete("/{goal_id}", operation_id="deleteGoal")
async def delete_goal(request: Request, goal_id: str, user_id=Depends(current_user_id)):
    from uuid import UUID

    async with tenant_transaction(user_id) as session:
        data = await controller.delete_goal(session, user_id, UUID(goal_id), date.today())
    return _envelope(request, data)
