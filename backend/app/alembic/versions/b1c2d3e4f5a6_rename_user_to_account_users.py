"""rename user table to account_users

Renames the template's ``user`` table to ``account_users`` (Loja Club naming).

Revision ID: b1c2d3e4f5a6
Revises: f0a1b2c3d4e5
Create Date: 2026-06-03 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5a6"
down_revision = "f0a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("user", "account_users")


def downgrade():
    op.rename_table("account_users", "user")
