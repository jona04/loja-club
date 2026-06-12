"""catalog product type

Revision ID: 6d906257c2c5
Revises: f7fbb7746388
Create Date: 2026-06-11 21:37:58.598224

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '6d906257c2c5'
down_revision = 'f7fbb7746388'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type first, then add with a server default so existing rows
    # backfill to ``image``; finally drop the server default so new rows rely on
    # the app default (the model declares none).
    product_type = sa.Enum(
        'image', 'image_3d', 'image_3d_customizable', name='producttype'
    )
    product_type.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'catalog_products',
        sa.Column(
            'type',
            sa.Enum(
                'image',
                'image_3d',
                'image_3d_customizable',
                name='producttype',
                create_type=False,
            ),
            nullable=False,
            server_default='image',
        ),
    )
    op.alter_column('catalog_products', 'type', server_default=None)


def downgrade():
    op.drop_column('catalog_products', 'type')
    sa.Enum(name='producttype').drop(op.get_bind(), checkfirst=True)
