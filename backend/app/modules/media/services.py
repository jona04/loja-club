"""Media pipeline: validate, store the original on S3, and build size variants.

Domain code uses :mod:`app.core.storage`; the heavy image work runs in the
worker (:mod:`app.modules.media.tasks`). Originals and variants are public
objects served through CloudFront; the bucket itself is private (INV-F2).
"""

import io
import uuid

from PIL import Image
from sqlmodel import Session

from app.core import storage
from app.core.api import AppError
from app.modules.media.enums import MediaStatus
from app.modules.media.models import MediaFile

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
"""Maximum accepted upload size (10 MiB)."""

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
"""Accepted image MIME types."""

VARIANT_MAX_SIZES: dict[str, int] = {
    "thumbnail": 150,
    "card": 400,
    "product": 800,
    "zoom": 1600,
}
"""Variant name -> max bounding-box size (px); aspect ratio is preserved."""

_CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

_ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp", "gif"}


def _extension(filename: str | None, content_type: str) -> str:
    """Return a safe file extension from the filename, falling back to the MIME.

    Args:
        filename: The original (untrusted) filename, or ``None``.
        content_type: The already-validated MIME type.

    Returns:
        A lowercase extension restricted to known image types.
    """
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in _ALLOWED_EXTS:
            return ext
    return _CONTENT_TYPE_EXT.get(content_type, "bin")


def validate_image(*, content_type: str, size: int) -> None:
    """Validate an upload's MIME type and size.

    Args:
        content_type: The declared MIME type.
        size: The payload size in bytes.

    Raises:
        AppError: 415 if the type is not an accepted image; 413 if too large.
    """
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise AppError(
            "unsupported_media_type",
            f"Unsupported content type: {content_type}",
            status_code=415,
        )
    if size > MAX_UPLOAD_BYTES:
        raise AppError(
            "media_too_large", "File exceeds the maximum size", status_code=413
        )


def _assert_image(data: bytes) -> None:
    """Ensure ``data`` decodes as a real image.

    Args:
        data: The raw upload bytes.

    Raises:
        AppError: 422 if the bytes are not a valid image.
    """
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()
    except Exception as exc:
        raise AppError(
            "invalid_image", "File is not a valid image", status_code=422
        ) from exc


def _variant_key(key: str, name: str) -> str:
    """Return the S3 key for a named variant of ``key``.

    Args:
        key: The original object key.
        name: The variant name (e.g. ``thumbnail``).

    Returns:
        The variant key (``<base>_<name>.<ext>``).
    """
    if "." in key:
        base, ext = key.rsplit(".", 1)
        return f"{base}_{name}.{ext}"
    return f"{key}_{name}"


def _resize(data: bytes, max_size: int) -> bytes:
    """Return ``data`` resized to fit a ``max_size`` box, preserving format.

    Args:
        data: The original image bytes.
        max_size: Maximum width/height in pixels.

    Returns:
        The resized image encoded in the original format.
    """
    with Image.open(io.BytesIO(data)) as img:
        fmt = img.format or "PNG"
        img.thumbnail((max_size, max_size))
        out = io.BytesIO()
        img.save(out, format=fmt)
        return out.getvalue()


def store_original(
    session: Session,
    *,
    store_id: uuid.UUID,
    owner_type: str,
    owner_id: uuid.UUID | None,
    data: bytes,
    filename: str | None,
    content_type: str,
) -> MediaFile:
    """Validate the upload, store the original on S3 and record ``media_files``.

    Variant generation is enqueued separately by the caller (worker).

    Args:
        session: Active database session.
        store_id: Owning store.
        owner_type: What the media belongs to (e.g. ``product``).
        owner_id: Owner id, when already known (else ``None``).
        data: Raw image bytes.
        filename: Original filename; its extension (a known image one) is used
            for the stored key.
        content_type: The image MIME type.

    Returns:
        The created :class:`MediaFile` (status ``processing``).

    Raises:
        AppError: If validation fails (type/size/decode).
    """
    validate_image(content_type=content_type, size=len(data))
    _assert_image(data)
    ext = _extension(filename, content_type)
    key = f"public/{store_id}/media/{uuid.uuid4()}.{ext}"
    storage.upload_fileobj(key, io.BytesIO(data), content_type)
    media = MediaFile(
        store_id=store_id,
        owner_type=owner_type,
        owner_id=owner_id,
        key=key,
        url=storage.public_url(key),
        content_type=content_type,
        size=len(data),
        status=MediaStatus.processing,
    )
    session.add(media)
    session.commit()
    session.refresh(media)
    return media


def generate_variants(session: Session, media: MediaFile) -> None:
    """Build the optimized variants of ``media`` and mark it ready.

    Downloads the original from S3, generates each :data:`VARIANT_MAX_SIZES`
    rendition (aspect-preserving), uploads them and stores their CDN URLs.

    Args:
        session: Active database session.
        media: The media record whose original is already on S3.
    """
    original = storage.download(media.key)
    variants: dict[str, str] = {}
    for name, max_size in VARIANT_MAX_SIZES.items():
        resized = _resize(original, max_size)
        vkey = _variant_key(media.key, name)
        storage.upload_fileobj(vkey, io.BytesIO(resized), media.content_type)
        variants[name] = storage.public_url(vkey)
    media.variants = variants
    media.status = MediaStatus.ready
    session.add(media)
    session.commit()
