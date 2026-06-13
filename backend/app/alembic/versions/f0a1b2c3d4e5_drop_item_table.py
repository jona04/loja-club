"""drop item table

Removes the FastAPI template's ``items`` example, which is not part of Kriar.

Revision ID: f0a1b2c3d4e5
Revises: fe56fa70289e
Create Date: 2026-06-03 00:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "f0a1b2c3d4e5"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("item")


def downgrade():
    op.create_table(
        "item",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
