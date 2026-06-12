"""Discount tables: coupons and their redemptions (doc 09/07).

Per-store (``store_id``) and soft-deleted (doc 07). A coupon's ``code`` is unique
among the store's **active** (non-deleted) coupons (partial unique index). A
redemption row is written when a coupon is used on an order, enforcing the usage
limit. Money is the store's single currency (INV-G3), so ``fixed`` coupons carry
no currency of their own.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, text
from sqlmodel import Field

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.discounts.enums import CouponType


class DiscountCoupon(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A discount coupon (percentage or fixed) the customer can apply."""

    __tablename__ = "discount_coupons"
    __table_args__ = (
        Index(
            "ix_discount_coupons_store_code",
            "store_id",
            "code",
            unique=True,
            postgresql_where=text("is_active AND deleted_at IS NULL"),
        ),
    )

    code: str = Field(max_length=64)
    type: CouponType
    value: int = Field(ge=0)
    min_subtotal_amount_minor: int = Field(default=0, ge=0)
    max_redemptions: int | None = Field(default=None, ge=1)
    valid_from: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    valid_until: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    is_active: bool = Field(default=True)


class DiscountCouponRedemption(UUIDMixin, TimestampMixin, StoreScopedMixin, table=True):
    """One use of a coupon (written when an order is placed with it)."""

    __tablename__ = "discount_coupon_redemptions"
    __table_args__ = (
        Index("ix_discount_redemptions_store_coupon", "store_id", "coupon_id"),
    )

    coupon_id: uuid.UUID = Field(foreign_key="discount_coupons.id", index=True)
    order_id: uuid.UUID | None = Field(
        default=None, foreign_key="order_orders.id", index=True
    )
    customer_id: uuid.UUID | None = Field(
        default=None, foreign_key="customer_profiles.id", index=True
    )
