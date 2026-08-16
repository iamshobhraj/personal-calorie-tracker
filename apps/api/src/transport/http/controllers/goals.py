from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.goals.application.service import GoalService
from src.persistence.models.goal import HealthGoal
from src.persistence.repositories.goals import GoalRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.transport.http.requests.goals import GoalCreateRequest


def goal_resource(goal: HealthGoal) -> dict[str, object]:
    return {
        "id": goal.id,
        "name": goal.name,
        "effectiveFrom": goal.effective_from,
        "effectiveTo": goal.effective_to,
        "targetWeightKg": goal.target_weight_kg,
        "status": goal.status,
        "targets": [
            {
                "nutrientCode": target.nutrient.code,
                "targetAmount": target.target_amount,
                "unit": target.nutrient.canonical_unit,
                "targetKind": target.target_kind,
            }
            for target in goal.targets
        ],
        "createdAt": goal.created_at,
        "updatedAt": goal.updated_at,
    }


def _service(session: AsyncSession) -> GoalService:
    return GoalService(GoalRepository(session), NutrientRepository(session))


async def create_goal(
    session: AsyncSession, user_id: UUID, request: GoalCreateRequest
) -> dict[str, object]:
    goal = await _service(session).create(user_id, request)
    await session.flush()
    return goal_resource(goal)


async def current_goal(session: AsyncSession, user_id: UUID, on_date: date) -> dict[str, object]:
    return goal_resource(await _service(session).current(user_id, on_date))


async def replace_goal(
    session: AsyncSession, user_id: UUID, goal_id: UUID, request: GoalCreateRequest
) -> dict[str, object]:
    goal, replaced = await _service(session).replace(user_id, goal_id, request)
    await session.flush()
    return {"goal": goal_resource(goal), "replacedGoalId": replaced}


async def delete_goal(
    session: AsyncSession, user_id: UUID, goal_id: UUID, today: date
) -> dict[str, object]:
    await _service(session).delete(user_id, goal_id, today)
    return {"id": goal_id, "status": "ARCHIVED"}
