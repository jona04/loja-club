"""Integration tests for linking a product to a catalog 3D model (panel API)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.customization import repositories
from app.modules.customization.models import Platform3DModel
from app.modules.customization.repositories import MUG_SLUG
from tests.utils.store import (
    TenantContext,
    create_member,
    create_user,
    member_headers,
)

BASE = "/api/v1/stores"


def _mug(db: Session) -> Platform3DModel:
    """Return the seeded ceramic-mug catalog model."""
    return next(
        m for m in repositories.list_active_models(session=db) if m.slug == MUG_SLUG
    )


def _create_product(
    client: TestClient,
    store_id: uuid.UUID,
    headers: dict[str, str],
    *,
    slug: str = "mug",
) -> str:
    """Create a draft product in the store and return its id."""
    cat = client.post(
        f"{BASE}/{store_id}/categories", headers=headers, json={"name": "Canecas"}
    ).json()["id"]
    resp = client.post(
        f"{BASE}/{store_id}/products",
        headers=headers,
        json={
            "name": "Mug",
            "slug": slug,
            "price_amount_minor": 1500,
            "category_ids": [cat],
        },
    )
    assert resp.status_code == 201, resp.text
    product_id: str = resp.json()["id"]
    return product_id


def test_link_sets_type_and_settings(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    model_id = str(_mug(db).id)

    resp = client.put(
        f"{BASE}/{a.id}/products/{pid}/3d-model",
        headers=h,
        json={
            "platform_3d_model_id": model_id,
            "type": "image_3d_customizable",
            "production_notes": "centralizar a arte",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["platform_3d_model_id"] == model_id
    assert body["model_slug"] == MUG_SLUG
    assert body["type"] == "image_3d_customizable"
    assert body["production_notes"] == "centralizar a arte"

    # The product's type is now the 3D type.
    prod = client.get(f"{BASE}/{a.id}/products/{pid}", headers=h).json()
    assert prod["type"] == "image_3d_customizable"

    # The link is readable back.
    got = client.get(f"{BASE}/{a.id}/products/{pid}/3d-model", headers=h).json()
    assert got["platform_3d_model_id"] == model_id


def test_get_returns_null_when_unlinked(
    client: TestClient, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    resp = client.get(f"{BASE}/{a.id}/products/{pid}/3d-model", headers=h)
    assert resp.status_code == 200
    assert resp.json() is None


def test_relink_updates_model_type_and_notes(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    model_id = str(_mug(db).id)
    url = f"{BASE}/{a.id}/products/{pid}/3d-model"

    client.put(
        url,
        headers=h,
        json={"platform_3d_model_id": model_id, "type": "image_3d_customizable"},
    )
    # Re-link: same product, now view-only, new notes (upsert, not a 2nd row).
    resp = client.put(
        url,
        headers=h,
        json={
            "platform_3d_model_id": model_id,
            "type": "image_3d",
            "production_notes": "sem personalização",
        },
    )
    assert resp.status_code == 200, resp.text
    got = client.get(url, headers=h).json()
    assert got["type"] == "image_3d"
    assert got["production_notes"] == "sem personalização"


def test_unlink_reverts_type(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    model_id = str(_mug(db).id)
    url = f"{BASE}/{a.id}/products/{pid}/3d-model"
    client.put(
        url,
        headers=h,
        json={"platform_3d_model_id": model_id, "type": "image_3d_customizable"},
    )

    resp = client.delete(url, headers=h)
    assert resp.status_code == 204

    prod = client.get(f"{BASE}/{a.id}/products/{pid}", headers=h).json()
    assert prod["type"] == "image"
    assert client.get(url, headers=h).json() is None


def test_unlink_without_link_is_404(
    client: TestClient, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    resp = client.delete(f"{BASE}/{a.id}/products/{pid}/3d-model", headers=h)
    assert resp.status_code == 404


def test_link_rejects_non_3d_type(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    model_id = str(_mug(db).id)
    resp = client.put(
        f"{BASE}/{a.id}/products/{pid}/3d-model",
        headers=h,
        json={"platform_3d_model_id": model_id, "type": "image"},
    )
    assert resp.status_code == 422


def test_link_rejects_disabled_model(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    mug = _mug(db)
    mug.is_active = False
    db.add(mug)
    db.commit()

    resp = client.put(
        f"{BASE}/{a.id}/products/{pid}/3d-model",
        headers=h,
        json={"platform_3d_model_id": str(mug.id), "type": "image_3d"},
    )
    assert resp.status_code == 422


def test_link_rejects_model_without_active_version(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    model = Platform3DModel(
        name="Sem versão", category="caneca", slug="no-version", is_active=True
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    resp = client.put(
        f"{BASE}/{a.id}/products/{pid}/3d-model",
        headers=h,
        json={"platform_3d_model_id": str(model.id), "type": "image_3d"},
    )
    assert resp.status_code == 422


def test_other_store_cannot_link_foreign_product(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    b, hb = two_stores.store_b, two_stores.owner_b_headers
    pid = _create_product(client, a.id, h)
    model_id = str(_mug(db).id)

    # Store B's owner addressing B's own URL but A's product -> not found.
    resp = client.put(
        f"{BASE}/{b.id}/products/{pid}/3d-model",
        headers=hb,
        json={"platform_3d_model_id": model_id, "type": "image_3d"},
    )
    assert resp.status_code == 404


def test_link_requires_assign_permission(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)
    model_id = str(_mug(db).id)

    # A 'support' member lacks customization.models.assign.
    support = create_user(db)
    create_member(db, store=a, user=support, role_key="support")
    sh = member_headers(client, db, support)

    resp = client.put(
        f"{BASE}/{a.id}/products/{pid}/3d-model",
        headers=sh,
        json={"platform_3d_model_id": model_id, "type": "image_3d"},
    )
    assert resp.status_code == 403
