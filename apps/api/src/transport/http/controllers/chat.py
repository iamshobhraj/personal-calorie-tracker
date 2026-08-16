from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.persistence.models.bonus import ChatConfirmation, ChatMessage, ChatSession
from src.persistence.models.enums import ChatRole
from src.persistence.repositories.chat import ChatRepository
from src.persistence.repositories.users import UserRepository
from src.services.ai.chat_service import NutritionChatProvider
from src.services.ai.limiter import AI_REQUEST_LIMITER
from src.shared.errors.api_error import ApiError
from src.shared.security.confirmation_tokens import constraints_hash, issue_confirmation


def session_resource(item: ChatSession) -> dict[str, object]:
    return {
        "id": item.id,
        "title": item.title,
        "createdAt": item.created_at,
        "updatedAt": item.updated_at,
    }


def message_resource(item: ChatMessage) -> dict[str, object]:
    actions = (
        (item.tool_payload or {}).get("actions", []) if isinstance(item.tool_payload, dict) else []
    )
    return {
        "id": item.id,
        "role": item.role,
        "content": item.content,
        "createdAt": item.created_at,
        "actions": actions,
    }


async def create_session(
    session: AsyncSession, user_id: UUID, title: str | None
) -> dict[str, object]:
    item = ChatSession(user_id=user_id, title=title)
    ChatRepository(session).add(item)
    await session.flush()
    return session_resource(item)


async def _build_user_nutrition_context(
    session: AsyncSession, user_id: UUID
) -> tuple[str, str, datetime]:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    from src.persistence.repositories.goals import GoalRepository
    from src.persistence.repositories.meals import MealRepository

    user = await UserRepository(session).get_active(user_id)
    timezone_name = user.timezone_name if user else "UTC"
    try:
        now_zoned = datetime.now(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        now_zoned = datetime.now(UTC)
        timezone_name = "UTC"

    today_date = now_zoned.date()

    goal = await GoalRepository(session).current_on_date(user_id, today_date)
    meals = await MealRepository(session).list_range(user_id, today_date, today_date, None, 1, 50)

    lines: list[str] = [
        f"Today's date: {today_date} ({timezone_name})",
    ]

    if goal:
        target_parts = [
            f"{t.nutrient.name}: {t.target_amount} {t.nutrient.canonical_unit}"
            for t in goal.targets
            if t.nutrient is not None
        ]
        lines.append(
            f"Active Daily Goal ('{goal.name}'): "
            + (", ".join(target_parts) if target_parts else "No specific targets")
        )
    else:
        lines.append("Active Daily Goal: None set")

    if meals:
        total_cals = 0.0
        total_prot = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        meal_lines: list[str] = []
        for m in meals:
            cals = 0.0
            prot = 0.0
            carbs = 0.0
            fat = 0.0
            for n in m.nutrients:
                if n.nutrient is not None and n.amount is not None:
                    amt = float(n.amount)
                    if n.nutrient.code == "ENERGY_KCAL":
                        cals += amt
                    elif n.nutrient.code == "PROTEIN":
                        prot += amt
                    elif n.nutrient.code == "CARBOHYDRATE":
                        carbs += amt
                    elif n.nutrient.code == "FAT":
                        fat += amt
            total_cals += cals
            total_prot += prot
            total_carbs += carbs
            total_fat += fat
            meal_type_str = m.meal_type.value if hasattr(m.meal_type, "value") else str(m.meal_type)
            macro_str = (
                f"{round(cals)} kcal, {round(prot, 1)}g P, {round(carbs, 1)}g C, {round(fat, 1)}g F"
            )
            meal_lines.append(f"- {meal_type_str}: {m.food_name} ({macro_str})")
        count = len(meals)
        totals_str = (
            f"Total Logged Today ({count} meal{'s' if count > 1 else ''}): "
            f"{round(total_cals)} kcal, {round(total_prot, 1)}g protein, "
            f"{round(total_carbs, 1)}g carbs, {round(total_fat, 1)}g fat."
        )
        lines.append(totals_str)
        lines.extend(meal_lines)
    else:
        lines.append("Total Logged Today: 0 kcal (No meals logged yet today).")

    return "\n".join(lines), timezone_name, now_zoned


async def create_message(
    session: AsyncSession, user_id: UUID, session_id: UUID, message: str, settings: Settings
) -> dict[str, object]:
    repo = ChatRepository(session)
    item = await repo.session(user_id, session_id)
    if item is None:
        raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
    history = await repo.messages(user_id, session_id)
    user_message = ChatMessage(
        user_id=user_id, session_id=session_id, role=ChatRole.USER, content=message
    )
    repo.add(user_message)
    await session.flush()
    compact = [
        (row.role.lower(), row.content)
        for row in [*history, user_message]
        if row.role != ChatRole.TOOL
    ]
    total = 0
    context: list[tuple[str, str]] = []
    for role, content in reversed(compact[-20:]):
        remaining = 12_000 - total
        if remaining <= 0:
            break
        context.append((role, content[-remaining:]))
        total += min(len(content), remaining)

    nutrition_context, timezone_name, now_zoned = await _build_user_nutrition_context(
        session, user_id
    )

    response_data = await NutritionChatProvider(settings, AI_REQUEST_LIMITER).respond(
        list(reversed(context)), nutrition_context=nutrition_context
    )
    reply_text = str(response_data.get("reply", "")).strip() or "Here is what I calculated for you."
    draft_data = response_data.get("mealDraft")

    actions: list[dict[str, Any]] = []
    if isinstance(draft_data, dict) and draft_data.get("foodName") and draft_data.get("nutrients"):
        digest = constraints_hash(
            {"type": "CREATE_MEAL", "sessionId": str(session_id), "source": "CHAT"}
        )
        token, jti, expires = issue_confirmation(
            settings, user_id, session_id, "CREATE_MEAL", digest
        )
        confirmation_entry = ChatConfirmation(
            jti=jti,
            user_id=user_id,
            session_id=session_id,
            action="CREATE_MEAL",
            draft_constraints_hash=digest,
            expires_at=expires,
        )
        repo.add(confirmation_entry)

        actions.append(
            {
                "type": "MEAL_DRAFT",
                "confirmationToken": token,
                "draft": {
                    "mealType": draft_data.get("mealType", "SNACKS"),
                    "foodName": str(draft_data["foodName"]).strip(),
                    "quantity": {
                        "value": float(draft_data.get("quantity", {}).get("value", 1) or 1),
                        "unit": str(
                            draft_data.get("quantity", {}).get("unit", "serving") or "serving"
                        ),
                        "description": draft_data.get("quantity", {}).get("description"),
                    },
                    "occurredAt": now_zoned.isoformat(),
                    "timezone": timezone_name,
                    "source": "CHAT",
                    "sourceExtractionId": None,
                    "notes": draft_data.get("notes"),
                    "nutrients": [
                        {
                            "code": str(n["code"]),
                            "amount": float(n["amount"]),
                        }
                        for n in draft_data["nutrients"]
                        if isinstance(n, dict) and "code" in n and "amount" in n
                    ],
                },
            }
        )

    assistant = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        role=ChatRole.ASSISTANT,
        content=reply_text,
        tool_payload={"actions": actions} if actions else None,
    )
    repo.add(assistant)
    item.updated_at = datetime.now(UTC)
    await session.flush()
    return {
        "userMessageId": user_message.id,
        "assistantMessage": message_resource(assistant),
        "actions": actions,
    }
