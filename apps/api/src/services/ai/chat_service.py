from __future__ import annotations

import asyncio

from google import genai

from src.config.settings import Settings
from src.services.ai.chat_prompt_registry import NUTRITION_CHAT_V1
from src.shared.errors.api_error import ApiError


class NutritionChatProvider:
    """Text-only bounded provider facade; mutations remain application-owned drafts."""

    def __init__(self, settings: Settings, limiter: asyncio.Semaphore) -> None:
        self._settings, self._limiter = settings, limiter

    async def respond(self, context: list[tuple[str, str]]) -> str:
        key = self._settings.gemini_api_key
        if key is None or not key.get_secret_value():
            raise ApiError(503, "AI_NOT_CONFIGURED", "Chat is not configured.")
        prompt = (
            NUTRITION_CHAT_V1
            + "\n\n"
            + "\n".join(f"{role}: {content}" for role, content in context)
        )

        def generate() -> str:
            reply = genai.Client(api_key=key.get_secret_value()).models.generate_content(
                model=self._settings.gemini_model, contents=prompt
            )
            if not reply.text:
                raise ValueError("Provider did not return a response")
            return reply.text[:8000]

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
