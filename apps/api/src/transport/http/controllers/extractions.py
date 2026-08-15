from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.bootstrap.dependencies import settings_dependency
from src.modules.extraction.application.service import ExtractionService
from src.persistence.models.enums import ImageKind
from src.persistence.models.upload import NutritionExtraction
from src.persistence.repositories.extractions import ExtractionRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.persistence.repositories.uploads import UploadRepository
from src.services.ai.providers.gemini import GeminiNutritionImageProvider
from src.services.files.image_validator import ValidatedImage
from src.shared.errors.api_error import ApiError


def extraction_resource(extraction: NutritionExtraction) -> dict[str, object]:
    return {
        "id": extraction.id,
        "status": extraction.status,
        "result": extraction.extracted_payload,
        "failure": {"code": extraction.failure_code, "message": extraction.failure_message}
        if extraction.failure_code
        else None,
    }


async def create_extraction(
    session: AsyncSession, user_id: UUID, image: ValidatedImage, image_kind: ImageKind
) -> dict[str, object]:
    settings = settings_dependency()
    extraction = await ExtractionService(
        session,
        UploadRepository(session),
        ExtractionRepository(session),
        NutrientRepository(session),
        GeminiNutritionImageProvider(settings),
        settings,
    ).create(user_id, image, image_kind)
    return extraction_resource(extraction)


async def get_extraction(
    session: AsyncSession, user_id: UUID, extraction_id: UUID
) -> dict[str, object]:
    extraction = await ExtractionRepository(session).get_owned(user_id, extraction_id)
    if extraction is None:
        raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
    return extraction_resource(extraction)
