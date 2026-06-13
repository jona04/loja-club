"""DTOs for the platform 3D catalog (merchant-facing browse)."""

import uuid

from sqlmodel import SQLModel

from app.modules.catalog.enums import ProductType


class Platform3DModelVersionPublic(SQLModel):
    """The active version of a catalog model, as exposed to the merchant."""

    id: uuid.UUID
    version: int
    glb_url: str
    printable_areas: list[dict[str, object]]
    text_config: dict[str, object]
    art_limits: dict[str, object]


class Platform3DModelPublic(SQLModel):
    """A catalog model plus its active version (or ``None`` if none active)."""

    id: uuid.UUID
    name: str
    category: str
    slug: str
    active_version: Platform3DModelVersionPublic | None


class Platform3DModelVersionAdmin(SQLModel):
    """A model version as seen by the admin (includes ``is_active``)."""

    id: uuid.UUID
    version: int
    glb_url: str
    printable_areas: list[dict[str, object]]
    text_config: dict[str, object]
    art_limits: dict[str, object]
    is_active: bool


class Platform3DModelAdmin(SQLModel):
    """A catalog model for the admin (includes ``is_active`` + active version)."""

    id: uuid.UUID
    name: str
    category: str
    slug: str
    is_active: bool
    active_version: Platform3DModelVersionAdmin | None


class Platform3DModelUpdate(SQLModel):
    """Partial update of a catalog model's metadata/visibility."""

    name: str | None = None
    category: str | None = None
    is_active: bool | None = None


class Platform3DModelVersionUpdate(SQLModel):
    """Partial update of a version's editor parameters/visibility."""

    printable_areas: list[dict[str, object]] | None = None
    text_config: dict[str, object] | None = None
    art_limits: dict[str, object] | None = None
    is_active: bool | None = None


class ProductModelLink(SQLModel):
    """Request to link a product to a catalog 3D model (merchant choice)."""

    platform_3d_model_id: uuid.UUID
    type: ProductType
    production_notes: str | None = None


class ProductModelSettingsPublic(SQLModel):
    """A product's current 3D-model link, for the merchant panel."""

    product_id: uuid.UUID
    type: ProductType
    platform_3d_model_id: uuid.UUID
    model_name: str
    model_slug: str
    model_category: str
    production_notes: str | None
