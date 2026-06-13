"""Shipping tables: the store's delivery methods (doc 11/07).

Per-store (``store_id``) and soft-deleted (doc 07). The MVP ships the method
catalog (pickup/combined/fixed/free); zones, rates and rules per region are a
fast-follow (``P6-SHIP-02``). Amounts are in the **store's** currency (a store
sells in a single currency, INV-G3); the Money object is paired with
``store.currency`` at display/checkout.
"""

from sqlalchemy import Index
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.shipping.enums import ShippingMethodType


class ShippingMethodBase(SQLModel):
    """Shared fields of a store's shipping method."""

    type: ShippingMethodType
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    price_amount_minor: int | None = Field(
        default=None, ge=0, description="Flat fee (minor units) for fixed_shipping"
    )
    min_order_amount_minor: int | None = Field(
        default=None, ge=0, description="Minimum order (minor units) for free_shipping"
    )


class ShippingMethod(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    ShippingMethodBase,
    table=True,
):
    """A delivery option a store offers at checkout."""

    __tablename__ = "shipping_methods"
    __table_args__ = (
        Index("ix_shipping_methods_store_type_active", "store_id", "type", "is_active"),
    )
