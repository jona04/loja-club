"""account_users: soft delete + updated_at

Adds ``updated_at`` and the soft-delete columns (``deleted_at``,
``deleted_by_user_id``, ``delete_reason``) to ``account_users`` and makes
``created_at`` NOT NULL, aligning it with the shared mixins (P1-ACCT-01).

Revision ID: a7b8c9d0e1f2
Revises: b1c2d3e4f5a6
Create Date: 2026-06-03 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a7b8c9d0e1f2"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "account_users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    # Drop the bootstrap default; the app sets updated_at via the mixin.
    op.alter_column("account_users", "updated_at", server_default=None)
    op.add_column(
        "account_users",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "account_users",
        sa.Column("deleted_by_user_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "account_users",
        sa.Column("delete_reason", sa.String(length=255), nullable=True),
    )
    op.alter_column(
        "account_users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "account_users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
    )
    op.drop_column("account_users", "delete_reason")
    op.drop_column("account_users", "deleted_by_user_id")
    op.drop_column("account_users", "deleted_at")
    op.drop_column("account_users", "updated_at")
