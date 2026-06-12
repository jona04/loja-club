"""Order tables: orders, items, addresses, status history, notes (doc 11/07).

Per-store (``store_id``) and soft-deleted where it makes sense (doc 07). An order
freezes what the customer bought: each ``order_items`` row snapshots the product
name, price and ``variant_id`` at creation; ``order_addresses`` snapshots the
delivery address. ``order_number`` is sequential **per store**.

Fulfillment tracking (``order_fulfillments``) and refunds (``order_refunds``) are
deferred — the order status covers shipping in the MVP and refunds are Fase 8.
"""

import uuid

from sqlalchemy import Index
from sqlmodel import Field

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.orders.enums import OrderStatus
from app.modules.shipping.enums import ShippingMethodType


class Order(UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True):
    """A customer's order. ``order_number`` is unique and sequential per store."""

    __tablename__ = "order_orders"
    __table_args__ = (
        Index("ix_order_orders_store_number", "store_id", "order_number", unique=True),
        Index("ix_order_orders_store_created", "store_id", "created_at"),
        Index("ix_order_orders_store_status", "store_id", "status"),
        Index("ix_order_orders_store_customer", "store_id", "customer_id"),
    )

    order_number: int
    status: OrderStatus = Field(default=OrderStatus.pending_payment)
    customer_id: uuid.UUID | None = Field(
        default=None, foreign_key="customer_profiles.id", index=True
    )
    guest_session_id: str | None = Field(default=None, max_length=64)
    shipping_method_type: ShippingMethodType | None = Field(default=None)
    shipping_method_name: str | None = Field(default=None, max_length=255)
    subtotal_amount_minor: int = Field(ge=0)
    shipping_amount_minor: int = Field(default=0, ge=0)
    discount_amount_minor: int = Field(default=0, ge=0)
    total_amount_minor: int = Field(ge=0)
    currency: str = Field(max_length=3)


class OrderItem(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A purchased line: product/variant + frozen name, price and quantity."""

    __tablename__ = "order_items"
    __table_args__ = (Index("ix_order_items_store_order", "store_id", "order_id"),)

    order_id: uuid.UUID = Field(foreign_key="order_orders.id", index=True)
    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    variant_id: uuid.UUID | None = Field(
        default=None, foreign_key="catalog_product_variants.id", index=True
    )
    name: str = Field(max_length=255)
    quantity: int = Field(ge=1)
    unit_price_amount_minor: int = Field(ge=0)
    unit_price_currency: str = Field(max_length=3)
    line_total_amount_minor: int = Field(ge=0)


class OrderAddress(UUIDMixin, TimestampMixin, StoreScopedMixin, table=True):
    """The delivery address snapshotted on the order (immutable)."""

    __tablename__ = "order_addresses"

    order_id: uuid.UUID = Field(foreign_key="order_orders.id", index=True)
    recipient_name: str | None = Field(default=None, max_length=255)
    line1: str = Field(max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(max_length=255)
    state: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str = Field(max_length=2)


class OrderStatusHistory(UUIDMixin, TimestampMixin, StoreScopedMixin, table=True):
    """One row per order status transition (audit trail)."""

    __tablename__ = "order_status_history"
    __table_args__ = (
        Index(
            "ix_order_status_history_store_order_created",
            "store_id",
            "order_id",
            "created_at",
        ),
    )

    order_id: uuid.UUID = Field(foreign_key="order_orders.id", index=True)
    status: OrderStatus
    note: str | None = Field(default=None, max_length=500)


class OrderNote(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """An internal note on an order (written by the merchant in the panel)."""

    __tablename__ = "order_notes"
    __table_args__ = (Index("ix_order_notes_store_order", "store_id", "order_id"),)

    order_id: uuid.UUID = Field(foreign_key="order_orders.id", index=True)
    body: str
    author_user_id: uuid.UUID | None = Field(default=None)
