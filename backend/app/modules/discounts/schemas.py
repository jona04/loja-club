"""API request/response schemas for the discounts module."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.modules.discounts.enums import CouponType


class CouponCreate(SQLModel):
    """Create a coupon."""

    code: str = Field(max_length=64)
    type: CouponType
    value: int = Field(ge=0)
    min_subtotal_amount_minor: int = Field(default=0, ge=0)
    max_redemptions: int | None = Field(default=None, ge=1)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool = True


class CouponUpdate(SQLModel):
    """Partial update of a coupon (only set fields apply)."""

    code: str | None = Field(default=None, max_length=64)
    type: CouponType | None = None
    value: int | None = Field(default=None, ge=0)
    min_subtotal_amount_minor: int | None = Field(default=None, ge=0)
    max_redemptions: int | None = Field(default=None, ge=1)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool | None = None


class CouponPublic(SQLModel):
    """A coupon as returned by the panel."""

    id: uuid.UUID
    code: str
    type: CouponType
    value: int
    min_subtotal_amount_minor: int
    max_redemptions: int | None
    valid_from: datetime | None
    valid_until: datetime | None
    is_active: bool
    created_at: datetime


class ApplyCouponInput(SQLModel):
    """Apply a coupon code to the cart."""

    code: str = Field(max_length=64)
