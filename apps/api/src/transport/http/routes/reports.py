from datetime import date

from fastapi import APIRouter, Depends, Query, Request

from src.bootstrap.dependencies import current_user_id, tenant_transaction
from src.shared.pagination.page import Page
from src.transport.http.controllers import reports as controller

router = APIRouter(prefix="/reports", tags=["reports"])


def _page(
    request: Request, data: list[dict[str, object]], page: int, limit: int, timezone: str | None
) -> dict[str, object]:
    total = len(data)
    result = Page(page, limit, total)
    slice_ = data[(page - 1) * limit : page * limit]
    return {
        "data": slice_,
        "pagination": {
            "page": page,
            "limit": limit,
            "totalItems": total,
            "totalPages": result.total_pages,
            "hasNext": result.has_next,
            "hasPrevious": result.has_previous,
        },
        "meta": {"requestId": request.state.request_id, "timezone": timezone},
    }


def _range(start: date, end: date) -> None:
    if end < start or (end - start).days > 366:
        from src.shared.errors.api_error import ApiError

        raise ApiError(422, "VALIDATION_FAILED", "The date range is invalid.")


@router.get("/calorie-trend", operation_id="getCalorieTrend")
async def calorie_trend(
    request: Request,
    dateFrom: date,
    dateTo: date,
    interval: str = "DAY",
    page: int = 1,
    limit: int = 20,
    timezone: str | None = None,
    user_id=Depends(current_user_id),
):
    _range(dateFrom, dateTo)
    async with tenant_transaction(user_id) as session:
        data = await controller.calorie_trend(session, user_id, dateFrom, dateTo, interval)
    return _page(request, data, page, limit, timezone)


@router.get("/macros", operation_id="getMacroReport")
async def macros(
    request: Request,
    dateFrom: date,
    dateTo: date,
    interval: str = "DAY",
    page: int = 1,
    limit: int = 20,
    timezone: str | None = None,
    user_id=Depends(current_user_id),
):
    _range(dateFrom, dateTo)
    async with tenant_transaction(user_id) as session:
        data = await controller.macros(session, user_id, dateFrom, dateTo, interval)
    return _page(request, data, page, limit, timezone)


@router.get("/micronutrients", operation_id="getMicronutrientReport")
async def micronutrients(
    request: Request,
    dateFrom: date,
    dateTo: date,
    nutrientCode: list[str] = Query(default=[]),
    page: int = 1,
    limit: int = 20,
    timezone: str | None = None,
    user_id=Depends(current_user_id),
):
    _range(dateFrom, dateTo)
    async with tenant_transaction(user_id) as session:
        data = await controller.micronutrients(session, user_id, dateFrom, dateTo, nutrientCode)
    return _page(request, data, page, limit, timezone)


@router.get("/goal-comparison", operation_id="getGoalComparison")
async def goal_comparison(
    request: Request,
    dateFrom: date,
    dateTo: date,
    interval: str = "DAY",
    page: int = 1,
    limit: int = 20,
    timezone: str | None = None,
    user_id=Depends(current_user_id),
):
    _range(dateFrom, dateTo)
    from src.shared.errors.api_error import ApiError
    from src.transport.http.controllers.goals import current_goal

    periods = []
    from src.modules.reports.application.service import ReportService

    async with tenant_transaction(user_id) as session:
        for start, end in ReportService.periods(dateFrom, dateTo, interval):
            try:
                goal = await current_goal(session, user_id, start)
                periods.append(
                    {
                        "periodStart": start,
                        "periodEnd": end,
                        "goalId": goal["id"],
                        "comparisons": [],
                        "dataComplete": False,
                    }
                )
            except ApiError:
                periods.append(
                    {
                        "periodStart": start,
                        "periodEnd": end,
                        "goalId": None,
                        "comparisons": [],
                        "dataComplete": False,
                    }
                )
    return _page(request, periods, page, limit, timezone)
