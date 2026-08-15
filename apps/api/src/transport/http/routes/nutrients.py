from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.bootstrap.dependencies import current_user_id, tenant_transaction
from src.persistence.models.enums import NutrientCategory
from src.shared.pagination.page import Page
from src.transport.http.controllers import nutrients as controller

router = APIRouter(prefix="/nutrients", tags=["nutrients"])


@router.get("", operation_id="listNutrients")
async def list_nutrients(
    request: Request,
    page: int = 1,
    limit: int = 20,
    category: NutrientCategory | None = None,
    user_id: UUID = Depends(current_user_id),
) -> dict[str, object]:
    if page < 1 or not 1 <= limit <= 100:
        from src.shared.errors.api_error import ApiError

        raise ApiError(422, "VALIDATION_FAILED", "Pagination is invalid.")
    async with tenant_transaction(user_id) as session:
        data, total = await controller.list_nutrients(session, category, page, limit)
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
        "meta": {"requestId": request.state.request_id},
    }
