from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.modules.extraction.ports.provider import NutritionImageProvider
from src.persistence.models.enums import ExtractionStatus, ImageKind, UploadPurpose, UploadStatus
from src.persistence.models.upload import NutritionExtraction, UploadObject
from src.persistence.repositories.extractions import ExtractionRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.persistence.repositories.uploads import UploadRepository
from src.services.ai.nutrition_image_service import NutritionImageService
from src.services.files.image_validator import ValidatedImage
from src.shared.errors.api_error import ApiError

_semaphore = __import__("asyncio").Semaphore(2)


class ExtractionService:
    def __init__(
        self,
        session: AsyncSession,
        uploads: UploadRepository,
        extractions: ExtractionRepository,
        nutrients: NutrientRepository,
        provider: NutritionImageProvider,
        settings: Settings,
    ) -> None:
        (
            self._session,
            self._uploads,
            self._extractions,
            self._nutrients,
            self._provider,
            self._settings,
        ) = session, uploads, extractions, nutrients, provider, settings

    async def create(
        self, user_id: UUID, image: ValidatedImage, image_kind: ImageKind
    ) -> NutritionExtraction:
        now = datetime.now(UTC)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if (
            await self._extractions.count_successful_for_day(
                user_id, day_start, day_start + timedelta(days=1)
            )
            >= self._settings.ai_successes_per_user_per_day
        ):
            raise ApiError(
                429, "AI_QUOTA_EXCEEDED", "The daily image extraction limit has been reached."
            )
        upload = UploadObject(
            user_id=user_id,
            purpose=UploadPurpose.NUTRITION_IMAGE,
            storage_key=f"temporary/{uuid4()}",
            mime_type=image.mime_type,
            byte_size=image.byte_size,
            sha256_hex=image.sha256_hex,
            status=UploadStatus.UPLOADED,
            expires_at=now + timedelta(hours=1),
        )
        self._uploads.add(upload)
        await self._session.flush()
        extraction = NutritionExtraction(
            user_id=user_id,
            upload_id=upload.id,
            image_kind=image_kind,
            status=ExtractionStatus.PROCESSING,
            provider="gemini",
            model=self._settings.gemini_model,
            prompt_version="nutrition-image-v1",
        )
        self._extractions.add(extraction)
        await self._session.flush()
        try:
            async with _semaphore:
                result = await self._provider.extract(
                    image.path.read_bytes(), image.mime_type, image_kind
                )
            result = await NutritionImageService(self._nutrients).validate(result, image_kind)
            payload = result.model_dump(by_alias=True, mode="json")
            provenance = "LABEL_AI" if result.image_kind == "LABEL" else "PLATE_AI"
            for nutrient in payload["nutrients"]:
                nutrient["provenance"] = provenance
            (
                extraction.status,
                extraction.extracted_payload,
                extraction.completed_at,
                extraction.confidence,
                extraction.warnings,
            ) = (
                ExtractionStatus.SUCCEEDED,
                payload,
                datetime.now(UTC),
                result.overall_confidence,
                payload["warnings"],
            )
        except ApiError as error:
            extraction.status, extraction.failure_code, extraction.failure_message = (
                ExtractionStatus.FAILED,
                error.code,
                error.message,
            )
            raise
        finally:
            upload.status = UploadStatus.DELETED
            image.path.unlink(missing_ok=True)
        return extraction
