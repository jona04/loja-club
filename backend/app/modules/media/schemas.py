"""API request/response schemas for the media module."""

import uuid

from sqlmodel import SQLModel

from app.modules.media.enums import MediaStatus


class MediaPublic(SQLModel):
    """Public representation of an uploaded media file."""

    id: uuid.UUID
    store_id: uuid.UUID
    owner_type: str
    owner_id: uuid.UUID | None
    key: str
    url: str
    variants: dict[str, str] | None
    content_type: str
    size: int
    status: MediaStatus
