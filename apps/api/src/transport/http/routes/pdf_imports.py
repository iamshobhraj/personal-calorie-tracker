from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile

from src.bootstrap.dependencies import (
    current_user_id,
    execute_idempotent,
    idempotency_key,
    tenant_transaction,
)
from src.config.settings import get_settings
from src.modules.meals.application.service import MealService
from src.persistence.models.enums import MealSource, MealType, PdfImportStatus
from src.persistence.repositories.extractions import ExtractionRepository
from src.persistence.repositories.meals import MealRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.persistence.repositories.pdf_imports import PdfImportRepository
from src.services.files.pdf_validator import validate_pdf
from src.services.files.temp_storage import temporary_directory
from src.shared.errors.api_error import ApiError
from src.transport.http.controllers import pdf_imports as controller
from src.transport.http.requests.meals import MealUpsertRequest
from src.transport.http.requests.pdf_imports import (
    PdfCommitRequest,
    PdfImportValidity,
    PdfRowUpdateRequest,
)

router = APIRouter(prefix="/pdf-imports", tags=["pdf imports"])


def _guard() -> None:
    if not get_settings().enable_pdf_import:
        raise ApiError(404, "FEATURE_DISABLED", "PDF import is not enabled.")


def _envelope(request: Request, data: object) -> dict[str, object]:
    return {"data": data, "meta": {"requestId": request.state.request_id}}


@router.post("", status_code=201, operation_id="createPdfImport")
async def create_pdf_import(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    timezone: str = Form(...),
    defaultMealType: MealType | None = Form(default=None),
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    _guard()
    settings = get_settings()
    async with temporary_directory(settings.upload_temp_dir) as directory:
        pdf = await validate_pdf(file, directory, settings.max_pdf_bytes, settings.pdf_max_pages)

        async def work(session):
            return 201, _envelope(
                request,
                await controller.create_import(
                    session, user_id, pdf, timezone, defaultMealType, settings
                ),
            )

        status, body, replay = await execute_idempotent(
            user_id,
            key,
            "POST",
            request.url.path,
            {"sha256": pdf.sha256_hex, "timezone": timezone, "defaultMealType": defaultMealType},
            work,
        )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
        body["meta"]["requestId"] = request.state.request_id
    return body


@router.get("/{import_id}", operation_id="getPdfImport")
async def get_pdf_import(request: Request, import_id: UUID, user_id=Depends(current_user_id)):
    _guard()
    async with tenant_transaction(user_id) as session:
        return _envelope(request, await controller.get_import(session, user_id, import_id))


@router.get("/{import_id}/rows", operation_id="listPdfImportRows")
async def list_pdf_rows(
    request: Request,
    import_id: UUID,
    page: int = 1,
    limit: int = 50,
    validity: PdfImportValidity = PdfImportValidity.ALL,
    user_id=Depends(current_user_id),
):
    _guard()
    if page < 1 or not 1 <= limit <= 100:
        raise ApiError(422, "VALIDATION_FAILED", "The page parameters are invalid.")
    async with tenant_transaction(user_id) as session:
        repo = PdfImportRepository(session)
        if await repo.get_owned(user_id, import_id) is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        rows = await repo.rows(user_id, import_id)
        if validity is PdfImportValidity.VALID:
            rows = [item for item in rows if not item.validation_errors]
        if validity is PdfImportValidity.INVALID:
            rows = [item for item in rows if item.validation_errors]
        total = len(rows)
        rows = rows[(page - 1) * limit : page * limit]
        return {
            "data": [controller.row_resource(item) for item in rows],
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total,
                "totalPages": max(1, (total + limit - 1) // limit),
                "hasNext": page * limit < total,
                "hasPrevious": page > 1,
            },
            "meta": {"requestId": request.state.request_id},
        }


@router.put("/{import_id}/rows/{row_id}", operation_id="updatePdfImportRow")
async def update_pdf_row(
    request: Request,
    import_id: UUID,
    row_id: int,
    payload: PdfRowUpdateRequest,
    user_id=Depends(current_user_id),
):
    _guard()
    async with tenant_transaction(user_id) as session:
        repo = PdfImportRepository(session)
        item = await repo.get_owned(user_id, import_id, lock=True)
        if item is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        if item.status is not PdfImportStatus.READY:
            raise ApiError(409, "IMPORT_NOT_EDITABLE", "This import cannot be edited.")
        rows = await repo.rows(user_id, import_id)
        row = next((value for value in rows if value.id == row_id), None)
        if row is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        draft = payload.parsed_meal.model_dump(mode="json", by_alias=True)
        draft["source"] = "PDF"
        draft["sourceExtractionId"] = None
        for nutrient in draft["nutrients"]:
            nutrient["provenance"] = "PDF_AI"
        row.parsed_payload, row.selected, row.validation_errors = draft, payload.selected, []
        item.valid_rows = sum(not value.validation_errors for value in rows)
        item.invalid_rows = len(rows) - item.valid_rows
        return _envelope(request, controller.row_resource(row))


@router.delete("/{import_id}", operation_id="cancelPdfImport")
async def cancel_pdf_import(request: Request, import_id: UUID, user_id=Depends(current_user_id)):
    _guard()
    async with tenant_transaction(user_id) as session:
        item = await PdfImportRepository(session).get_owned(user_id, import_id, lock=True)
        if item is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        if item.status is PdfImportStatus.COMMITTED:
            raise ApiError(
                409, "IMPORT_ALREADY_COMMITTED", "A committed import cannot be cancelled."
            )
        item.status = PdfImportStatus.CANCELLED
        return _envelope(request, {"id": item.id, "status": item.status})


@router.post("/{import_id}/commit", status_code=201, operation_id="commitPdfImport")
async def commit_pdf_import(
    request: Request,
    response: Response,
    import_id: UUID,
    payload: PdfCommitRequest,
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    _guard()

    async def work(session):
        repo = PdfImportRepository(session)
        item = await repo.get_owned(user_id, import_id, lock=True)
        if item is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        if item.status is not PdfImportStatus.READY:
            raise ApiError(409, "IMPORT_NOT_READY", "This import cannot be committed.")
        rows = await repo.selected_rows(user_id, import_id)
        if payload.selected_row_ids is not None:
            allowed = set(payload.selected_row_ids)
            rows = [row for row in rows if row.id in allowed]
        if not rows:
            raise ApiError(422, "NO_ROWS_SELECTED", "Select at least one valid row to commit.")
        if any(row.validation_errors for row in rows):
            raise ApiError(422, "IMPORT_HAS_INVALID_ROWS", "Selected rows must all be valid.")
        meals = MealService(
            MealRepository(session), NutrientRepository(session), ExtractionRepository(session)
        )
        created: list[UUID] = []
        for row in rows:
            draft = MealUpsertRequest.model_validate(row.parsed_payload)
            draft.source = MealSource.PDF
            meal = await meals.create(user_id, draft)
            await session.flush()
            row.committed_meal_id = meal.id
            created.append(meal.id)
        item.status = PdfImportStatus.COMMITTED
        return 201, _envelope(
            request,
            {
                "importId": item.id,
                "status": "COMMITTED",
                "createdMealEntryIds": created,
                "createdCount": len(created),
            },
        )

    status, body, replay = await execute_idempotent(
        user_id,
        key,
        "POST",
        request.url.path,
        payload.model_dump(mode="json", by_alias=True),
        work,
    )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
    return body
