"""Checkout tables: the checkout session (doc 23/07).

Per-store (``store_id``). A session tracks a checkout in progress (``active``,
expiring in ~24h) and is marked ``completed`` once the order is created.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index
from sqlmodel import Field

from app.db.base import StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.checkout.enums import CheckoutStatus


class CheckoutSession(UUIDMixin, TimestampMixin, StoreScopedMixin, table=True):
    """A checkout in progress for a cart; expires after ~24h."""

    __tablename__ = "checkout_sessions"
    __table_args__ = (
        Index(
            "ix_checkout_sessions_store_cart_status",
            "store_id",
            "cart_id",
            "status",
        ),
        Index("ix_checkout_sessions_expires_status", "expires_at", "status"),
    )

    cart_id: uuid.UUID = Field(foreign_key="cart_carts.id", index=True)
    status: CheckoutStatus = Field(default=CheckoutStatus.active)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore
    order_id: uuid.UUID | None = Field(default=None, foreign_key="order_orders.id")
