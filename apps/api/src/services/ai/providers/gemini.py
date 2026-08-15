import asyncio
from typing import Any, cast

from google import genai
from google.genai import types

from src.config.settings import Settings
from src.persistence.models.enums import ImageKind
from src.services.ai.limiter import AI_REQUEST_LIMITER
from src.services.ai.output_schema import AiNutritionResult
from src.services.ai.prompt_registry import NUTRITION_IMAGE_V1
from src.shared.errors.api_error import ApiError


class GeminiNutritionImageProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def extract(
        self, image_bytes: bytes, mime_type: str, image_kind: ImageKind
    ) -> AiNutritionResult:
        key = self._settings.gemini_api_key
        if key is None or not key.get_secret_value():
            raise ApiError(503, "AI_NOT_CONFIGURED", "Image extraction is not configured.")

        def generate() -> AiNutritionResult:
            client = genai.Client(api_key=key.get_secret_value())
            response = client.models.generate_content(
                model=self._settings.gemini_model,
                contents=cast(
                    Any,
                    [
                        NUTRITION_IMAGE_V1,
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ],
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=AiNutritionResult
                ),
            )
            if response.text is None:
                raise ValueError("Provider did not return structured content")
            return AiNutritionResult.model_validate_json(response.text)

        try:
            async with AI_REQUEST_LIMITER:
                return await asyncio.wait_for(
                    asyncio.to_thread(generate), timeout=self._settings.gemini_timeout_seconds
                )
        except ApiError:
            raise
        except (TimeoutError, ValueError) as exc:
            raise ApiError(
                503, "AI_UNAVAILABLE", "Image extraction is temporarily unavailable."
            ) from exc
        except Exception as exc:
            raise ApiError(
                502, "AI_UNAVAILABLE", "Image extraction is temporarily unavailable."
            ) from exc
