from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.persistence.base import Base
from src.persistence.models.enums import ExtractionStatus, ImageKind, UploadPurpose, UploadStatus

if TYPE_CHECKING:
    from src.persistence.models.user import AppUser


class UploadObject(Base):
    __tablename__ = "upload_object"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        CheckConstraint("purpose IN ('NUTRITION_IMAGE','DIARY_PDF')", name="upload_purpose"),
        CheckConstraint(
            "status IN ('PENDING','UPLOADED','QUARANTINED','DELETED')", name="upload_status"
        ),
        CheckConstraint("byte_size > 0", name="upload_size"),
        Index("ix_upload_user_created", "user_id", text("created_at DESC"), text("id DESC")),
        Index("ix_upload_expiry", "expires_at", postgresql_where=text("status <> 'DELETED'")),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    purpose: Mapped[UploadPurpose] = mapped_column(String(16))
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    byte_size: Mapped[int] = mapped_column(BigInteger)
    sha256_hex: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[UploadStatus] = mapped_column(
        String(16), default=UploadStatus.PENDING, server_default=text("'PENDING'")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    user: Mapped[AppUser] = relationship(lazy="raise", back_populates="uploads")
    extraction: Mapped[NutritionExtraction | None] = relationship(
        lazy="raise",
        cascade="all, delete-orphan",
        uselist=False,
        overlaps="user,extractions,upload",
    )


class NutritionExtraction(Base):
    __tablename__ = "nutrition_extraction"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        UniqueConstraint("upload_id"),
        ForeignKeyConstraint(
            ("upload_id", "user_id"),
            ("upload_object.id", "upload_object.user_id"),
            ondelete="CASCADE",
        ),
        CheckConstraint("image_kind IN ('AUTO','LABEL','PLATE')", name="extraction_image_kind"),
        CheckConstraint("status IN ('PROCESSING','SUCCEEDED','FAILED')", name="extraction_status"),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1", name="extraction_confidence"
        ),
        CheckConstraint(
            "(status = 'SUCCEEDED' AND extracted_payload IS NOT NULL "
            "AND completed_at IS NOT NULL) OR status <> 'SUCCEEDED'",
            name="extraction_success_payload",
        ),
        Index(
            "ix_extraction_user_status_created",
            "user_id",
            "status",
            text("created_at DESC"),
            text("id DESC"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    upload_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    image_kind: Mapped[ImageKind] = mapped_column(String(16))
    status: Mapped[ExtractionStatus] = mapped_column(
        String(16), default=ExtractionStatus.PROCESSING, server_default=text("'PROCESSING'")
    )
    provider: Mapped[str | None] = mapped_column(String(40))
    model: Mapped[str | None] = mapped_column(String(80))
    prompt_version: Mapped[str | None] = mapped_column(String(32))
    schema_version: Mapped[int] = mapped_column(SmallInteger, default=1, server_default=text("1"))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    extracted_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    warnings: Mapped[list[Any]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    failure_code: Mapped[str | None] = mapped_column(String(60))
    failure_message: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[AppUser] = relationship(
        lazy="raise", back_populates="extractions", overlaps="extraction,upload"
    )
    upload: Mapped[UploadObject] = relationship(
        lazy="raise", back_populates="extraction", overlaps="user,extractions"
    )
