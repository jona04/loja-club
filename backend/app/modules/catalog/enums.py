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


class ProductType(str, Enum):
    """What a product is, for the storefront and the add-to-cart gate (doc 22).

    - ``image``: a regular product (photos); may have variants; goes straight
      to the cart.
    - ``image_3d``: has a 3D model for viewing, but no customization; goes
      straight to the cart.
    - ``image_3d_customizable``: has a customizable 3D model — the customer must
      customize and approve before adding to the cart.

    All products are ``image`` in this phase; the 3D types are activated later
    (Fase 7), when a 3D model is generated and linked.
    """

    image = "image"
    image_3d = "image_3d"
    image_3d_customizable = "image_3d_customizable"


class ProductVariantStatus(str, Enum):
    """Lifecycle status of a product variant."""

    active = "active"
    archived = "archived"
