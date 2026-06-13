"""Customer tables: profiles, addresses, guest sessions (doc 23/07).

All per-store (``store_id``); profiles/addresses are soft-deleted (doc 07). A
customer is identified within a store by **normalized email** and/or
**``phone_e164``** — either may be absent, but each is unique among the store's
active customers when present.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, text
from sqlmodel import Field

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin


class CustomerProfile(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """The final buyer of a store, identified by normalized email/phone.

    The same email/phone in two stores yields two different customers (each row
    is ``store_id``-scoped). ``email`` and ``phone_e164`` are unique among the
    store's active (non-deleted) customers when set (partial unique indexes).
    """

    __tablename__ = "customer_profiles"
    __table_args__ = (
        Index(
            "ix_customer_profiles_store_email",
            "store_id",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL AND deleted_at IS NULL"),
        ),
        Index(
            "ix_customer_profiles_store_phone",
            "store_id",
            "phone_e164",
            unique=True,
            postgresql_where=text("phone_e164 IS NOT NULL AND deleted_at IS NULL"),
        ),
    )

    name: str = Field(max_length=255)
    email: str | None = Field(default=None, max_length=320)
    phone_e164: str | None = Field(default=None, max_length=20)


class CustomerAddress(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A shipping/billing address of a customer (many per customer)."""

    __tablename__ = "customer_addresses"
    __table_args__ = (
        Index("ix_customer_addresses_store_customer", "store_id", "customer_id"),
    )

    customer_id: uuid.UUID = Field(foreign_key="customer_profiles.id", index=True)
    recipient_name: str | None = Field(default=None, max_length=255)
    line1: str = Field(max_length=255)
    number: str | None = Field(default=None, max_length=32)
    line2: str | None = Field(default=None, max_length=255)
    neighborhood: str | None = Field(default=None, max_length=255)
    city: str = Field(max_length=255)
    state: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str = Field(max_length=2, description="ISO 3166-1 alpha-2")


class CustomerGuestSession(UUIDMixin, TimestampMixin, StoreScopedMixin, table=True):
    """An anonymous browser session (cookie ``guest_session_id``), per store.

    The token is globally unique; the session may later link to a customer. It
    expires after 30 days (``expires_at``); expiry cleanup is a follow-up.
    """

    __tablename__ = "customer_guest_sessions"
    __table_args__ = (
        Index("ix_customer_guest_sessions_store_expires", "store_id", "expires_at"),
    )

    guest_session_id: str = Field(max_length=64, unique=True, index=True)
    customer_id: uuid.UUID | None = Field(
        default=None, foreign_key="customer_profiles.id", index=True
    )
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore
