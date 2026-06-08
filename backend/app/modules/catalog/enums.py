"""Enumerations for the catalog module."""

from enum import Enum


class ProductStatus(str, Enum):
    """Lifecycle status of a catalog product (doc 09).

    - ``draft``: never published; editable; the slug follows the name.
    - ``published``: live on the storefront; the slug is fixed.
    - ``archived``: taken offline but kept — reversible via publish; the slug
      stays reserved.

    Deleting a product is a **soft delete** (``deleted_at``), not a status.
    """

    draft = "draft"
    published = "published"
    archived = "archived"


class ProductVariantStatus(str, Enum):
    """Lifecycle status of a product variant."""

    active = "active"
    archived = "archived"
