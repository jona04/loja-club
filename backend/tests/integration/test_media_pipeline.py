"""Media pipeline tests: mocked S3 (moto) + an env-gated real S3/CloudFront smoke."""

import io
from collections.abc import Generator
from typing import Any

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs
import httpx
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from PIL import Image
from sqlmodel import Session

from app.core import storage
from app.core.api import AppError
from app.core.config import settings
from app.modules.media import services
from app.modules.media.enums import MediaStatus
from tests.utils.store import TenantContext, create_store


def _png_bytes(color: str = "red", size: tuple[int, int] = (1200, 900)) -> bytes:
    """Return the bytes of a freshly encoded PNG of ``size``."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> Generator[Any, None, None]:
    with mock_aws():
        monkeypatch.setattr(settings, "S3_BUCKET", "loja-club-test")
        monkeypatch.setattr(settings, "CDN_BASE_URL", "https://cdn.test")
        client = boto3.client("s3", region_name=settings.S3_REGION)
        client.create_bucket(
            Bucket="loja-club-test",
            CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION},
        )
        yield client


def test_validate_rejects_non_image() -> None:
    with pytest.raises(AppError):
        services.validate_image(content_type="application/pdf", size=10)


def test_validate_rejects_too_large() -> None:
    with pytest.raises(AppError):
        services.validate_image(
            content_type="image/png", size=services.MAX_UPLOAD_BYTES + 1
        )


def test_extension_sanitizes_and_falls_back() -> None:
    assert services._extension("photo.JPG", "image/png") == "jpg"
    assert services._extension(None, "image/jpeg") == "jpg"
    assert services._extension("evil.php", "image/png") == "png"


def test_store_original_uploads_and_records(db: Session, s3: Any) -> None:
    store = create_store(db)
    data = _png_bytes()
    media = services.store_original(
        db,
        store_id=store.id,
        owner_type="product",
        owner_id=None,
        data=data,
        filename="pic.png",
        content_type="image/png",
    )
    assert media.status == MediaStatus.processing
    assert media.size == len(data)
    assert media.url == f"https://cdn.test/{media.key}"
    obj = s3.get_object(Bucket="loja-club-test", Key=media.key)
    assert obj["ContentLength"] == len(data)


def test_store_original_rejects_corrupt_bytes(db: Session) -> None:
    with pytest.raises(AppError):
        services.store_original(
            db,
            store_id=create_store(db).id,
            owner_type="product",
            owner_id=None,
            data=b"not-an-image",
            filename="x.png",
            content_type="image/png",
        )


def test_generate_variants_creates_four(db: Session, s3: Any) -> None:
    store = create_store(db)
    media = services.store_original(
        db,
        store_id=store.id,
        owner_type="product",
        owner_id=None,
        data=_png_bytes(),
        filename="pic.png",
        content_type="image/png",
    )
    services.generate_variants(db, media)
    assert media.status == MediaStatus.ready
    assert set(media.variants or {}) == set(services.VARIANT_MAX_SIZES)
    for name in services.VARIANT_MAX_SIZES:
        s3.get_object(
            Bucket="loja-club-test", Key=services._variant_key(media.key, name)
        )


@pytest.mark.usefixtures("s3")
def test_media_scoped_by_store(db: Session) -> None:
    store_a = create_store(db, slug="store-a")
    store_b = create_store(db, slug="store-b")
    media_a = services.store_original(
        db,
        store_id=store_a.id,
        owner_type="product",
        owner_id=None,
        data=_png_bytes(),
        filename="a.png",
        content_type="image/png",
    )
    media_b = services.store_original(
        db,
        store_id=store_b.id,
        owner_type="product",
        owner_id=None,
        data=_png_bytes(),
        filename="b.png",
        content_type="image/png",
    )
    assert media_a.key.startswith(f"public/{store_a.id}/")
    assert media_b.key.startswith(f"public/{store_b.id}/")


@pytest.mark.usefixtures("s3")
def test_upload_route_creates_media(
    client: TestClient,
    two_stores: TenantContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _noop(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr("app.modules.media.routes.enqueue", _noop)
    resp = client.post(
        f"/api/v1/stores/{two_stores.store_a.id}/media",
        headers=two_stores.owner_a_headers,
        files={"file": ("pic.png", _png_bytes(), "image/png")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "processing"
    assert body["store_id"] == str(two_stores.store_a.id)


@pytest.mark.skipif(
    not settings.storage_enabled,
    reason="AWS storage not configured (set S3_BUCKET + credentials)",
)
def test_real_media_pipeline_smoke(db: Session) -> None:
    """Env-gated smoke: real S3 upload + variants + a CloudFront GET."""
    store = create_store(db)
    media = services.store_original(
        db,
        store_id=store.id,
        owner_type="product",
        owner_id=None,
        data=_png_bytes(),
        filename="smoke.png",
        content_type="image/png",
    )
    keys = [media.key] + [
        services._variant_key(media.key, name) for name in services.VARIANT_MAX_SIZES
    ]
    try:
        services.generate_variants(db, media)
        assert media.variants is not None
        resp = httpx.get(media.variants["thumbnail"], timeout=30)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("image/")
    finally:
        for key in keys:
            storage.delete(key)
