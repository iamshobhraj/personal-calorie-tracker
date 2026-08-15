from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.persistence.models.bonus import PdfImport, PdfImportRow
from src.persistence.models.enums import MealType, PdfImportStatus, UploadPurpose, UploadStatus
from src.persistence.models.upload import UploadObject
from src.persistence.repositories.pdf_imports import PdfImportRepository
from src.persistence.repositories.uploads import UploadRepository
from src.services.ai.limiter import AI_REQUEST_LIMITER
from src.services.ai.pdf_diary_service import PdfDiaryProvider
from src.services.files.pdf_validator import ValidatedPdf
from src.shared.errors.api_error import ApiError
from src.transport.http.requests.meals import MealUpsertRequest


def import_resource(item: PdfImport) -> dict[str, object]:
    return {
        "id": item.id,
        "status": item.status,
        "summary": {
            "totalRows": item.total_rows,
            "validRows": item.valid_rows,
            "invalidRows": item.invalid_rows,
        },
    }


def row_resource(row: PdfImportRow) -> dict[str, object]:
    return {
        "rowId": row.id,
        "sourceRowNumber": row.source_row_number,
        "selected": row.selected,
        "parsedMeal": row.parsed_payload or None,
        "validationErrors": row.validation_errors,
        "committedMealId": row.committed_meal_id,
    }


def _draft(row: object, timezone: str) -> dict[str, object]:
    raw = row.model_dump(by_alias=True, mode="json")  # type: ignore[attr-defined]
    return {
        "mealType": raw.get("mealType"),
        "foodName": raw.get("foodName"),
        "quantity": raw.get("quantity"),
        "occurredAt": raw.get("occurredAt"),
        "timezone": timezone,
        "source": "PDF",
        "sourceExtractionId": None,
        "notes": raw.get("notes"),
        "nutrients": [
            {
                "code": item["code"],
                "amount": item["amount"],
                "confidence": item["confidence"],
                "provenance": "PDF_AI",
            }
            for item in raw.get("nutrients", [])
        ],
    }


async def create_import(
    session: AsyncSession,
    user_id: UUID,
    pdf: ValidatedPdf,
    timezone: str,
    default_meal_type: MealType | None,
    settings: Settings,
) -> dict[str, object]:
    repository = PdfImportRepository(session)
    if await repository.count_successes_today(user_id) >= settings.pdf_successes_per_user_per_day:
        raise ApiError(429, "PDF_DAILY_LIMIT", "The daily PDF import limit has been reached.")
    upload = UploadObject(
        user_id=user_id,
        purpose=UploadPurpose.DIARY_PDF,
        storage_key=f"transient/pdf/{uuid4()}",
        mime_type="application/pdf",
        byte_size=pdf.byte_size,
        sha256_hex=pdf.sha256_hex,
        status=UploadStatus.UPLOADED,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    UploadRepository(session).add(upload)
    await session.flush()
    item = PdfImport(user_id=user_id, upload_id=upload.id)
    repository.add(item)
    await session.flush()
    try:
        extraction = await PdfDiaryProvider(settings, AI_REQUEST_LIMITER).extract(
            pdf.path.read_bytes(), timezone, default_meal_type
        )
        rows: list[PdfImportRow] = []
        valid = 0
        for parsed in extraction.rows[: settings.pdf_max_rows]:
            draft = _draft(parsed, timezone)
            errors: list[dict[str, str]] = []
            try:
                MealUpsertRequest.model_validate(draft)
                valid += 1
            except ValueError as exc:
                errors.append({"code": "VALIDATION_FAILED", "message": str(exc)})
            rows.append(
                PdfImportRow(
                    import_id=item.id,
                    user_id=user_id,
                    source_row_number=parsed.source_row_number,
                    parsed_payload=draft,
                    validation_errors=errors,
                    selected=not errors,
                )
            )
        item.total_rows, item.valid_rows, item.invalid_rows = len(rows), valid, len(rows) - valid
        item.status, item.completed_at = PdfImportStatus.READY, datetime.now(UTC)
        repository.add_rows(rows)
        return import_resource(item)
    except ApiError:
        item.status, item.completed_at = PdfImportStatus.FAILED, datetime.now(UTC)
        item.failure_message = "The PDF could not be parsed."
        raise
    finally:
        pdf.path.unlink(missing_ok=True)
        upload.status = UploadStatus.DELETED


async def get_import(session: AsyncSession, user_id: UUID, import_id: UUID) -> dict[str, object]:
    item = await PdfImportRepository(session).get_owned(user_id, import_id)
    if item is None:
        raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
    return import_resource(item)
