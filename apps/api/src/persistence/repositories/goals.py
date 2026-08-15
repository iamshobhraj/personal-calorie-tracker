from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.persistence.models.enums import GoalStatus
from src.persistence.models.goal import GoalNutrientTarget, HealthGoal


class GoalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _with_targets(self) -> Any:
        return selectinload(HealthGoal.targets).selectinload(GoalNutrientTarget.nutrient)

    async def current_on_date(self, user_id: UUID, on_date: date) -> HealthGoal | None:
        statement = (
            select(HealthGoal)
            .options(self._with_targets())
            .where(
                HealthGoal.user_id == user_id,
                HealthGoal.status == GoalStatus.ACTIVE,
                HealthGoal.effective_from <= on_date,
                (HealthGoal.effective_to.is_(None)) | (HealthGoal.effective_to > on_date),
            )
        )
        return await self._session.scalar(statement)

    async def list(
        self, user_id: UUID, status: GoalStatus | None, page: int, limit: int
    ) -> list[HealthGoal]:
        statement = (
            select(HealthGoal).options(self._with_targets()).where(HealthGoal.user_id == user_id)
        )
        if status is not None:
            statement = statement.where(HealthGoal.status == status)
        statement = (
            statement.order_by(HealthGoal.effective_from.desc(), HealthGoal.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list((await self._session.scalars(statement)).unique().all())

    def add(self, goal: HealthGoal) -> None:
        self._session.add(goal)

    async def get_owned(self, user_id: UUID, goal_id: UUID) -> HealthGoal | None:
        return await self._session.scalar(
            select(HealthGoal)
            .options(self._with_targets())
            .where(HealthGoal.id == goal_id, HealthGoal.user_id == user_id)
        )

    async def archive_or_delete(self, user_id: UUID, goal_id: UUID, archive: bool) -> bool:
        goal = await self.get_owned(user_id, goal_id)
        if goal is None:
            return False
        if archive:
            goal.status = GoalStatus.ARCHIVED
        else:
            await self._session.execute(
                delete(HealthGoal).where(HealthGoal.id == goal_id, HealthGoal.user_id == user_id)
            )
        return True
