from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response

from src.bootstrap.dependencies import (
    current_user_id,
    execute_idempotent,
    idempotency_key,
    tenant_transaction,
)
from src.shared.pagination.page import Page
from src.transport.http.controllers import meals as controller
from src.transport.http.requests.meals import MealUpsertRequest

router = APIRouter(prefix="/meal-entries", tags=["meals"])


def _envelope(
    request: Request,
    data: object,
    timezone: str | None = None,
    filters: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "data": data,
        "meta": {"requestId": request.state.request_id, "timezone": timezone, "filters": filters},
    }


@router.get("", operation_id="listMealEntries")
async def list_meals(
    request: Request,
    dateFrom: date | None = None,
    dateTo: date | None = None,
    mealType: list[str] | None = None,
    page: int = 1,
    limit: int = 20,
    user_id=Depends(current_user_id),
):
    from src.modules.users.application.service import UserService
    from src.persistence.models.enums import MealType
    from src.persistence.repositories.users import UserRepository

    async with tenant_transaction(user_id) as session:
        user = await UserService(UserRepository(session)).profile(user_id)
        today = date.today()
        start, end = dateFrom or today, dateTo or today
        if end < start or (end - start).days > 366:
            from src.shared.errors.api_error import ApiError

            raise ApiError(422, "VALIDATION_FAILED", "The date range is invalid.")
        types = [MealType(item) for item in mealType or []]
        data, total = await controller.list_meals(session, user_id, start, end, types, page, limit)
    result = Page(page, limit, total)
    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "totalItems": total,
            "totalPages": result.total_pages,
            "hasNext": result.has_next,
            "hasPrevious": result.has_previous,
        },
        "meta": {
            "requestId": request.state.request_id,
            "timezone": user.timezone_name,
            "filters": {"dateFrom": str(start), "dateTo": str(end)},
        },
    }


@router.get("/{meal_id}", operation_id="getMealEntry")
async def get_meal(request: Request, meal_id: UUID, user_id=Depends(current_user_id)):
    async with tenant_transaction(user_id) as session:
        data = await controller.get_meal(session, user_id, meal_id)
    return _envelope(request, data)


@router.post("", status_code=201, operation_id="createMealEntry")
async def create_meal(
    request: Request,
    response: Response,
    payload: MealUpsertRequest,
    chat_confirmation_token: str | None = Header(default=None, alias="X-Chat-Confirmation-Token"),
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    async def work(session):
        return 201, _envelope(
            request,
            await controller.create_meal(session, user_id, payload, chat_confirmation_token),
        )

    status, body, replay = await execute_idempotent(
        user_id, key, "POST", request.url.path, payload.model_dump(mode="json", by_alias=True), work
    )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
        body["meta"]["requestId"] = request.state.request_id
    return body


@router.put("/{meal_id}", operation_id="replaceMealEntry")
async def replace_meal(
    request: Request, meal_id: UUID, payload: MealUpsertRequest, user_id=Depends(current_user_id)
):
    async with tenant_transaction(user_id) as session:
        data = await controller.replace_meal(session, user_id, meal_id, payload)
    return _envelope(request, data)


@router.delete("/{meal_id}", operation_id="deleteMealEntry")
async def delete_meal(request: Request, meal_id: UUID, user_id=Depends(current_user_id)):
    async with tenant_transaction(user_id) as session:
        data = await controller.delete_meal(session, user_id, meal_id)
    return _envelope(request, data)
