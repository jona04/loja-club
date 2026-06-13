"""Integration tests for the platform 3D catalog (seed, slug coupling, listing)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.config import settings
from app.modules.customization import repositories
from app.modules.customization.models import Platform3DModel
from app.modules.customization.repositories import MUG_SLUG
from app.modules.customization.storage import model_glb_url


def test_seed_creates_the_mug(db: Session) -> None:
    models = repositories.list_active_models(session=db)
    mug = next(m for m in models if m.slug == MUG_SLUG)

    version = repositories.get_active_version(session=db, model_id=mug.id)
    assert version is not None
    assert version.version == 1
    assert len(version.printable_areas) == 1
    assert version.printable_areas[0]["id"] == "front"
    assert "fonts" in version.text_config
    mimes = version.art_limits["mimes"]
    assert isinstance(mimes, list)
    assert "image/png" in mimes


def test_glb_url_is_derived_from_slug(db: Session) -> None:
    mug = next(
        m for m in repositories.list_active_models(session=db) if m.slug == MUG_SLUG
    )
    version = repositories.get_active_version(session=db, model_id=mug.id)
    assert version is not None
    # The stored URL must equal the single-source helper (slug == CDN path).
    assert version.glb_url == model_glb_url(MUG_SLUG, 1)
    assert version.glb_url.endswith(f"/3d-models/{MUG_SLUG}/v1/model.glb")


def test_seed_is_idempotent(db: Session) -> None:
    before = len(repositories.list_active_models(session=db))
    repositories.seed_platform_3d_models(session=db)
    after = len(repositories.list_active_models(session=db))
    assert before == after


def test_slug_unique_among_active(db: Session) -> None:
    db.add(Platform3DModel(name="Dup", category="caneca", slug="dupe"))
    db.commit()
    db.add(Platform3DModel(name="Dup 2", category="caneca", slug="dupe"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_list_active_excludes_inactive(db: Session) -> None:
    mug = next(
        m for m in repositories.list_active_models(session=db) if m.slug == MUG_SLUG
    )
    mug.is_active = False
    db.add(mug)
    db.commit()
    slugs = {m.slug for m in repositories.list_active_models(session=db)}
    assert MUG_SLUG not in slugs


def test_catalog_route_lists_models(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/3d-catalog/models",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    mug = next((m for m in data if m["slug"] == MUG_SLUG), None)
    assert mug is not None
    assert mug["active_version"]["version"] == 1
    assert mug["active_version"]["glb_url"].endswith(
        f"/3d-models/{MUG_SLUG}/v1/model.glb"
    )
    assert len(mug["active_version"]["printable_areas"]) == 1


def test_catalog_route_requires_auth(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/3d-catalog/models")
    assert response.status_code == 401
