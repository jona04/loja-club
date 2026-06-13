"""CLI: upload an optimized GLB to the public 3D-models path on the CDN.

Reuses :mod:`app.core.storage` (INV-F2) — never touches boto3 directly. The
object is stored under the versioned, immutable key
``public/3d-models/{slug}/v{version}/model.glb`` and served by CloudFront; the
printed URL is what the catalog seed (``P7-CAT-01``) stores in
``platform_3d_model_versions.glb_url``.

Usage:
    uv run python scripts/upload_glb.py <local.glb> <slug> <version>

Example:
    uv run python scripts/upload_glb.py ../scripts/glb/dist/mug.glb ceramic-mug 1
"""

import sys
from pathlib import Path

from app.core import storage

_CONTENT_TYPE = "model/gltf-binary"


def model_key(slug: str, version: int) -> str:
    """Build the versioned public key for a catalog GLB.

    Args:
        slug: The model slug (e.g. ``ceramic-mug``).
        version: The model version number (1-based, immutable).

    Returns:
        The object key ``public/3d-models/{slug}/v{version}/model.glb``.
    """
    return f"public/3d-models/{slug}/v{version}/model.glb"


def upload_glb(local_path: Path, slug: str, version: int) -> str:
    """Upload a local GLB to its public CDN key and return the public URL.

    Args:
        local_path: Path to the optimized ``.glb`` file on disk.
        slug: The model slug.
        version: The model version number.

    Returns:
        The public CloudFront URL of the uploaded object.

    Raises:
        FileNotFoundError: If ``local_path`` does not exist.
    """
    key = model_key(slug, version)
    with local_path.open("rb") as fileobj:
        storage.upload_fileobj(key, fileobj, _CONTENT_TYPE)
    return storage.public_url(key)


def main() -> None:
    """Parse argv and upload the GLB, printing the resulting CDN URL.

    Raises:
        SystemExit: With usage if the arguments are missing/invalid.
    """
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: uv run python scripts/upload_glb.py <local.glb> <slug> <version>"
        )
    local_path = Path(sys.argv[1])
    slug = sys.argv[2]
    version = int(sys.argv[3])
    if not local_path.is_file():
        raise SystemExit(f"file not found: {local_path}")

    url = upload_glb(local_path, slug, version)
    print(url)  # noqa: T201 — the CDN URL is this CLI's output


if __name__ == "__main__":
    main()
