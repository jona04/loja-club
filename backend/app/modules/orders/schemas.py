"""API request/response schemas for the orders module."""

import uuid

from sqlmodel import SQLModel

from app.modules.orders.enums import OrderStatus
from app.modules.shipping.enums import ShippingMethodType


class OrderItemPublic(SQLModel):
    """A purchased line (frozen name/price)."""

    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: uuid.UUID | None
    name: str
    quantity: int
    unit_price_amount_minor: int
    unit_price_currency: str
    line_total_amount_minor: int


class OrderPublic(SQLModel):
    """An order with its items (checkout confirmation + panel detail)."""

    id: uuid.UUID
    order_number: int
    status: OrderStatus
    currency: str
    subtotal_amount_minor: int
    shipping_amount_minor: int
    discount_amount_minor: int
    total_amount_minor: int
    shipping_method_type: ShippingMethodType | None
    shipping_method_name: str | None
    items: list[OrderItemPublic]
