"""Import a template's demo assets (images) into the CDN.

A template's ``demo.json`` ships with the original image URLs (the uxpilot
sources). This module downloads each image, stores it on S3 (served by
CloudFront) and rewrites the references to the CDN URL — so the demo store
(``P5-DEMO-02``) and the storefront no longer depend on the source URLs.

Idempotent: a URL that already points at the CDN is returned unchanged and
never re-downloaded; each source maps to a deterministic key, so re-imports
overwrite rather than duplicate.
"""

import io
import json
from pathlib import Path
from typing import Any

import httpx

from app.core import storage
from app.core.config import settings

_TEMPLATES_DIR = (
    Path(__file__).resolve().parents[4] / "frontend-storefront" / "templates"
)

_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".avif": "image/avif",
}


def load_demo(template_id: str) -> dict[str, Any] | None:
    """Load a template's ``demo.json`` (categories + products), or ``None``.

    Args:
        template_id: The template id (folder under the storefront templates).

    Returns:
        The parsed demo manifest, or ``None`` when the file is absent.
    """
    path = _TEMPLATES_DIR / template_id / "demo.json"
    if not path.is_file():
        return None
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _write_demo(template_id: str, demo: dict[str, Any]) -> None:
    """Persist the (rewritten) demo manifest back to the template's demo.json.

    So the committed manifest points at our CDN and no longer depends on the
    source (uxpilot) URLs.

    Args:
        template_id: The template whose manifest is written.
        demo: The manifest to serialize.
    """
    path = _TEMPLATES_DIR / template_id / "demo.json"
    path.write_text(
        json.dumps(demo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _is_cdn_url(url: str) -> bool:
    """Return whether ``url`` already points at the configured CDN.

    Args:
        url: The image URL to test.

    Returns:
        ``True`` if the URL is already a CDN URL (no import needed).
    """
    return url.startswith(settings.CDN_BASE_URL.rstrip("/"))


def _asset_key(template_id: str, url: str) -> str:
    """Build the deterministic S3 key for a template asset URL.

    Args:
        template_id: The owning template id.
        url: The source image URL.

    Returns:
        A stable ``public/templates/{id}/{filename}`` key — same source URL maps
        to the same key, so re-imports overwrite instead of duplicating.
    """
    filename = url.rstrip("/").rsplit("/", 1)[-1].split("?")[0] or "asset"
    return f"public/templates/{template_id}/{filename}"


def _ensure_cdn(client: httpx.Client, template_id: str, url: str) -> str:
    """Ensure ``url``'s image is on the CDN, returning the CDN URL.

    Already-CDN URLs are returned unchanged (idempotent). Otherwise the image is
    downloaded and uploaded to S3 under a deterministic key.

    Args:
        client: An open HTTP client used to download the source image.
        template_id: The owning template id (used in the S3 key).
        url: The source image URL.

    Returns:
        The CDN URL of the stored image.

    Raises:
        httpx.HTTPStatusError: If the source download returns an error status.
    """
    if _is_cdn_url(url):
        return url
    key = _asset_key(template_id, url)
    response = client.get(url, follow_redirects=True)
    response.raise_for_status()
    content_type = _CONTENT_TYPES.get(
        Path(key).suffix.lower(), "application/octet-stream"
    )
    storage.upload_fileobj(key, io.BytesIO(response.content), content_type)
    return storage.public_url(key)


def import_demo_assets(template_id: str) -> dict[str, Any]:
    """Import a template's demo images into the CDN and persist the manifest.

    Downloads each product image that is not yet on the CDN, stores it, rewrites
    the manifest's image URLs to the CDN, and — when anything changed — writes
    the rewritten ``demo.json`` back, so the committed manifest stops depending
    on the source (uxpilot) URLs.

    Args:
        template_id: The template whose demo assets are imported.

    Returns:
        The demo manifest (``categories`` + ``products``) with CDN image URLs;
        an empty manifest when the template has no ``demo.json``.
    """
    demo = load_demo(template_id)
    if demo is None:
        return {"categories": [], "products": []}
    products: list[dict[str, Any]] = demo.get("products", [])
    changed = False
    with httpx.Client(timeout=30.0) as client:
        for product in products:
            image = product.get("image")
            if isinstance(image, str) and image and not _is_cdn_url(image):
                product["image"] = _ensure_cdn(client, template_id, image)
                changed = True
    if changed:
        _write_demo(template_id, demo)
    return demo
