"""Integration tests for platform-admin template asset uploads (mocked S3)."""

from collections.abc import Generator
from typing import Any

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from sqlmodel import Session

from app.core import storage
from app.core.api import AppError
from app.core.config import settings
from app.modules.platform_admin import services


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> Generator[Any, None, None]:
    with mock_aws():
        storage.reset_client()
        monkeypatch.setattr(settings, "S3_BUCKET", "loja-club-test")
        monkeypatch.setattr(settings, "CDN_BASE_URL", "https://cdn.test")
        client = boto3.client("s3", region_name=settings.S3_REGION)
        client.create_bucket(
            Bucket="loja-club-test",
            CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION},
        )
        yield client


@pytest.mark.usefixtures("s3")
def test_set_thumbnail_uploads_and_links(db: Session) -> None:
    template = services.set_template_thumbnail(
        session=db, template_id="aurora", data=b"\x89PNG fake", content_type="image/png"
    )
    assert template.preview_image_url is not None
    assert template.preview_image_url.startswith(
        "https://cdn.test/public/templates/aurora/thumbnail-"
    )
    assert template.preview_image_url.endswith(".png")


@pytest.mark.usefixtures("s3")
def test_set_thumbnail_invalid_type(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        services.set_template_thumbnail(
            session=db, template_id="aurora", data=b"x", content_type="text/plain"
        )
    assert exc.value.status_code == 422


@pytest.mark.usefixtures("s3")
def test_set_thumbnail_template_not_found(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        services.set_template_thumbnail(
            session=db, template_id="nope", data=b"x", content_type="image/png"
        )
    assert exc.value.status_code == 404


@pytest.mark.usefixtures("s3")
def test_upload_thumbnail_over_http(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/platform/templates/bazar/thumbnail",
        headers=superuser_token_headers,
        files={"file": ("thumb.png", b"\x89PNG fake", "image/png")},
    )
    assert r.status_code == 200
    assert r.json()["preview_image_url"].startswith("https://cdn.test/")


@pytest.mark.usefixtures("s3")
def test_upload_thumbnail_requires_platform_permission(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/platform/templates/aurora/thumbnail",
        headers=normal_user_token_headers,
        files={"file": ("thumb.png", b"x", "image/png")},
    )
    assert r.status_code == 403
