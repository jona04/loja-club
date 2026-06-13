"""DTOs for the platform 3D catalog (merchant-facing browse)."""

import uuid

from sqlmodel import SQLModel


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
