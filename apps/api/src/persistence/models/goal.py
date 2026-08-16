from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.persistence.base import Base
from src.persistence.models.enums import GoalStatus, TargetKind

if TYPE_CHECKING:
    from src.persistence.models.nutrition import NutrientDefinition
    from src.persistence.models.user import AppUser


class HealthGoal(Base):
    __tablename__ = "health_goal"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from", name="goal_period"
        ),
        CheckConstraint("target_weight_kg IS NULL OR target_weight_kg > 0", name="goal_weight"),
        CheckConstraint("status IN ('ACTIVE','ARCHIVED')", name="goal_status"),
        ExcludeConstraint(
            ("user_id", "="),
            (
                text("daterange(effective_from, COALESCE(effective_to, 'infinity'::date), '[)')"),
                "&&",
            ),
            name="no_overlapping_active_goals",
            using="gist",
            where=text("status = 'ACTIVE'"),
        ),
        Index(
            "ix_health_goal_user_current",
            "user_id",
            text("effective_from DESC"),
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(
        String(100), default="Daily goal", server_default=text("'Daily goal'")
    )
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    status: Mapped[GoalStatus] = mapped_column(
        String(16), default=GoalStatus.ACTIVE, server_default=text("'ACTIVE'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    user: Mapped[AppUser] = relationship(lazy="raise", back_populates="goals")
    targets: Mapped[list[GoalNutrientTarget]] = relationship(
        lazy="raise", cascade="all, delete-orphan"
    )


class GoalNutrientTarget(Base):
    __tablename__ = "goal_nutrient_target"
    __table_args__ = (
        ForeignKeyConstraint(
            ("goal_id", "user_id"), ("health_goal.id", "health_goal.user_id"), ondelete="CASCADE"
        ),
        CheckConstraint("target_amount >= 0", name="goal_target_nonnegative"),
        CheckConstraint("target_kind IN ('TARGET','MINIMUM','MAXIMUM')", name="goal_target_kind"),
        Index("ix_goal_target_user_nutrient", "user_id", "nutrient_id", "goal_id"),
    )

    goal_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    nutrient_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("nutrient_definition.id", ondelete="RESTRICT"), primary_key=True
    )
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    target_kind: Mapped[TargetKind] = mapped_column(
        String(10), default=TargetKind.TARGET, server_default=text("'TARGET'")
    )

    goal: Mapped[HealthGoal] = relationship(lazy="raise", back_populates="targets")
    nutrient: Mapped[NutrientDefinition] = relationship(lazy="raise", back_populates="goal_targets")
