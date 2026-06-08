"""API request/response schemas for the catalog module."""

import uuid

from sqlmodel import Field, SQLModel

from app.modules.catalog.enums import ProductVariantStatus
from app.modules.catalog.models import CategoryBase, ProductBase

# --- Products ---


class ProductCreate(SQLModel):
    """Fields accepted when creating a product (status starts as ``draft``)."""

    name: str = Field(max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    price_amount_minor: int = Field(ge=0)
    price_currency: str | None = Field(default=None, max_length=3)
    is_featured: bool = False


class ProductUpdate(SQLModel):
    """Partial update for a product (unset fields are left unchanged)."""

    name: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    price_amount_minor: int | None = Field(default=None, ge=0)
    price_currency: str | None = Field(default=None, max_length=3)
    is_featured: bool | None = None


class ProductPublic(ProductBase):
    """Public representation of a product."""

    id: uuid.UUID
    store_id: uuid.UUID


# --- Categories ---


class CategoryCreate(SQLModel):
    """Fields accepted when creating a category."""

    name: str = Field(max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None


class CategoryUpdate(SQLModel):
    """Partial update for a category."""

    name: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None


class CategoryPublic(CategoryBase):
    """Public representation of a category."""

    id: uuid.UUID
    store_id: uuid.UUID


# --- Variants ---


class VariantCreate(SQLModel):
    """Fields accepted when creating a product variant."""

    name: str = Field(max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    attributes: dict[str, str] | None = None
    price_override_amount_minor: int | None = Field(default=None, ge=0)
    price_override_currency: str | None = Field(default=None, max_length=3)


class VariantUpdate(SQLModel):
    """Partial update for a product variant."""

    name: str | None = Field(default=None, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    attributes: dict[str, str] | None = None
    price_override_amount_minor: int | None = Field(default=None, ge=0)
    price_override_currency: str | None = Field(default=None, max_length=3)


class VariantPublic(SQLModel):
    """Public representation of a product variant."""

    id: uuid.UUID
    store_id: uuid.UUID
    product_id: uuid.UUID
    name: str
    sku: str | None
    attributes: dict[str, str] | None
    price_override_amount_minor: int | None
    price_override_currency: str | None
    status: ProductVariantStatus


# --- Images ---


class ImageAttach(SQLModel):
    """Link a (processed) media file to a product at a position."""

    media_file_id: uuid.UUID
    position: int = Field(default=0, ge=0)


class ImagePublic(SQLModel):
    """Public representation of a product image link."""

    id: uuid.UUID
    store_id: uuid.UUID
    product_id: uuid.UUID
    media_file_id: uuid.UUID
    position: int


# --- Inventory ---


class InventorySet(SQLModel):
    """Set the stock quantity for a product (optionally a specific variant)."""

    variant_id: uuid.UUID | None = None
    quantity: int = Field(ge=0)


class InventoryPublic(SQLModel):
    """Public representation of a stock entry."""

    id: uuid.UUID
    store_id: uuid.UUID
    product_id: uuid.UUID
    variant_id: uuid.UUID | None
    quantity: int
