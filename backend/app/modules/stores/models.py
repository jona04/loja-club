"""Store (tenant) tables: ``store_stores`` and ``store_settings``.

API request/response schemas live in ``schemas.py``; enums in ``enums.py``. The
store is the central tenant; every commercial entity is scoped to it by
``store_id`` (doc 06). Each store carries its own ``currency``/``locale``
(INV-G3), seeded from the platform defaults at creation.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Index, text
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.modules.stores.enums import MembershipStatus, StoreStatus


class StoreBase(SQLModel):
    """Shared store fields."""

    name: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    status: StoreStatus = Field(default=StoreStatus.draft)
    country: str = Field(
        default="BR", max_length=2, description="ISO 3166-1 alpha-2 country code"
    )
    currency: str = Field(max_length=3, description="ISO 4217 currency code")
    locale: str = Field(max_length=35)


class Store(UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreBase, table=True):
    """Store (tenant) table.

    ``slug`` is unique among non-deleted stores (partial unique index), so a
    deleted store's slug can be reused.
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


class StoreSettingsBase(SQLModel):
    """Shared store-settings fields (doc 09)."""

    public_name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    logo_url: str | None = Field(default=None, max_length=2048)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=32)
    whatsapp_number: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None)


class StoreSettings(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreSettingsBase, table=True
):
    """Per-store settings, one row per store (1:1 with ``store_stores``)."""

    __tablename__ = "store_settings"

    store_id: uuid.UUID = Field(foreign_key="store_stores.id", unique=True, index=True)
    social_links: dict[str, str] | None = Field(default=None, sa_column=Column(JSON))


class StoreRole(UUIDMixin, table=True):
    """Store role (seeded lookup; global, applied per store via membership)."""

    __tablename__ = "store_roles"

    key: str = Field(unique=True, index=True, max_length=50)
    name: str = Field(max_length=100)


class StoreMember(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    """Membership linking an account user to a store with a role.

    Unique among non-deleted rows on ``(store_id, user_id)``, so removing a
    member (soft delete) frees a new invite for the same user.
    """

    __tablename__ = "store_members"
    __table_args__ = (
        Index(
            "ix_store_members_store_user_active",
            "store_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_store_members_store_status", "store_id", "status"),
    )

    store_id: uuid.UUID = Field(foreign_key="store_stores.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="account_users.id", index=True)
    role_id: uuid.UUID = Field(foreign_key="store_roles.id", index=True)
    status: MembershipStatus = Field(default=MembershipStatus.active)
    invited_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    removed_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class StorePermission(UUIDMixin, table=True):
    """Store permission catalog (seeded; ``key`` + ``module``)."""

    __tablename__ = "store_permissions"

    key: str = Field(unique=True, index=True, max_length=100)
    module: str = Field(max_length=50, index=True)
    description: str | None = Field(default=None, max_length=255)


class StoreRolePermission(UUIDMixin, table=True):
    """Positive role -> permission grant (seeded join)."""

    __tablename__ = "store_role_permissions"
    __table_args__ = (
        Index(
            "ix_store_role_permissions_role_perm",
            "role_id",
            "permission_id",
            unique=True,
        ),
    )

    role_id: uuid.UUID = Field(foreign_key="store_roles.id", index=True)
    permission_id: uuid.UUID = Field(foreign_key="store_permissions.id", index=True)
