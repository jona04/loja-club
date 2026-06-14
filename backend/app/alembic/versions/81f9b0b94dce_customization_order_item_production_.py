"""customization_order_item_production_status

Revision ID: 81f9b0b94dce
Revises: b7e1c0d9a4f2
Create Date: 2026-06-14 16:34:12.969793

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '81f9b0b94dce'
down_revision = 'b7e1c0d9a4f2'
branch_labels = None
depends_on = None


_VALUES = (
    'received',
    'reviewing',
    'needs_contact',
    'approved_for_production',
    'in_production',
    'production_done',
)
production_status = sa.Enum(*_VALUES, name='customizationproductionstatus')


def upgrade():
    # Create the enum type first, then add the column with a transient server
    # default so any existing order items backfill to 'received'; finally drop the
    # default so the column matches the model (the ORM always supplies the value).
    bind = op.get_bind()
    production_status.create(bind, checkfirst=True)
    op.add_column(
        'customization_order_items',
        sa.Column(
            'production_status',
            sa.Enum(*_VALUES, name='customizationproductionstatus', create_type=False),
            nullable=False,
            server_default='received',
        ),
    )
    op.alter_column(
        'customization_order_items', 'production_status', server_default=None
    )


def downgrade():
    op.drop_column('customization_order_items', 'production_status')
    production_status.drop(op.get_bind(), checkfirst=True)
