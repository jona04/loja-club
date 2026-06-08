"""rename account_users email index

Renames the stale ``ix_user_email`` index (inherited from the template's
``user`` table through ``rename_table`` in P0-MOD-04) to
``ix_account_users_email``, matching the SQLModel-generated name and removing
recurring autogenerate noise.

Revision ID: c2d3e4f5a6b7
Revises: 516224031edd
Create Date: 2026-06-03 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "c2d3e4f5a6b7"
down_revision = "516224031edd"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER INDEX ix_user_email RENAME TO ix_account_users_email")


def downgrade():
    op.execute("ALTER INDEX ix_account_users_email RENAME TO ix_user_email")
