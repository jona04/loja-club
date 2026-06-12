"""API request/response schemas for the customers module."""

from sqlmodel import Field, SQLModel


class AddressInput(SQLModel):
    """An address provided at checkout (appended to the customer if new)."""

    recipient_name: str | None = Field(default=None, max_length=255)
    line1: str = Field(max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(max_length=255)
    state: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str = Field(max_length=2, description="ISO 3166-1 alpha-2")
