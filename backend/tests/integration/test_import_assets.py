"""import_assets: mocked S3 (moto) + mocked image downloads."""

from collections.abc import Generator
from typing import Any

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs
import httpx
import pytest
from moto import mock_aws

from app.core import storage
from app.core.config import settings
from app.modules.content import import_assets


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


@pytest.fixture
def writes(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str, dict[str, Any]]]:
    """Capture (and suppress) demo.json writes so tests never touch real files."""
    captured: list[tuple[str, dict[str, Any]]] = []
    monkeypatch.setattr(
        import_assets,
        "_write_demo",
        lambda tid, demo: captured.append((tid, demo)),
    )
    return captured


class _FakeResponse:
    """Minimal stand-in for an ``httpx.Response`` (content + status check)."""

    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        return None


def _demo(image: str) -> dict[str, Any]:
    return {
        "categories": [{"name": "Canecas", "slug": "canecas"}],
        "products": [
            {
                "name": "Caneca Térmica",
                "slug": "caneca-termica",
                "price": 5900,
                "category": "canecas",
                "image": image,
            }
        ],
    }


def test_import_uploads_rewrites_and_persists(
    s3: Any,
    writes: list[tuple[str, dict[str, Any]]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The source image is stored on S3, rewritten to the CDN, and persisted."""
    monkeypatch.setattr(
        import_assets, "load_demo", lambda _id: _demo("https://ux.example/gen_a.png")
    )
    calls: list[str] = []

    def fake_get(_self: Any, url: str, **_kwargs: Any) -> _FakeResponse:
        calls.append(url)
        return _FakeResponse(b"PNGDATA")

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    result = import_assets.import_demo_assets("aurora")

    cdn = "https://cdn.test/public/templates/aurora/gen_a.png"
    assert calls == ["https://ux.example/gen_a.png"]
    assert result["products"][0]["image"] == cdn
    body = s3.get_object(
        Bucket="loja-club-test", Key="public/templates/aurora/gen_a.png"
    )["Body"].read()
    assert body == b"PNGDATA"
    # The rewritten manifest is persisted back (CDN URL), not left on uxpilot.
    assert writes == [("aurora", result)]
    assert writes[0][1]["products"][0]["image"] == cdn


@pytest.mark.usefixtures("s3")
def test_import_skips_already_cdn_urls(
    writes: list[tuple[str, dict[str, Any]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A demo already on the CDN is unchanged, not re-downloaded, not re-written."""
    cdn = "https://cdn.test/public/templates/aurora/gen_a.png"
    monkeypatch.setattr(import_assets, "load_demo", lambda _id: _demo(cdn))

    def fail_get(_self: Any, _url: str, **_kwargs: Any) -> _FakeResponse:
        raise AssertionError("a CDN URL must not be re-downloaded")

    monkeypatch.setattr(httpx.Client, "get", fail_get)

    result = import_assets.import_demo_assets("aurora")
    assert result["products"][0]["image"] == cdn
    assert writes == []


@pytest.mark.parametrize("template_id", ["aurora", "bazar", "studio"])
def test_shipped_demo_is_valid(template_id: str) -> None:
    """Each shipped demo.json loads with coherent categories and products."""
    demo = import_assets.load_demo(template_id)
    assert demo is not None
    assert demo["categories"]
    assert demo["products"]
    for product in demo["products"]:
        assert str(product["image"]).startswith("https://")
        assert product["slug"] and product["name"]
        assert int(product["price"]) > 0


def test_load_demo_missing_returns_none() -> None:
    assert import_assets.load_demo("does-not-exist-xyzzy") is None


def test_import_demo_assets_no_demo_returns_empty() -> None:
    """A template without a demo.json imports to an empty manifest (no error)."""
    assert import_assets.import_demo_assets("does-not-exist-xyzzy") == {
        "categories": [],
        "products": [],
    }


@pytest.mark.skipif(
    not settings.storage_enabled,
    reason="AWS storage not configured (set S3_BUCKET + credentials)",
)
@pytest.mark.usefixtures("writes")
def test_real_import_smoke() -> None:
    """Env-gated: really resolve aurora's demo images to the dev CDN."""
    storage.reset_client()
    result = import_assets.import_demo_assets("aurora")
    images = [str(p["image"]) for p in result["products"]]
    assert images
    assert all(img.startswith(settings.CDN_BASE_URL.rstrip("/")) for img in images)
