"""API request/response schemas for the orders module."""

import uuid
from datetime import datetime

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


class OrderSummary(SQLModel):
    """A row in the panel orders list (number + status + total + customer)."""

    id: uuid.UUID
    order_number: int
    status: OrderStatus
    currency: str
    total_amount_minor: int
    item_count: int
    customer_name: str | None
    created_at: datetime


class OrderAddressPublic(SQLModel):
    """The delivery address snapshotted on an order."""

    recipient_name: str | None
    line1: str
    number: str | None
    line2: str | None
    neighborhood: str | None
    city: str
    state: str | None
    postal_code: str | None
    country: str


class OrderCustomerPublic(SQLModel):
    """The customer behind an order (for contact + WhatsApp handoff)."""

    id: uuid.UUID
    name: str
    email: str | None
    phone_e164: str | None


class OrderStatusHistoryPublic(SQLModel):
    """One status transition in an order's history."""

    status: OrderStatus
    note: str | None
    created_at: datetime


class OrderNotePublic(SQLModel):
    """An internal note written on an order by the merchant."""

    id: uuid.UUID
    body: str
    author_user_id: uuid.UUID | None
    created_at: datetime


class OrderDetail(SQLModel):
    """The full order, for the panel detail (customer, address, history, notes)."""

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
    created_at: datetime
    customer: OrderCustomerPublic | None
    address: OrderAddressPublic | None
    items: list[OrderItemPublic]
    status_history: list[OrderStatusHistoryPublic]
    notes: list[OrderNotePublic]


class OrderStatusUpdate(SQLModel):
    """Move an order to the next operational status."""

    status: OrderStatus


class OrderNoteCreate(SQLModel):
    """Add an internal note to an order."""

    body: str
