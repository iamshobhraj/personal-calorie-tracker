from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, cast

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from src.config.settings import Settings
from src.persistence.models.enums import MealType
from src.shared.errors.api_error import ApiError

PDF_DIARY_V1 = (
    "pdf-diary-v1: transcribe diary rows in order. Preserve uncertainty, never invent "
    "nutrients or zeroes, and return incomplete rows rather than dropping them."
)


class PdfDiaryNutrient(BaseModel):
    code: str
    amount: Decimal = Field(ge=0)
    unit: Literal["kcal", "g", "mg", "mcg"]
    confidence: Decimal = Field(ge=0, le=1)


class PdfDiaryRow(BaseModel):
    source_row_number: int = Field(alias="sourceRowNumber", gt=0)
    meal_type: MealType | None = Field(alias="mealType")
    food_name: str | None = Field(alias="foodName", default=None, max_length=200)
    quantity: dict[str, Any] | None = None
    occurred_at: datetime | None = Field(alias="occurredAt", default=None)
    nutrients: list[PdfDiaryNutrient] = Field(default_factory=list, max_length=25)
    notes: str | None = Field(default=None, max_length=1000)
    confidence: Decimal = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=10)


class PdfDiaryExtraction(BaseModel):
    rows: list[PdfDiaryRow] = Field(max_length=500)
    warnings: list[str] = Field(default_factory=list, max_length=20)


class PdfDiaryProvider:
    def __init__(self, settings: Settings, limiter: asyncio.Semaphore) -> None:
        self._settings, self._limiter = settings, limiter

    async def extract(
        self, content: bytes, timezone: str, default_meal_type: MealType | None
    ) -> PdfDiaryExtraction:
        key = self._settings.gemini_api_key
        if key is None or not key.get_secret_value():
            raise ApiError(503, "AI_NOT_CONFIGURED", "PDF import is not configured.")
        prompt = (
            f"{PDF_DIARY_V1}\nTimezone: {timezone}. "
            f"Default meal type: {default_meal_type or 'none'}."
        )

        def generate() -> PdfDiaryExtraction:
            client = genai.Client(api_key=key.get_secret_value())
            response = client.models.generate_content(
                model=self._settings.gemini_model,
                contents=cast(
                    Any, [prompt, types.Part.from_bytes(data=content, mime_type="application/pdf")]
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=PdfDiaryExtraction
                ),
            )
            if response.text is None:
                raise ValueError("Provider did not return structured content")
            return PdfDiaryExtraction.model_validate_json(response.text)

        try:
            async with self._limiter:
                return await asyncio.wait_for(
                    asyncio.to_thread(generate), timeout=self._settings.pdf_parse_timeout_seconds
                )
        except ApiError:
            raise
        except (TimeoutError, ValueError) as exc:
            raise ApiError(503, "AI_UNAVAILABLE", "PDF import is temporarily unavailable.") from exc
        except Exception as exc:
            raise ApiError(502, "AI_UNAVAILABLE", "PDF import is temporarily unavailable.") from exc
