"""Catalog tables: products, variants, images, categories, inventory, collections.

All tables are scoped to a store via ``store_id`` (``StoreScopedMixin``) and use
soft delete (doc 07). API schemas live in ``schemas.py``; enums in ``enums.py``.
Money is stored as ``*_amount_minor`` (int) + ``*_currency`` (ISO 4217), per
INV-G1/D4; the :class:`app.core.money.Money` value object is built in code.
"""

import uuid

from sqlalchemy import JSON, Column, Index, text
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.catalog.enums import ProductStatus, ProductVariantStatus


class ProductBase(SQLModel):
    """Shared product fields (doc 09)."""

    name: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: ProductStatus = Field(default=ProductStatus.draft)
    price_amount_minor: int = Field(ge=0, description="Price in minor units (INV-D4)")
    price_currency: str = Field(max_length=3, description="ISO 4217 currency code")
    is_featured: bool = Field(default=False)


class Product(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    ProductBase,
    table=True,
):
    """A sellable product, scoped to a store.

    ``slug`` is unique among non-deleted products of the same store (partial
    unique index), so a store can reuse an archived product's slug, and two
    different stores may hold the same slug independently.
    """

    __tablename__ = "catalog_products"
    __table_args__ = (
        Index(
            "ix_catalog_products_store_slug_active",
            "store_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_catalog_products_store_status", "store_id", "status"),
        Index("ix_catalog_products_store_created", "store_id", "created_at"),
    )


class ProductVariant(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A variant of a product (e.g. a size/color combination).

    ``price_override_*`` is optional; when unset, the variant inherits the
    product's price.
    """

    __tablename__ = "catalog_product_variants"
    __table_args__ = (
        Index(
            "ix_catalog_variants_store_product_status",
            "store_id",
            "product_id",
            "status",
        ),
    )

    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    name: str = Field(max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    attributes: dict[str, str] | None = Field(default=None, sa_column=Column(JSON))
    price_override_amount_minor: int | None = Field(default=None, ge=0)
    price_override_currency: str | None = Field(default=None, max_length=3)
    status: ProductVariantStatus = Field(default=ProductVariantStatus.active)


class ProductImage(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """An image attached to a product, ordered by ``position``.

    ``media_file_id`` references ``media_files``; the foreign-key constraint is
    added in P2-MEDIA-02, when that table exists.
    """

    __tablename__ = "catalog_product_images"
    __table_args__ = (
        Index(
            "ix_catalog_images_store_product_position",
            "store_id",
            "product_id",
            "position",
        ),
    )

    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    media_file_id: uuid.UUID = Field(foreign_key="media_files.id", index=True)
    position: int = Field(default=0)


class CategoryBase(SQLModel):
    """Shared category fields."""

    name: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    description: str | None = Field(default=None)


class Category(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    CategoryBase,
    table=True,
):
    """A product category, scoped to a store (slug unique per active store)."""

    __tablename__ = "catalog_categories"
    __table_args__ = (
        Index(
            "ix_catalog_categories_store_slug_active",
            "store_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class ProductCategory(UUIDMixin, StoreScopedMixin, table=True):
    """Join table linking a product to a category (unique per pair)."""

    __tablename__ = "catalog_product_categories"
    __table_args__ = (
        Index(
            "ix_catalog_product_categories_pair",
            "product_id",
            "category_id",
            unique=True,
        ),
    )

    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    category_id: uuid.UUID = Field(foreign_key="catalog_categories.id", index=True)


class InventoryItem(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """Stock quantity for a product or one of its variants.

    ``variant_id`` is null for product-level stock.
    """

    __tablename__ = "catalog_inventory_items"
    __table_args__ = (
        Index(
            "ix_catalog_inventory_store_product_variant",
            "store_id",
            "product_id",
            "variant_id",
        ),
    )

    product_id: uuid.UUID = Field(foreign_key="catalog_products.id", index=True)
    variant_id: uuid.UUID | None = Field(
        default=None, foreign_key="catalog_product_variants.id", index=True
    )
    quantity: int = Field(default=0, ge=0)


class CollectionBase(SQLModel):
    """Shared collection (showcase) fields."""

    name: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)


class Collection(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    CollectionBase,
    table=True,
):
    """A storefront collection/showcase (e.g. home highlights)."""

    __tablename__ = "catalog_collections"
    __table_args__ = (
        Index(
            "ix_catalog_collections_store_slug_active",
            "store_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
