"""Object storage abstraction over AWS S3 (boto3).

Domain code uses these helpers and never imports boto3 directly (INV-F2). The
bucket is private (S3 Block Public Access); public objects are served through
CloudFront via :func:`public_url`, and private ones via presigned URLs
(:func:`generate_presigned_url`).
"""

from typing import Any, BinaryIO

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs

from app.core.config import settings

_client: Any = None


def _s3_client() -> Any:
    """Return the shared S3 client, creating it on first use (INV-F6).

    The boto3 client (and its connection pool) is reused process-wide. Tests
    call :func:`reset_client` to rebuild it inside an active ``moto`` context.

    Returns:
        A cached boto3 S3 client.
    """
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        )
    return _client


def reset_client() -> None:
    """Drop the cached S3 client so the next call rebuilds it.

    Used by tests to recreate the client inside an active ``moto`` mock context
    (or with the current credentials).
    """
    global _client
    _client = None


def close_client() -> None:
    """Close and drop the cached S3 client (on app shutdown, INV-F6)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def upload_fileobj(key: str, fileobj: BinaryIO, content_type: str) -> None:
    """Upload a file object to the bucket under ``key`` (stored privately).

    Args:
        key: Object key; the caller chooses the prefix (e.g. ``public/...`` or
            ``private/{store_id}/...``).
        fileobj: A binary file-like object to upload.
        content_type: The object's MIME type.
    """
    _s3_client().put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=fileobj,
        ContentType=content_type,
    )


def generate_presigned_url(key: str, *, expires_in: int = 3600) -> str:
    """Return a time-limited presigned GET URL for a private object.

    Args:
        key: Object key.
        expires_in: URL validity in seconds.

    Returns:
        A presigned HTTPS URL granting temporary read access.
    """
    url: str = _s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )
    return url


def delete(key: str) -> None:
    """Delete an object from the bucket.

    Args:
        key: Object key to delete.
    """
    _s3_client().delete_object(Bucket=settings.S3_BUCKET, Key=key)


def download(key: str) -> bytes:
    """Download an object's bytes from the bucket.

    Args:
        key: Object key to fetch.

    Returns:
        The object's raw bytes.
    """
    obj = _s3_client().get_object(Bucket=settings.S3_BUCKET, Key=key)
    data: bytes = obj["Body"].read()
    return data


def public_url(key: str) -> str:
    """Return the public CloudFront (CDN) URL for ``key``.

    Args:
        key: Object key of a public object.

    Returns:
        The CDN URL (``{CDN_BASE_URL}/{key}``).
    """
    base = settings.CDN_BASE_URL.rstrip("/")
    return f"{base}/{key.lstrip('/')}"
