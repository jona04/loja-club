"""HTTP routes for media uploads (panel)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile

from app.api.deps import SessionDep
from app.core.queue import enqueue
from app.modules.media import services
from app.modules.media.models import MediaFile
from app.modules.media.schemas import MediaPublic
from app.modules.stores.models import StoreMember
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/stores/{store_id}/media", tags=["media"])


@router.post("", response_model=MediaPublic, status_code=201)
async def upload_media(
    store_id: uuid.UUID,
    session: SessionDep,
    file: UploadFile,
    _perm: Annotated[
        StoreMember, Depends(require_permission("catalog.product.update"))
    ],
    owner_type: Annotated[str, Form()] = "product",
) -> MediaFile:
    """Upload an image: store the original on S3 and enqueue variant generation.

    Args:
        store_id: The active store id from the path.
        session: Active database session.
        file: The uploaded image.
        _perm: Authorization (requires ``catalog.product.update``).
        owner_type: What the media belongs to (default ``product``).

    Returns:
        The created media file (status ``processing``).
    """
    data = await file.read()
    media = services.store_original(
        session,
        store_id=store_id,
        owner_type=owner_type,
        owner_id=None,
        data=data,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
    )
    await enqueue("generate_image_variants", str(media.id))
    return media
