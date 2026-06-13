"""orders and unique inventory

Revision ID: 33517f4ccbc8
Revises: 5d0fd62fc87b
Create Date: 2026-06-11 23:05:29.469214

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '33517f4ccbc8'
down_revision = '5d0fd62fc87b'
branch_labels = None
depends_on = None


def upgrade():
    # ``order_orders`` creates the ``orderstatus`` enum; the later use (and the
    # already-existing ``shippingmethodtype``) reference it with create_type=False.
    op.create_table('order_orders',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('delete_reason', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_number', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('pending_payment', 'paid', 'processing', 'shipped', 'delivered', 'canceled', name='orderstatus'), nullable=False),
    sa.Column('customer_id', sa.Uuid(), nullable=True),
    sa.Column('guest_session_id', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=True),
    sa.Column('shipping_method_type', postgresql.ENUM('fixed_shipping', 'free_shipping', 'local_pickup', 'private_delivery', name='shippingmethodtype', create_type=False), nullable=True),
    sa.Column('shipping_method_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('subtotal_amount_minor', sa.Integer(), nullable=False),
    sa.Column('shipping_amount_minor', sa.Integer(), nullable=False),
    sa.Column('discount_amount_minor', sa.Integer(), nullable=False),
    sa.Column('total_amount_minor', sa.Integer(), nullable=False),
    sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer_profiles.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_orders_customer_id'), 'order_orders', ['customer_id'], unique=False)
    op.create_index('ix_order_orders_store_created', 'order_orders', ['store_id', 'created_at'], unique=False)
    op.create_index('ix_order_orders_store_customer', 'order_orders', ['store_id', 'customer_id'], unique=False)
    op.create_index(op.f('ix_order_orders_store_id'), 'order_orders', ['store_id'], unique=False)
    op.create_index('ix_order_orders_store_number', 'order_orders', ['store_id', 'order_number'], unique=True)
    op.create_index('ix_order_orders_store_status', 'order_orders', ['store_id', 'status'], unique=False)
    op.create_table('order_addresses',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('recipient_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('line1', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('line2', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('city', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('state', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('postal_code', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=True),
    sa.Column('country', sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order_orders.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_addresses_order_id'), 'order_addresses', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_addresses_store_id'), 'order_addresses', ['store_id'], unique=False)
    op.create_table('order_items',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('delete_reason', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.Column('variant_id', sa.Uuid(), nullable=True),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price_amount_minor', sa.Integer(), nullable=False),
    sa.Column('unit_price_currency', sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False),
    sa.Column('line_total_amount_minor', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order_orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['catalog_products.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store_stores.id'], ),
    sa.ForeignKeyConstraint(['variant_id'], ['catalog_product_variants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_order_items_store_id'), 'order_items', ['store_id'], unique=False)
    op.create_index('ix_order_items_store_order', 'order_items', ['store_id', 'order_id'], unique=False)
    op.create_index(op.f('ix_order_items_variant_id'), 'order_items', ['variant_id'], unique=False)
    op.create_table('order_notes',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('delete_reason', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('body', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('author_user_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order_orders.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_notes_order_id'), 'order_notes', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_notes_store_id'), 'order_notes', ['store_id'], unique=False)
    op.create_index('ix_order_notes_store_order', 'order_notes', ['store_id', 'order_id'], unique=False)
    op.create_table('order_status_history',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('status', postgresql.ENUM('pending_payment', 'paid', 'processing', 'shipped', 'delivered', 'canceled', name='orderstatus', create_type=False), nullable=False),
    sa.Column('note', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order_orders.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['store_stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_status_history_order_id'), 'order_status_history', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_status_history_store_id'), 'order_status_history', ['store_id'], unique=False)
    op.create_index('ix_order_status_history_store_order_created', 'order_status_history', ['store_id', 'order_id', 'created_at'], unique=False)
    op.drop_index(op.f('ix_catalog_inventory_store_product_variant'), table_name='catalog_inventory_items')
    op.create_index('ix_catalog_inventory_store_product_variant', 'catalog_inventory_items', ['store_id', 'product_id', 'variant_id'], unique=True, postgresql_nulls_not_distinct=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_catalog_inventory_store_product_variant', table_name='catalog_inventory_items', postgresql_nulls_not_distinct=True)
    op.create_index(op.f('ix_catalog_inventory_store_product_variant'), 'catalog_inventory_items', ['store_id', 'product_id', 'variant_id'], unique=False)
    op.drop_index('ix_order_status_history_store_order_created', table_name='order_status_history')
    op.drop_index(op.f('ix_order_status_history_store_id'), table_name='order_status_history')
    op.drop_index(op.f('ix_order_status_history_order_id'), table_name='order_status_history')
    op.drop_table('order_status_history')
    op.drop_index('ix_order_notes_store_order', table_name='order_notes')
    op.drop_index(op.f('ix_order_notes_store_id'), table_name='order_notes')
    op.drop_index(op.f('ix_order_notes_order_id'), table_name='order_notes')
    op.drop_table('order_notes')
    op.drop_index(op.f('ix_order_items_variant_id'), table_name='order_items')
    op.drop_index('ix_order_items_store_order', table_name='order_items')
    op.drop_index(op.f('ix_order_items_store_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_order_addresses_store_id'), table_name='order_addresses')
    op.drop_index(op.f('ix_order_addresses_order_id'), table_name='order_addresses')
    op.drop_table('order_addresses')
    op.drop_index('ix_order_orders_store_status', table_name='order_orders')
    op.drop_index('ix_order_orders_store_number', table_name='order_orders')
    op.drop_index(op.f('ix_order_orders_store_id'), table_name='order_orders')
    op.drop_index('ix_order_orders_store_customer', table_name='order_orders')
    op.drop_index('ix_order_orders_store_created', table_name='order_orders')
    op.drop_index(op.f('ix_order_orders_customer_id'), table_name='order_orders')
    op.drop_table('order_orders')
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
