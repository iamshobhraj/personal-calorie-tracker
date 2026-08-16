"""Allow a new active goal to reuse an archived goal's start date.

Revision ID: 0004_allow_recreated_goal_dates
Revises: 0003_pdf_import_and_chat
"""

from __future__ import annotations

from alembic import op

revision = "0004_allow_recreated_goal_dates"
down_revision = "0003_pdf_import_and_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE health_goal DROP CONSTRAINT IF EXISTS uq_health_goal_user_id")


def downgrade() -> None:
    op.execute("""
    DELETE FROM health_goal h1
    USING health_goal h2
    WHERE h1.user_id = h2.user_id
      AND h1.effective_from = h2.effective_from
      AND h1.created_at < h2.created_at
    """)
    op.create_unique_constraint(
        "uq_health_goal_user_id", "health_goal", ["user_id", "effective_from"]
    )
