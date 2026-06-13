"""Storage-key helpers for the platform 3D catalog (single source of truth).

The model ``slug`` drives **both** the catalog row and the CDN path, so the GLB
URL is always derivable from ``slug`` + ``version``. The seed and the upload CLI
(``backend/scripts/upload_glb.py``) both go through here — never a hand-written
path — so the stored ``glb_url`` and the uploaded object can't diverge.
"""

from app.core import storage


def model_glb_key(slug: str, version: int) -> str:
    """Return the public CDN object key for a catalog model's GLB.

    Args:
        slug: The model slug (also the CDN path segment).
        version: The immutable version number.

    Returns:
        The key ``public/3d-models/{slug}/v{version}/model.glb``.
    """
    return f"public/3d-models/{slug}/v{version}/model.glb"


def model_glb_url(slug: str, version: int) -> str:
    """Return the public CDN (CloudFront) URL for a catalog model's GLB.

    Args:
        slug: The model slug.
        version: The immutable version number.

    Returns:
        The CDN URL of the model's GLB.
    """
    return storage.public_url(model_glb_key(slug, version))
