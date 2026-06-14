"""Platform 3D catalog tables (``platform_3d_models`` / ``_versions``).

Platform-owned (no ``store_id``): the Kriar 3D catalog is global, seeded by the
dev. A model has one or more **immutable** versions — the optimized GLB on the
CDN plus the JSON parameters that drive the storefront editor (printable areas,
text limits, art limits). The ``slug`` is the single source of truth for the CDN
path (see :mod:`app.modules.customization.storage`). Store-scoped,
merchant-generated models are a separate path.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Index, text
from sqlmodel import Field, SQLModel

from app.db.base import (
    SoftDeleteMixin,
    StoreScopedMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.modules.customization.enums import CustomizationSessionStatus


class Platform3DModelBase(SQLModel):
    """Shared catalog-model fields."""

    name: str = Field(max_length=100)
    category: str = Field(max_length=50, description="Product family, e.g. 'caneca'")
    slug: str = Field(
        max_length=100,
        description="Stable unique identifier; also the CDN path segment",
    )
    is_active: bool = True


class Platform3DModel(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, Platform3DModelBase, table=True
):
    """A public 3D catalog model (platform-owned, seeded).

    ``slug`` is unique among non-deleted models (partial unique index) and is the
    single source of truth for the GLB's CDN path.
    """

    __tablename__ = "platform_3d_models"
    __table_args__ = (
        Index(
            "ix_platform_3d_models_slug_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_platform_3d_models_category", "category"),
    )


class Platform3DModelVersionBase(SQLModel):
    """Shared version fields: the GLB plus the editor parameters."""

    version: int = Field(ge=1, description="Immutable version number (1-based)")
    glb_url: str = Field(max_length=500, description="CDN URL of the optimized GLB")
    printable_areas: list[dict[str, object]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="UV region (rectangle) + limits, per printable area",
    )
    text_config: dict[str, object] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Allowed fonts and text size limits",
    )
    art_limits: dict[str, object] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Accepted mimes, max bytes, min dimension",
    )
    is_active: bool = True


class Platform3DModelVersion(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Platform3DModelVersionBase,
    table=True,
):
    """An immutable version of a catalog model (GLB + editor parameters).

    The GLB is immutable per version (a new GLB is a new version); the
    ``printable_areas`` / ``text_config`` / ``art_limits`` JSONs stay editable in
    the admin within the version.
    """

    __tablename__ = "platform_3d_model_versions"
    __table_args__ = (
        Index(
            "ix_platform_3d_model_versions_model_version",
            "model_id",
            "version",
            unique=True,
        ),
    )

    model_id: uuid.UUID = Field(foreign_key="platform_3d_models.id", index=True)


class CustomizationProductSettingsBase(SQLModel):
    """Shared fields for a product's 3D-model link."""

    production_notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Merchant notes for production (e.g. print placement hints)",
    )


