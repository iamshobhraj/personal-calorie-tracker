from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.persistence.base import Base
from src.persistence.models.enums import UserStatus

if TYPE_CHECKING:
    from src.persistence.models.auth import AuthCredential, RefreshSession
    from src.persistence.models.goal import HealthGoal
    from src.persistence.models.meal import MealEntry
    from src.persistence.models.upload import NutritionExtraction, UploadObject


class AppUser(Base):
    __tablename__ = "app_user"
    __table_args__ = (
        CheckConstraint("deleted_at IS NULL OR status = 'DELETED'", name="deleted_status"),
        Index(
            "uq_app_user_email_active",
            text("lower(email)"),
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND email IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    external_subject: Mapped[str | None] = mapped_column(String(255), unique=True)
    email: Mapped[str | None] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(100))
    timezone_name: Mapped[str] = mapped_column(
        String(64), default="UTC", server_default=text("'UTC'")
    )
    status: Mapped[UserStatus] = mapped_column(
        String(16), default=UserStatus.ACTIVE, server_default=text("'ACTIVE'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    goals: Mapped[list[HealthGoal]] = relationship(lazy="raise", cascade="all, delete-orphan")
    meals: Mapped[list[MealEntry]] = relationship(
        lazy="raise", cascade="all, delete-orphan", overlaps="source_extraction"
    )
    uploads: Mapped[list[UploadObject]] = relationship(lazy="raise", cascade="all, delete-orphan")
    extractions: Mapped[list[NutritionExtraction]] = relationship(
        lazy="raise", cascade="all, delete-orphan", overlaps="extraction,upload"
    )
    credential: Mapped[AuthCredential | None] = relationship(
        lazy="raise", cascade="all, delete-orphan", uselist=False
    )
    refresh_sessions: Mapped[list[RefreshSession]] = relationship(
        lazy="raise", cascade="all, delete-orphan"
    )
