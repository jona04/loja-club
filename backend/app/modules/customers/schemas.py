"""API request/response schemas for the customers module."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.modules.orders.enums import OrderStatus


class AddressInput(SQLModel):
    """An address provided at checkout (appended to the customer if new)."""

    recipient_name: str | None = Field(default=None, max_length=255)
    line1: str = Field(max_length=255)
    number: str | None = Field(default=None, max_length=32)
    line2: str | None = Field(default=None, max_length=255)
    neighborhood: str | None = Field(default=None, max_length=255)
    city: str = Field(max_length=255)
    state: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str = Field(max_length=2, description="ISO 3166-1 alpha-2")


class CustomerSummary(SQLModel):
    """A row in the panel customers list."""

    id: uuid.UUID
    name: str
    email: str | None
    phone_e164: str | None
    created_at: datetime


class CustomerAddressPublic(SQLModel):
    """A saved customer address."""

    id: uuid.UUID
    recipient_name: str | None
    line1: str
    number: str | None
    line2: str | None
    neighborhood: str | None
    city: str
    state: str | None
    postal_code: str | None
    country: str


class CustomerOrderRow(SQLModel):
    """An order in a customer's purchase history."""

    id: uuid.UUID
    order_number: int
    status: OrderStatus
    currency: str
    total_amount_minor: int
    created_at: datetime


class CustomerDetail(SQLModel):
    """A customer's profile, saved addresses and order history (panel detail)."""

    id: uuid.UUID
    name: str
    email: str | None
    phone_e164: str | None
    created_at: datetime
    addresses: list[CustomerAddressPublic]
    orders: list[CustomerOrderRow]
