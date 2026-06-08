"""Storage abstraction: mocked S3 (moto) + an env-gated real S3 smoke."""

import io
import uuid
from collections.abc import Generator
from typing import Any

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs
import pytest
from moto import mock_aws

from app.core import storage
from app.core.config import settings


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


def test_upload_stores_object(s3: Any) -> None:
    storage.upload_fileobj("public/x.txt", io.BytesIO(b"hi"), "text/plain")
    body = s3.get_object(Bucket="loja-club-test", Key="public/x.txt")["Body"].read()
    assert body == b"hi"


@pytest.mark.usefixtures("s3")
def test_presigned_url_targets_key() -> None:
    storage.upload_fileobj(
        "private/a.bin", io.BytesIO(b"x"), "application/octet-stream"
    )
    url = storage.generate_presigned_url("private/a.bin", expires_in=120)
    assert url.startswith("https://")
    assert "private/a.bin" in url


def test_delete_removes_object(s3: Any) -> None:
    storage.upload_fileobj("public/del.txt", io.BytesIO(b"x"), "text/plain")
    storage.delete("public/del.txt")
    resp = s3.list_objects_v2(Bucket="loja-club-test", Prefix="public/del.txt")
    assert resp.get("KeyCount", 0) == 0


def test_public_url_uses_cdn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "CDN_BASE_URL", "https://cdn.test")
    assert storage.public_url("public/x.txt") == "https://cdn.test/public/x.txt"


@pytest.mark.skipif(
    not settings.storage_enabled,
    reason="AWS storage not configured (set S3_BUCKET + credentials)",
)
def test_real_s3_roundtrip() -> None:
    """Env-gated smoke against the real dev bucket (skipped without creds)."""
    key = f"test/smoke-{uuid.uuid4()}.txt"
    storage.upload_fileobj(key, io.BytesIO(b"smoke"), "text/plain")
    client = boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        head = client.head_object(Bucket=settings.S3_BUCKET, Key=key)
        assert head["ContentLength"] == 5
        assert key in storage.generate_presigned_url(key, expires_in=120)
    finally:
        storage.delete(key)