class CustomizationProductSettings(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    CustomizationProductSettingsBase,
    table=True,
):
    """Links a store's product to a catalog 3D model (the merchant's choice).

    One active row per product (partial unique index on ``store_id +
    product_id`` where ``deleted_at IS NULL``): linking upserts it and sets the
    product's ``type`` (``image_3d`` / ``image_3d_customizable``); unlinking
    soft-deletes it and reverts ``type`` to ``image``. The chosen model is the
    platform catalog model; the storefront editor resolves the model to use from
    here.
    """

    __tablename__ = "customization_product_settings"
    __table_args__ = (
        Index(
            "ix_customization_product_settings_store_product",
            "store_id",
            "product_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    platform_3d_model_id: uuid.UUID = Field(
        foreign_key="platform_3d_models.id", index=True
    )


class CustomizationSession(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    table=True,
):
    """A customer's in-progress (or frozen) 3D customization of a product.

    Holds the editor ``state_json`` (doc 30 §4) against a **pinned** catalog
    version. Owned either by a guest browser (``guest_session_id``) or assembled
    by the store (``created_by_user_id`` + ``customer_id``, assisted flow); the
    assisted session also carries a read-only ``public_token`` for a shareable
    link. ``snapshot_key`` is the approved client-side PNG (doc 30 §5). Sessions
    expire 30 days after creation (swept to ``expired`` by the worker).
    """

    __tablename__ = "customization_sessions"
    __table_args__ = (
        Index(
            "ix_customization_sessions_store_product_status",
            "store_id",
            "product_id",
            "status",
        ),
        Index(
            "ix_customization_sessions_store_guest_status",
            "store_id",
            "guest_session_id",
            "status",
        ),
        Index(
            "ix_customization_sessions_store_customer_status",
            "store_id",
            "customer_id",
            "status",
        ),
        Index("ix_customization_sessions_expires_status", "expires_at", "status"),
        Index(
            "ix_customization_sessions_public_token",
            "public_token",
            unique=True,
            postgresql_where=text("public_token IS NOT NULL AND deleted_at IS NULL"),
        ),
    )

    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    platform_3d_model_version_id: uuid.UUID = Field(
        foreign_key="platform_3d_model_versions.id", index=True
    )
    state_json: dict[str, object] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="The editor state (doc 30 §4): pinned model + layers",
    )
    status: CustomizationSessionStatus = Field(default=CustomizationSessionStatus.draft)
    guest_session_id: str | None = Field(default=None, max_length=64)
    customer_id: uuid.UUID | None = Field(
        default=None, foreign_key="customer_profiles.id"
    )
    created_by_user_id: uuid.UUID | None = Field(
        default=None, description="Store user who assembled an assisted session"
    )
    snapshot_key: str | None = Field(default=None, max_length=500)
    public_token: str | None = Field(default=None, max_length=64)
    expires_at: datetime = Field(
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    approved_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class CustomizationUpload(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    table=True,
):
    """A raster asset a customer uploaded for a session (private, doc 30 §6).

    Stored under ``private/<store_id>/customizations/<session_id>/...`` and only
    ever served via a short-lived presigned URL. Layers in ``state_json``
    reference it by id.
    """

    __tablename__ = "customization_uploads"
    __table_args__ = (
        Index(
            "ix_customization_uploads_store_session",
            "store_id",
            "customization_session_id",
        ),
    )

    customization_session_id: uuid.UUID = Field(
        foreign_key="customization_sessions.id", index=True
    )
    key: str = Field(max_length=500, description="Private S3 object key")
    mime: str = Field(max_length=100)
    size_bytes: int = Field(ge=0)
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)


class CustomizationCartItem(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    table=True,
):
    """Links a cart line to its approved customization session (doc 30 §7).

    One active link per cart line (partial unique index). When the cart becomes
    an order, the session is **frozen** into ``customization_order_items``.
    """

    __tablename__ = "customization_cart_items"
    __table_args__ = (
        Index(
            "ix_customization_cart_items_store_cart_item",
            "store_id",
            "cart_item_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    cart_item_id: uuid.UUID = Field(foreign_key="cart_items.id", index=True)
    customization_session_id: uuid.UUID = Field(
        foreign_key="customization_sessions.id", index=True
    )


class CustomizationOrderItem(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    table=True,
):
    """A frozen copy of a customization on an order line (INV-P5, doc 30 §7).

    Independent of the live session: holds the pinned ``version_id``, the
    ``state_json`` as approved, and the snapshot copied to the order's private
    prefix. Editing the catalog area/version or the session later never changes
    a placed order.
    """

    __tablename__ = "customization_order_items"
    __table_args__ = (
        Index("ix_customization_order_items_store_order", "store_id", "order_id"),
        Index(
            "ix_customization_order_items_store_order_item",
            "store_id",
            "order_item_id",
            unique=True,
        ),
    )

    order_id: uuid.UUID = Field(foreign_key="order_orders.id", index=True)
    order_item_id: uuid.UUID = Field(foreign_key="order_items.id", index=True)
    customization_session_id: uuid.UUID = Field(
        foreign_key="customization_sessions.id", index=True
    )
    platform_3d_model_version_id: uuid.UUID = Field(
        foreign_key="platform_3d_model_versions.id", index=True
    )
    state_json: dict[str, object] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="The approved editor state, frozen at order time",
    )
    snapshot_key: str | None = Field(
        default=None, max_length=500, description="Snapshot copied to the order prefix"
    )
