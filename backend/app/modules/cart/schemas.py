"""API request/response schemas for the cart module."""

import uuid

from sqlmodel import Field, SQLModel


class AddItemInput(SQLModel):
    """Add a product (optionally a variant) to the cart."""

    product_id: uuid.UUID
    variant_id: uuid.UUID | None = None
    quantity: int = Field(default=1, ge=1)


class UpdateItemInput(SQLModel):
    """Set a cart line's quantity."""

    quantity: int = Field(ge=1)


class CartItemPublic(SQLModel):
    """A cart line, render-ready for the storefront."""

    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: uuid.UUID | None
    name: str
    slug: str
    image_url: str | None
    quantity: int
    unit_price_amount_minor: int
    unit_price_currency: str
    line_total_amount_minor: int


class CartPublic(SQLModel):
    """A cart with its items and computed subtotal."""

    id: uuid.UUID
    currency: str
    item_count: int
    subtotal_amount_minor: int
    items: list[CartItemPublic]
