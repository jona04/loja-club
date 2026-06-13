"""Platform 3D catalog tables (``platform_3d_models`` / ``_versions``).

Platform-owned (no ``store_id``): the Kriar 3D catalog is global, seeded by the
dev. A model has one or more **immutable** versions — the optimized GLB on the
CDN plus the JSON parameters that drive the storefront editor (printable areas,
text limits, art limits). The ``slug`` is the single source of truth for the CDN
path (see :mod:`app.modules.customization.storage`). Store-scoped,
merchant-generated models are a separate path.
"""

import uuid

from sqlalchemy import JSON, Column, Index, text
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Platform3DModelBase(SQLModel):
    """Shared catalog-model fields."""

    name: str = Field(max_length=100)
    category: str = Field(max_length=50, description="Product family, e.g. 'caneca'")
    slug: str = Field(
        max_length=100,
        description="Stable unique identifier; also the CDN path segment",
    )
    is_active: bool = True


class Platform3DModel(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, Platform3DModelBase, table=True
):
    """A public 3D catalog model (platform-owned, seeded).

    ``slug`` is unique among non-deleted models (partial unique index) and is the
    single source of truth for the GLB's CDN path.
    """

    __tablename__ = "platform_3d_models"
    __table_args__ = (
        Index(
            "ix_platform_3d_models_slug_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_platform_3d_models_category", "category"),
    )


class Platform3DModelVersionBase(SQLModel):
    """Shared version fields: the GLB plus the editor parameters."""

    version: int = Field(ge=1, description="Immutable version number (1-based)")
    glb_url: str = Field(max_length=500, description="CDN URL of the optimized GLB")
    printable_areas: list[dict[str, object]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Decal projector + rectangle and limits, per printable area",
    )
    text_config: dict[str, object] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Allowed fonts and text size limits",
    )
    art_limits: dict[str, object] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Accepted mimes, max bytes, min dimension",
    )
    is_active: bool = True


class Platform3DModelVersion(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Platform3DModelVersionBase,
    table=True,
):
    """An immutable version of a catalog model (GLB + editor parameters).

    The GLB is immutable per version (a new GLB is a new version); the
    ``printable_areas`` / ``text_config`` / ``art_limits`` JSONs stay editable in
    the admin within the version.
    """

    __tablename__ = "platform_3d_model_versions"
    __table_args__ = (
        Index(
            "ix_platform_3d_model_versions_model_version",
            "model_id",
            "version",
            unique=True,
        ),
    )

    model_id: uuid.UUID = Field(foreign_key="platform_3d_models.id", index=True)
