"""Store (tenant) models: ``store_stores`` and ``store_settings``.

The store is the central tenant; every commercial entity is scoped to it by
``store_id`` (doc 06). Each store carries its own ``currency``/``locale``
(INV-G3), seeded from the platform defaults at creation.
"""

import uuid
from enum import Enum

from sqlalchemy import JSON, Column, Index, text
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class StoreStatus(str, Enum):
    """Lifecycle status of a store (doc 09)."""

    draft = "draft"
    active = "active"
    paused = "paused"
    suspended = "suspended"
    blocked = "blocked"
    archived = "archived"


class StoreBase(SQLModel):
    """Shared store fields."""

    name: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    status: StoreStatus = Field(default=StoreStatus.draft)
    currency: str = Field(max_length=3, description="ISO 4217 currency code")
    locale: str = Field(max_length=35)


class Store(UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreBase, table=True):
    """Store (tenant) table.

    ``slug`` is unique among non-deleted stores (partial unique index), so an
    archived store's slug can be reused.
    """

    __tablename__ = "store_stores"
    __table_args__ = (
        Index(
            "ix_store_stores_slug_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class StorePublic(StoreBase):
    """Store as returned via the API."""

    id: uuid.UUID


class StoreSettingsBase(SQLModel):
    """Shared store-settings fields (doc 09)."""

    public_name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    logo_url: str | None = Field(default=None, max_length=2048)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=32)
    whatsapp_number: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None)
    is_published: bool = Field(default=False)


class StoreSettings(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreSettingsBase, table=True
):
    """Per-store settings, one row per store (1:1 with ``store_stores``)."""

    __tablename__ = "store_settings"

    store_id: uuid.UUID = Field(foreign_key="store_stores.id", unique=True, index=True)
    social_links: dict[str, str] | None = Field(default=None, sa_column=Column(JSON))


class StoreSettingsPublic(StoreSettingsBase):
    """Store settings as returned via the API."""

    id: uuid.UUID
    store_id: uuid.UUID
    social_links: dict[str, str] | None = None
