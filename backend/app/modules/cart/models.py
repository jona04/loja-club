"""Cart tables: server-side carts and their items (doc 10/11/07).

Per-store (``store_id``) and soft-deleted (doc 07). A cart is keyed by the
anonymous ``guest_session_id`` (cookie) and may later link to a ``customer_id``
(at checkout). Items carry the chosen ``variant_id`` and a unit-price snapshot
taken when added; the **order** re-freezes prices at creation (``P6-ORD-01``).
"""

import uuid

from sqlalchemy import Index
from sqlmodel import Field

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.cart.enums import CartStatus


class CartCart(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A customer's cart (one ``active`` per guest session within a store)."""

    __tablename__ = "cart_carts"
    __table_args__ = (
        Index(
            "ix_cart_carts_store_guest_status",
            "store_id",
            "guest_session_id",
            "status",
        ),
        Index(
            "ix_cart_carts_store_customer_status",
            "store_id",
            "customer_id",
            "status",
        ),
    )

    guest_session_id: str | None = Field(default=None, max_length=64, index=True)
    customer_id: uuid.UUID | None = Field(
        default=None, foreign_key="customer_profiles.id", index=True
    )
    status: CartStatus = Field(default=CartStatus.active)
    coupon_code: str | None = Field(default=None, max_length=64)


class CartItem(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A line in a cart: a product (+ optional variant) and a quantity.

    ``unit_price_*`` is the price snapshot when the item was added (display);
    the order re-freezes the price at creation.
    """

    __tablename__ = "cart_items"
    __table_args__ = (Index("ix_cart_items_store_cart", "store_id", "cart_id"),)

    cart_id: uuid.UUID = Field(foreign_key="cart_carts.id", index=True)
    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    variant_id: uuid.UUID | None = Field(
        default=None, foreign_key="catalog_product_variants.id", index=True
    )
    quantity: int = Field(ge=1)
    unit_price_amount_minor: int = Field(ge=0)
    unit_price_currency: str = Field(max_length=3)
