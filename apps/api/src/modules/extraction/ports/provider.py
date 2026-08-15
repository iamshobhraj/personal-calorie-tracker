from typing import Protocol

from src.persistence.models.enums import ImageKind
from src.services.ai.output_schema import AiNutritionResult


class NutritionImageProvider(Protocol):
    async def extract(
        self, image_bytes: bytes, mime_type: str, image_kind: ImageKind
    ) -> AiNutritionResult: ...
