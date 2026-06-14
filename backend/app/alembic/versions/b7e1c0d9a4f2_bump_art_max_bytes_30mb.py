"""bump art_limits max_bytes to 30 MiB

Revision ID: b7e1c0d9a4f2
Revises: ea7cf5fe8d46
Create Date: 2026-06-14 14:40:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b7e1c0d9a4f2'
down_revision = 'ea7cf5fe8d46'
branch_labels = None
depends_on = None

# Bumps already-seeded 3D model versions from the old 15 MiB art cap to 30 MiB
# (doc 31 §4); rows still on the old default get the new one (admin-edited rows
# with other values are left untouched).
_OLD = 15 * 1024 * 1024
_NEW = 30 * 1024 * 1024


def upgrade():
    op.execute(
        "UPDATE platform_3d_model_versions "
        f"SET art_limits = jsonb_set(art_limits::jsonb, '{{max_bytes}}', '{_NEW}')::json "
        f"WHERE (art_limits::jsonb->>'max_bytes') = '{_OLD}'"
    )


def downgrade():
    op.execute(
        "UPDATE platform_3d_model_versions "
        f"SET art_limits = jsonb_set(art_limits::jsonb, '{{max_bytes}}', '{_OLD}')::json "
        f"WHERE (art_limits::jsonb->>'max_bytes') = '{_NEW}'"
    )
