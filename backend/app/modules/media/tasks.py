"""Worker tasks for the media module (arq)."""

import uuid
from typing import Any

from sqlmodel import Session

from app.core.db import engine
from app.modules.media import services
from app.modules.media.models import MediaFile


async def generate_image_variants(_ctx: dict[str, Any], media_id: str) -> None:
    """Worker task: generate the size variants for a media file.

    Args:
        _ctx: arq worker context (unused).
        media_id: The ``media_files`` id to process.
    """
    with Session(engine) as session:  # pragma: no cover - worker I/O glue
        media = session.get(MediaFile, uuid.UUID(media_id))
        if media is not None and media.deleted_at is None:
            services.generate_variants(session, media)
