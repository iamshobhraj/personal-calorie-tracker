from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile

from src.bootstrap.dependencies import (
    current_user_id,
    execute_idempotent,
    idempotency_key,
    tenant_transaction,
)
from src.config.settings import get_settings
from src.persistence.models.enums import ImageKind
from src.services.files.image_validator import validate_image
from src.services.files.temp_storage import temporary_directory
from src.transport.http.controllers import extractions as controller

router = APIRouter(prefix="/nutrition-extractions", tags=["nutrition extractions"])


def _envelope(request: Request, data: object) -> dict[str, object]:
    return {"data": data, "meta": {"requestId": request.state.request_id}}


@router.post("", operation_id="createNutritionExtraction")
async def create_extraction(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    imageKind: ImageKind = Form(default=ImageKind.AUTO),
    key: str = Depends(idempotency_key),
    user_id=Depends(current_user_id),
):
    settings = get_settings()
    async with temporary_directory(settings.upload_temp_dir) as directory:
        image = await validate_image(
            file, directory, settings.max_image_bytes, settings.max_image_pixels
        )

        async def work(session):
            return 200, _envelope(
                request, await controller.create_extraction(session, user_id, image, imageKind)
            )

        status, body, replay = await execute_idempotent(
            user_id,
            key,
            "POST",
            request.url.path,
            {"sha256": image.sha256_hex, "imageKind": imageKind},
            work,
        )
    response.status_code = status
    if replay:
        response.headers["Idempotency-Replayed"] = "true"
        body["meta"]["requestId"] = request.state.request_id
    return body


@router.get("/{extraction_id}", operation_id="getNutritionExtraction")
async def get_extraction(request: Request, extraction_id: UUID, user_id=Depends(current_user_id)):
    async with tenant_transaction(user_id) as session:
        data = await controller.get_extraction(session, user_id, extraction_id)
    return _envelope(request, data)
