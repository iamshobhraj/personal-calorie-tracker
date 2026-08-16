import asyncio
from typing import Any, cast

from google import genai
from google.genai import types

from src.config.settings import Settings
from src.persistence.models.enums import ImageKind
from src.persistence.seeds.nutrients import NUTRIENTS
from src.services.ai.limiter import AI_REQUEST_LIMITER
from src.services.ai.output_schema import AiNutritionResult
from src.services.ai.prompt_registry import NUTRITION_IMAGE_V1
from src.shared.errors.api_error import ApiError

_CANONICAL_NUTRIENT_CODES = tuple(nutrient[0] for nutrient in NUTRIENTS)
_NUTRIENT_CODE_INSTRUCTION = "Use only these canonical nutrient codes: " + ", ".join(
    _CANONICAL_NUTRIENT_CODES
)

_GEMINI_NUTRITION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "imageKind": {"type": "string", "enum": ["LABEL", "PLATE"]},
        "foodName": {"type": "string"},
        "quantity": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "unit": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["value", "unit"],
        },
        "nutrients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "enum": _CANONICAL_NUTRIENT_CODES},
                    "amount": {"type": "number"},
                    "unit": {"type": "string", "enum": ["kcal", "g", "mg", "mcg"]},
                    "confidence": {"type": "number"},
                },
                "required": ["code", "amount", "unit", "confidence"],
            },
        },
        "overallConfidence": {"type": "number"},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "requiresUserConfirmation": {"type": "boolean"},
    },
    "required": [
        "imageKind",
        "foodName",
        "quantity",
        "nutrients",
        "overallConfidence",
        "requiresUserConfirmation",
    ],
}


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
                        f"{NUTRITION_IMAGE_V1}\n{_NUTRIENT_CODE_INSTRUCTION}",
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ],
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=_GEMINI_NUTRITION_RESPONSE_SCHEMA,
                ),
            )
            if isinstance(response.parsed, AiNutritionResult):
                return response.parsed
            if response.parsed is not None:
                return AiNutritionResult.model_validate(response.parsed)
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
