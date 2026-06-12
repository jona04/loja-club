"""API request/response schemas for the checkout module."""

import uuid

from sqlmodel import Field, SQLModel

from app.modules.customers.schemas import AddressInput


class CheckoutContact(SQLModel):
    """Customer contact collected at checkout (no password)."""

    name: str = Field(max_length=255)
    email: str | None = None
    phone: str | None = None
    region: str | None = None  # ISO 3166-1 country for the phone (selector)


class CheckoutInput(SQLModel):
    """The checkout submission: contact + address + chosen shipping method."""

    contact: CheckoutContact
    address: AddressInput
    shipping_method_id: uuid.UUID


class PoliciesUpdate(SQLModel):
    """Partial update of a store's checkout policies."""

    return_policy: str | None = None
    exchange_policy: str | None = None
    privacy_policy: str | None = None


class PoliciesPublic(SQLModel):
    """A store's checkout policies (return/exchange/privacy)."""

    return_policy: str | None
    exchange_policy: str | None
    privacy_policy: str | None
