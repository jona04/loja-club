"""Integration tests for the content (layout) panel routes."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.cache import cache_get, cache_set
from tests.utils.store import (
    TenantContext,
    create_member,
    create_user,
    member_headers,
)

BASE = "/api/v1/stores"


def test_list_templates_and_apply(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout"

    templates = client.get(f"{base}/templates", headers=h)
    assert templates.status_code == 200
    assert {t["id"] for t in templates.json()} >= {"aurora", "bazar", "studio"}

    # Default settings are created on first read, with the default template.
    got = client.get(base, headers=h)
    assert got.status_code == 200
    assert got.json()["active_template_id"] == "aurora"

    # Applying a template persists it AND drops the storefront read cache.
    cache_set(f"{a.id}:theme", "stale", prefix="store")
    applied = client.patch(base, headers=h, json={"active_template_id": "bazar"})
    assert applied.status_code == 200
    assert applied.json()["active_template_id"] == "bazar"
    assert cache_get(f"{a.id}:theme", prefix="store") is None


def test_apply_invalid_template_is_400(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    resp = client.patch(
        f"{BASE}/{a.id}/layout",
        headers=two_stores.owner_a_headers,
        json={"active_template_id": "nope"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "invalid_template"


def test_edit_appearance(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    resp = client.patch(
        f"{BASE}/{a.id}/layout",
        headers=two_stores.owner_a_headers,
        json={"headline": "Bem-vindo", "banner_image_url": "https://cdn/b.png"},
    )
    assert resp.status_code == 200
    assert resp.json()["headline"] == "Bem-vindo"


def test_preview_does_not_persist(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    preview = client.get(f"{BASE}/{a.id}/layout/preview/bazar", headers=h)
    assert preview.status_code == 200
    assert preview.json()["active_template_id"] == "bazar"
    # The active template stays the default after a preview.
    assert (
        client.get(f"{BASE}/{a.id}/layout", headers=h).json()["active_template_id"]
        == "aurora"
    )


def test_layout_isolated_from_other_store(
    client: TestClient, two_stores: TenantContext
) -> None:
    # Store B's owner is not a member of Store A → no access.
    resp = client.get(
        f"{BASE}/{two_stores.store_a.id}/layout",
        headers=two_stores.owner_b_headers,
    )
    assert resp.status_code == 403


def test_view_role_cannot_update(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    viewer = create_user(db)
    create_member(db, store=a, user=viewer, role_key="catalog")
    vh = member_headers(client, db, viewer)
    assert client.get(f"{BASE}/{a.id}/layout", headers=vh).status_code == 200
    blocked = client.patch(f"{BASE}/{a.id}/layout", headers=vh, json={"headline": "x"})
    assert blocked.status_code == 403
