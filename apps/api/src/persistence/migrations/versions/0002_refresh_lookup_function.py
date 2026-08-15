"""Permit opaque refresh lookup without weakening tenant RLS.

Revision ID: 0002_refresh_lookup
Revises: 0001_initial_schema
"""

from alembic import op

revision = "0002_refresh_lookup"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE FUNCTION refresh_session_lookup(input_hash text)
    RETURNS TABLE(id uuid, user_id uuid, token_hash text, expires_at timestamptz,
                  revoked_at timestamptz)
    LANGUAGE sql SECURITY DEFINER SET search_path = public AS $$
      SELECT id, user_id, token_hash, expires_at, revoked_at
      FROM refresh_session WHERE token_hash = input_hash
    $$
    """)
    op.execute("GRANT EXECUTE ON FUNCTION refresh_session_lookup(text) TO PUBLIC")


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS refresh_session_lookup(text)")
