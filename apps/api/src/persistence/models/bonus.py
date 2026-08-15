from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.persistence.base import Base
from src.persistence.models.enums import ChatRole, PdfImportStatus


class PdfImport(Base):
    __tablename__ = "pdf_import"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        UniqueConstraint("upload_id"),
        ForeignKeyConstraint(
            ("upload_id", "user_id"),
            ("upload_object.id", "upload_object.user_id"),
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "status IN ('PROCESSING','READY','COMMITTED','FAILED','CANCELLED')",
            name="pdf_import_status",
        ),
        CheckConstraint("valid_rows + invalid_rows <= total_rows", name="pdf_import_counts"),
        Index("ix_pdf_import_user_created", "user_id", text("created_at DESC"), text("id DESC")),
    )
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    upload_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    status: Mapped[PdfImportStatus] = mapped_column(String(16), default=PdfImportStatus.PROCESSING)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    failure_message: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PdfImportRow(Base):
    __tablename__ = "pdf_import_row"
    __table_args__ = (
        ForeignKeyConstraint(
            ("import_id", "user_id"), ("pdf_import.id", "pdf_import.user_id"), ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ("committed_meal_id", "user_id"),
            ("meal_entry.id", "meal_entry.user_id"),
            ondelete="SET NULL (committed_meal_id)",
        ),
        UniqueConstraint("import_id", "source_row_number"),
        CheckConstraint("source_row_number > 0", name="pdf_import_row_number"),
        Index("ix_import_rows_page", "user_id", "import_id", "source_row_number", "id"),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    import_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    source_row_number: Mapped[int] = mapped_column(Integer)
    parsed_payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    validation_errors: Mapped[list[Any]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    selected: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    committed_meal_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class ChatSession(Base):
    __tablename__ = "chat_session"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        Index("ix_chat_session_page", "user_id", text("updated_at DESC"), text("id DESC")),
    )
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    title: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )


class ChatMessage(Base):
    __tablename__ = "chat_message"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        ForeignKeyConstraint(
            ("session_id", "user_id"),
            ("chat_session.id", "chat_session.user_id"),
            ondelete="CASCADE",
        ),
        CheckConstraint("role IN ('USER','ASSISTANT','TOOL')", name="chat_message_role"),
        CheckConstraint("length(content) <= 10000", name="chat_message_content"),
        Index("ix_chat_message_page", "user_id", "session_id", "created_at", "id"),
    )
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    session_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    role: Mapped[ChatRole] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    tool_name: Mapped[str | None] = mapped_column(String(80))
    tool_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class ChatConfirmation(Base):
    __tablename__ = "chat_confirmation"
    __table_args__ = (
        UniqueConstraint("jti", "user_id"),
        ForeignKeyConstraint(
            ("session_id", "user_id"),
            ("chat_session.id", "chat_session.user_id"),
            ondelete="CASCADE",
        ),
        CheckConstraint("action = 'CREATE_MEAL'", name="chat_confirmation_action"),
        CheckConstraint("expires_at > created_at", name="chat_confirmation_expiry"),
        CheckConstraint(
            "consumed_at IS NULL OR consumed_at >= created_at", name="chat_confirmation_consumed"
        ),
        Index(
            "ix_chat_confirmation_active",
            "user_id",
            "expires_at",
            "jti",
            postgresql_where=text("consumed_at IS NULL"),
        ),
    )
    jti: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE")
    )
    session_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(24))
    draft_constraints_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
