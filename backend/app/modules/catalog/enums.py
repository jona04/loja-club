"""Enumerations for the catalog module."""

from enum import Enum


class ProductStatus(str, Enum):
    """Lifecycle status of a catalog product (doc 09)."""

    draft = "draft"
    published = "published"
    archived = "archived"


class ProductVariantStatus(str, Enum):
    """Lifecycle status of a product variant."""

    active = "active"
    archived = "archived"
