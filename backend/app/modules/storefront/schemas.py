"""Public DTOs for the storefront (customer-facing reads).

Lean, read-only shapes assembled from ``stores``/``catalog``/``content``; no
admin fields are exposed.
"""

import uuid

from sqlmodel import SQLModel

from app.modules.catalog.schemas import (
    CategoryPublic,
    ImagePublic,
    ProductPublic,
)


class StorefrontStore(SQLModel):
    """Public store identity/contact (from ``stores``/``store_settings``)."""

    name: str
    slug: str
    currency: str
    locale: str
    public_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    whatsapp_number: str | None = None
    return_policy: str | None = None
    exchange_policy: str | None = None
    privacy_policy: str | None = None


class StorefrontTheme(SQLModel):
    """Public appearance for rendering (active template + theme fields + chrome).

    Read-only: a store with no settings yet falls back to the default template
    without creating a row. ``settings`` are the active template's schema-driven
    chrome values (defaults merged with the store's overrides).
    """

    active_template_id: str
    banner_image_url: str | None = None
    headline: str | None = None
    featured_collection_id: uuid.UUID | None = None
    primary_color: str | None = None
    background_color: str | None = None
    font_family: str | None = None
    settings: dict[str, object] = {}


class StorefrontVariant(SQLModel):
    """A purchasable variant on the product page (name + effective price + stock).

    ``price_*`` is the **effective** price (the variant override, else the
    product's). ``available_quantity`` is ``None`` when stock isn't tracked
    (unlimited); ``in_stock`` already folds that in.
    """

    id: uuid.UUID
    name: str
    attributes: dict[str, str] | None = None
    price_amount_minor: int
    price_currency: str
    in_stock: bool
    available_quantity: int | None = None


class StorefrontProduct(ProductPublic):
    """A published product with its images, for storefront cards and detail.

    On the product **detail** it also carries the active ``variants`` and stock
    (``in_stock`` / ``available_quantity``, product-level for variant-less
    products); cards/home leave ``variants`` empty.
    """

    images: list[ImagePublic] = []
    variants: list[StorefrontVariant] = []
    in_stock: bool = True
    available_quantity: int | None = None


class StorefrontCategorySection(SQLModel):
    """A category with its first products (templates with category sections)."""

    category: CategoryPublic
    products: list[StorefrontProduct]


class StorefrontHome(SQLModel):
    """The storefront home payload: store identity, active theme and highlights."""

    store: StorefrontStore
    theme: StorefrontTheme
    featured_products: list[StorefrontProduct]
    category_sections: list[StorefrontCategorySection] = []
