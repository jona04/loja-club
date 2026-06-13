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
