"""Create the Stage 1 normalized nutrition schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-16
"""

from __future__ import annotations

import os
import re

from alembic import op

from src.persistence import models  # noqa: F401
from src.persistence.base import Base

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
_TENANT_TABLES = (
    "health_goal",
    "goal_nutrient_target",
    "upload_object",
    "nutrition_extraction",
    "meal_entry",
    "meal_entry_nutrient",
    "refresh_session",
    "idempotency_record",
)


def _runtime_role() -> str:
    role = os.environ.get("APP_DB_USER", "calorie_app")
    if not _IDENTIFIER.fullmatch(role):
        raise ValueError("APP_DB_USER must be a simple lowercase PostgreSQL identifier")
    return role


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    Base.metadata.create_all(bind=bind)
    for table in _TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_owner ON {table} "
            "USING (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid) "
            "WITH CHECK (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid)"
        )
    role = _runtime_role()
    op.execute(f'GRANT USAGE ON SCHEMA public TO "{role}"')
    op.execute(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "{role}"')
    op.execute(f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "{role}"')


def downgrade() -> None:
    bind = op.get_bind()
    for table in reversed(_TENANT_TABLES):
        op.execute(f"DROP POLICY IF EXISTS {table}_owner ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    Base.metadata.drop_all(bind=bind)
    op.execute("DROP EXTENSION IF EXISTS btree_gist")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
