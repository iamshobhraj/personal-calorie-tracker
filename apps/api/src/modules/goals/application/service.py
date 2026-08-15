from datetime import date
from uuid import UUID

from src.persistence.models.enums import GoalStatus
from src.persistence.models.goal import GoalNutrientTarget, HealthGoal
from src.persistence.repositories.goals import GoalRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.shared.errors.api_error import ApiError
from src.transport.http.requests.goals import GoalCreateRequest


class GoalService:
    def __init__(self, goals: GoalRepository, nutrients: NutrientRepository) -> None:
        self._goals, self._nutrients = goals, nutrients

    async def _targets(self, user_id: UUID, request: GoalCreateRequest) -> list[GoalNutrientTarget]:
        definitions = await self._nutrients.get_mapping_by_codes(
            item.nutrient_code for item in request.targets
        )
        if len(definitions) != len(request.targets):
            raise ApiError(422, "UNKNOWN_NUTRIENT", "One or more nutrient codes are invalid.")
        targets: list[GoalNutrientTarget] = []
        for item in request.targets:
            definition = definitions[item.nutrient_code]
            if not definition.is_active:
                raise ApiError(422, "UNKNOWN_NUTRIENT", "One or more nutrient codes are invalid.")
            targets.append(
                GoalNutrientTarget(
                    user_id=user_id,
                    nutrient_id=definition.id,
                    target_amount=item.target_amount,
                    target_kind=item.target_kind,
                    nutrient=definition,
                )
            )
        return targets

    async def create(self, user_id: UUID, request: GoalCreateRequest) -> HealthGoal:
        current = await self._goals.current_on_date(user_id, request.effective_from)
        if current is not None:
            if current.effective_to is None and current.effective_from < request.effective_from:
                current.effective_to = request.effective_from
            else:
                raise ApiError(
                    409, "GOAL_PERIOD_CONFLICT", "This goal overlaps an active goal period."
                )
        goal = HealthGoal(
            user_id=user_id,
            name=request.name,
            effective_from=request.effective_from,
            effective_to=request.effective_to,
            target_weight_kg=request.target_weight_kg,
            status=GoalStatus.ACTIVE,
        )
        goal.targets = await self._targets(user_id, request)
        self._goals.add(goal)
        return goal

    async def current(self, user_id: UUID, on_date: date) -> HealthGoal:
        goal = await self._goals.current_on_date(user_id, on_date)
        if goal is None:
            raise ApiError(404, "GOAL_NOT_FOUND", "No current goal was found.")
        return goal

    async def replace(
        self, user_id: UUID, goal_id: UUID, request: GoalCreateRequest
    ) -> tuple[HealthGoal, UUID]:
        existing = await self._goals.get_owned(user_id, goal_id)
        if existing is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        existing.status = GoalStatus.ARCHIVED
        created = await self.create(user_id, request)
        return created, existing.id

    async def delete(self, user_id: UUID, goal_id: UUID, today: date) -> None:
        existing = await self._goals.get_owned(user_id, goal_id)
        if existing is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        await self._goals.archive_or_delete(user_id, goal_id, existing.effective_from <= today)
