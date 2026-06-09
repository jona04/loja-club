"""Public DTOs for the storefront (customer-facing reads).

Lean, read-only shapes assembled from ``stores``/``catalog``/``content``; no
admin fields are exposed.
"""

import uuid

from sqlmodel import SQLModel

from app.modules.catalog.schemas import ImagePublic, ProductPublic


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


class StorefrontTheme(SQLModel):
    """Public appearance for rendering (active template + theme fields).

    Read-only: a store with no settings yet falls back to the default template
    (``classic``) without creating a row.
    """

    active_template_id: str
    banner_image_url: str | None = None
    headline: str | None = None
    featured_collection_id: uuid.UUID | None = None
    primary_color: str | None = None
    background_color: str | None = None
    font_family: str | None = None


class StorefrontProduct(ProductPublic):
    """A published product with its images, for storefront cards and detail."""

    images: list[ImagePublic] = []


class StorefrontHome(SQLModel):
    """The storefront home payload: store identity, active theme and highlights."""

    store: StorefrontStore
    theme: StorefrontTheme
    featured_products: list[StorefrontProduct]
