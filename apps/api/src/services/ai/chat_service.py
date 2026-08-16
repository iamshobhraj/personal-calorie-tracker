from __future__ import annotations

import asyncio
import json
from typing import Any

from google import genai
from google.genai import types

from src.config.settings import Settings
from src.services.ai.chat_prompt_registry import NUTRITION_CHAT_V1
from src.shared.errors.api_error import ApiError

_CHAT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "mealDraft": {
            "type": "object",
            "properties": {
                "foodName": {"type": "string"},
                "mealType": {"type": "string", "enum": ["BREAKFAST", "LUNCH", "DINNER", "SNACKS"]},
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
                            "code": {
                                "type": "string",
                                "enum": [
                                    "ENERGY_KCAL",
                                    "PROTEIN",
                                    "CARBOHYDRATE",
                                    "FAT",
                                    "FIBER",
                                    "SUGAR",
                                    "SODIUM",
                                ],
                            },
                            "amount": {"type": "number"},
                        },
                        "required": ["code", "amount"],
                    },
                },
                "notes": {"type": "string"},
            },
            "required": ["foodName", "mealType", "quantity", "nutrients"],
        },
    },
    "required": ["reply"],
}


class NutritionChatProvider:
    """Bounded provider facade returning conversational replies and structured meal drafts."""

    def __init__(self, settings: Settings, limiter: asyncio.Semaphore) -> None:
        self._settings, self._limiter = settings, limiter

    async def respond(
        self, context: list[tuple[str, str]], nutrition_context: str | None = None
    ) -> dict[str, Any]:
        key = self._settings.gemini_api_key
        if key is None or not key.get_secret_value():
            raise ApiError(503, "AI_NOT_CONFIGURED", "Chat is not configured.")
        parts = [NUTRITION_CHAT_V1]
        if nutrition_context:
            parts.append(
                "CURRENT USER CONTEXT (use this to answer user questions about their daily "
                f"calories, meals, or goals):\n{nutrition_context}"
            )
        parts.append("\n".join(f"{role}: {content}" for role, content in context))
        prompt = "\n\n".join(parts)

        def generate() -> dict[str, Any]:
            client = genai.Client(api_key=key.get_secret_value())
            reply = client.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=_CHAT_RESPONSE_SCHEMA,
                ),
            )
            if not reply.text:
                raise ValueError("Provider did not return a response")
            try:
                data = json.loads(reply.text)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
            return {"reply": reply.text}

        try:
            async with self._limiter:
                return await asyncio.wait_for(
                    asyncio.to_thread(generate), timeout=self._settings.gemini_timeout_seconds
                )
        except ApiError:
            raise
        except (TimeoutError, ValueError) as exc:
            raise ApiError(503, "AI_UNAVAILABLE", "Chat is temporarily unavailable.") from exc
        except Exception as exc:
            raise ApiError(502, "AI_UNAVAILABLE", "Chat is temporarily unavailable.") from exc
