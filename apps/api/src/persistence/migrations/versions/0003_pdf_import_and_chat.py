# ruff: noqa: E501
"""Add tenant-isolated PDF import and constrained chat records.

Revision ID: 0003_pdf_import_and_chat
Revises: 0002_refresh_lookup
"""

from __future__ import annotations

import os
import re

from alembic import op

revision = "0003_pdf_import_and_chat"
down_revision = "0002_refresh_lookup"
branch_labels = None
depends_on = None

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
_TABLES = ("pdf_import", "pdf_import_row", "chat_session", "chat_message", "chat_confirmation")


def _runtime_role() -> str:
    role = os.environ.get("APP_DB_USER", "calorie_app")
    if not _IDENTIFIER.fullmatch(role):
        raise ValueError("APP_DB_USER must be a simple lowercase PostgreSQL identifier")
    return role


def _ensure_role(role: str) -> None:
    op.execute(f"""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
        CREATE ROLE "{role}";
      END IF;
    END
    $$;
    """)


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS pdf_import (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
      upload_id uuid NOT NULL, status varchar(16) NOT NULL DEFAULT 'PROCESSING', total_rows integer NOT NULL DEFAULT 0,
      valid_rows integer NOT NULL DEFAULT 0, invalid_rows integer NOT NULL DEFAULT 0,
      failure_message varchar(500), created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz,
      UNIQUE (id,user_id), UNIQUE (upload_id),
      CONSTRAINT pdf_import_upload_user_fk FOREIGN KEY (upload_id,user_id) REFERENCES upload_object(id,user_id) ON DELETE CASCADE,
      CONSTRAINT pdf_import_status CHECK (status IN ('PROCESSING','READY','COMMITTED','FAILED','CANCELLED')),
      CONSTRAINT pdf_import_counts CHECK (total_rows >= 0 AND valid_rows >= 0 AND invalid_rows >= 0 AND valid_rows + invalid_rows <= total_rows)
    )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_pdf_import_user_created "
        "ON pdf_import(user_id, created_at DESC, id DESC)"
    )
    op.execute("""
    CREATE TABLE IF NOT EXISTS pdf_import_row (
      id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, import_id uuid NOT NULL, user_id uuid NOT NULL,
      source_row_number integer NOT NULL, parsed_payload jsonb NOT NULL, validation_errors jsonb NOT NULL DEFAULT '[]'::jsonb, selected boolean NOT NULL DEFAULT true,
      committed_meal_id uuid, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(import_id, source_row_number),
      CONSTRAINT pdf_import_row_import_fk FOREIGN KEY(import_id,user_id) REFERENCES pdf_import(id,user_id) ON DELETE CASCADE,
      CONSTRAINT pdf_import_row_meal_fk FOREIGN KEY(committed_meal_id,user_id) REFERENCES meal_entry(id,user_id) ON DELETE SET NULL,
      CONSTRAINT pdf_import_row_number CHECK (source_row_number > 0)
    )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_import_rows_page "
        "ON pdf_import_row(user_id,import_id,source_row_number,id)"
    )
    op.execute("""
    CREATE TABLE IF NOT EXISTS chat_session (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
      title varchar(200), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(id,user_id)
    )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_session_page "
        "ON chat_session(user_id,updated_at DESC,id DESC)"
    )
    op.execute("""
    CREATE TABLE IF NOT EXISTS chat_message (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(), session_id uuid NOT NULL, user_id uuid NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
      role varchar(12) NOT NULL, content text NOT NULL, tool_name varchar(80), tool_payload jsonb, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(id,user_id),
      CONSTRAINT chat_message_session_fk FOREIGN KEY(session_id,user_id) REFERENCES chat_session(id,user_id) ON DELETE CASCADE,
      CONSTRAINT chat_message_role CHECK(role IN ('USER','ASSISTANT','TOOL')), CONSTRAINT chat_message_content CHECK(length(content) <= 10000)
    )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_message_page "
        "ON chat_message(user_id,session_id,created_at ASC,id ASC)"
    )
    op.execute("""
    CREATE TABLE IF NOT EXISTS chat_confirmation (
      jti uuid PRIMARY KEY, user_id uuid NOT NULL, session_id uuid NOT NULL,
      action varchar(24) NOT NULL, draft_constraints_hash char(64) NOT NULL,
      expires_at timestamptz NOT NULL, consumed_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE(jti,user_id), CONSTRAINT chat_confirmation_session_fk FOREIGN KEY(session_id,user_id) REFERENCES chat_session(id,user_id) ON DELETE CASCADE,
      CONSTRAINT chat_confirmation_action CHECK(action = 'CREATE_MEAL'), CONSTRAINT chat_confirmation_expiry CHECK(expires_at > created_at),
      CONSTRAINT chat_confirmation_consumed CHECK(consumed_at IS NULL OR consumed_at >= created_at)
    )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_confirmation_active ON chat_confirmation(user_id,expires_at,jti) "
        "WHERE consumed_at IS NULL"
    )
    for table in _TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS {table}_owner ON {table}")
        op.execute(
            f"CREATE POLICY {table}_owner ON {table} USING (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid) WITH CHECK (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid)"
        )
    role = _runtime_role()
    _ensure_role(role)
    op.execute(f'GRANT SELECT, INSERT, UPDATE, DELETE ON {", ".join(_TABLES)} TO "{role}"')
    op.execute(f'GRANT USAGE, SELECT ON SEQUENCE pdf_import_row_id_seq TO "{role}"')


def downgrade() -> None:
    for table in reversed(_TABLES):
        op.execute(f"DROP POLICY IF EXISTS {table}_owner ON {table}")
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
