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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.persistence.base import Base
from src.persistence.models.enums import MealSource, MealType, NutrientProvenance

if TYPE_CHECKING:
    from src.persistence.models.nutrition import NutrientDefinition
    from src.persistence.models.upload import NutritionExtraction
    from src.persistence.models.user import AppUser


class MealEntry(Base):
    __tablename__ = "meal_entry"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        ForeignKeyConstraint(
            ("source_extraction_id", "user_id"),
            ("nutrition_extraction.id", "nutrition_extraction.user_id"),
            ondelete="SET NULL (source_extraction_id)",
        ),
        CheckConstraint("meal_type IN ('BREAKFAST','LUNCH','DINNER','SNACKS')", name="meal_type"),
        CheckConstraint("length(trim(food_name)) > 0", name="meal_food_name"),
        CheckConstraint("quantity > 0", name="meal_quantity"),
        CheckConstraint("source IN ('MANUAL','IMAGE','PDF','CHAT')", name="meal_source"),
        CheckConstraint(
            "(source = 'IMAGE') = (source_extraction_id IS NOT NULL)", name="meal_image_source"
        ),
        Index(
            "ix_meal_user_date_page",
            "user_id",
            text("local_date DESC"),
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index(
            "ix_meal_user_type_date_page",
            "user_id",
            "meal_type",
            text("local_date DESC"),
            text("occurred_at DESC"),
            text("id DESC"),
        ),
        Index("ix_meal_user_occurred", "user_id", text("occurred_at DESC"), text("id DESC")),
        Index(
            "uq_meal_source_extraction",
            "source_extraction_id",
            unique=True,
            postgresql_where=text("source_extraction_id IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    meal_type: Mapped[MealType] = mapped_column(String(12))
    food_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    quantity_unit: Mapped[str] = mapped_column(String(30))
    portion_description: Mapped[str | None] = mapped_column(String(200))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    entry_timezone: Mapped[str] = mapped_column(String(64))
    local_date: Mapped[date] = mapped_column(Date)
    source: Mapped[MealSource] = mapped_column(
        String(12), default=MealSource.MANUAL, server_default=text("'MANUAL'")
    )
    source_extraction_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    notes: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    user: Mapped[AppUser] = relationship(lazy="raise", back_populates="meals")
    source_extraction: Mapped[NutritionExtraction | None] = relationship(
        lazy="raise", overlaps="user,meals"
    )
    nutrients: Mapped[list[MealEntryNutrient]] = relationship(
        lazy="raise", cascade="all, delete-orphan"
    )


class MealEntryNutrient(Base):
    __tablename__ = "meal_entry_nutrient"
    __table_args__ = (
        ForeignKeyConstraint(
            ("meal_entry_id", "user_id"),
            ("meal_entry.id", "meal_entry.user_id"),
            ondelete="CASCADE",
        ),
        CheckConstraint("amount >= 0", name="meal_nutrient_amount"),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1", name="meal_nutrient_confidence"
        ),
        CheckConstraint(
            "provenance IN ('USER','LABEL_AI','PLATE_AI','PDF_AI')", name="meal_nutrient_provenance"
        ),
        Index("ix_meal_nutrient_report", "user_id", "nutrient_id", "meal_entry_id"),
    )

    meal_entry_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    nutrient_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("nutrient_definition.id", ondelete="RESTRICT"), primary_key=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    provenance: Mapped[NutrientProvenance] = mapped_column(
        String(16), default=NutrientProvenance.USER, server_default=text("'USER'")
    )

    meal_entry: Mapped[MealEntry] = relationship(lazy="raise", back_populates="nutrients")
    nutrient: Mapped[NutrientDefinition] = relationship(
        lazy="raise", back_populates="meal_nutrients"
    )
