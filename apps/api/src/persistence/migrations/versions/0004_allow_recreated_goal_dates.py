"""Allow a new active goal to reuse an archived goal's start date.

Revision ID: 0004_allow_recreated_goal_dates
Revises: 0003_pdf_import_and_chat
"""

from alembic import op


revision = "0004_allow_recreated_goal_dates"
down_revision = "0003_pdf_import_and_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_health_goal_user_id", "health_goal", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("uq_health_goal_user_id", "health_goal", ["user_id", "effective_from"])
