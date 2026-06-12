"""API request/response schemas for the shipping module."""

import uuid

from sqlmodel import Field, SQLModel

from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethodBase


class ShippingMethodCreate(SQLModel):
    """Fields accepted when creating a shipping method."""

    type: ShippingMethodType
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    price_amount_minor: int | None = Field(default=None, ge=0)
    min_order_amount_minor: int | None = Field(default=None, ge=0)


class ShippingMethodUpdate(SQLModel):
    """Partial update for a shipping method (``type`` is immutable)."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    price_amount_minor: int | None = Field(default=None, ge=0)
    min_order_amount_minor: int | None = Field(default=None, ge=0)


class ShippingMethodPublic(ShippingMethodBase):
    """Public representation of a shipping method (panel + checkout)."""

    id: uuid.UUID
    store_id: uuid.UUID
