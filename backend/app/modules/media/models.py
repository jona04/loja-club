"""Media tables: ``media_files`` (originals plus their optimized variants).

Files live on S3 (private bucket) and are served through CloudFront; the row
holds the keys/URLs, never the binary (doc 07/13). Scoped per store via
``store_id`` (``StoreScopedMixin``).
"""

import uuid

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.media.enums import MediaStatus


class MediaFile(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """An uploaded image: the original plus its generated variants.

    ``owner_type``/``owner_id`` say what the file belongs to (e.g. a product);
    ``owner_id`` is null until the file is attached. ``variants`` maps a variant
    name (``thumbnail``/``card``/``product``/``zoom``) to its CDN URL.
    """

    __tablename__ = "media_files"
    __table_args__ = (
        Index("ix_media_files_store_id_id", "store_id", "id"),
        Index("ix_media_files_store_owner", "store_id", "owner_type", "owner_id"),
    )

    owner_type: str = Field(max_length=50, index=True)
    owner_id: uuid.UUID | None = Field(default=None, index=True)
    key: str = Field(max_length=1024, unique=True)
    url: str = Field(max_length=2048)
    variants: dict[str, str] | None = Field(default=None, sa_column=Column(JSON))
    content_type: str = Field(max_length=100)
    size: int = Field(ge=0)
    status: MediaStatus = Field(default=MediaStatus.processing)
