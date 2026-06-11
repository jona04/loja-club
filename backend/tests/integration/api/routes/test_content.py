"""Integration tests for the content (layout) panel routes."""

from fastapi.testclient import TestClient
from sqlmodel import Session, col, select

from app.core.cache import cache_get, cache_set
from app.modules.content.models import ContentMenuItem
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


def test_template_settings_default_empty(
    client: TestClient, two_stores: TenantContext
) -> None:
    """A store with no overrides reads its active template + empty settings."""
    a = two_stores.store_a
    resp = client.get(
        f"{BASE}/{a.id}/layout/settings", headers=two_stores.owner_a_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["template_id"] == "aurora"
    assert body["settings"] == {}


def test_template_settings_save_and_read_back(
    client: TestClient, two_stores: TenantContext
) -> None:
    """PATCH saves the overrides (validated), drops the cache, and GET reflects."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/settings"

    cache_set(f"{a.id}:theme", "stale", prefix="store")
    saved = client.patch(
        base,
        headers=h,
        json={
            "settings": {
                "announcement_text": "Frete grátis",
                "show_trust_badges": False,
            }
        },
    )
    assert saved.status_code == 200
    assert saved.json()["settings"] == {
        "announcement_text": "Frete grátis",
        "show_trust_badges": False,
    }
    assert cache_get(f"{a.id}:theme", prefix="store") is None
    got = client.get(base, headers=h)
    assert got.json()["settings"]["announcement_text"] == "Frete grátis"


def test_template_settings_unknown_key_is_422(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    resp = client.patch(
        f"{BASE}/{a.id}/layout/settings",
        headers=two_stores.owner_a_headers,
        json={"settings": {"nope": "x"}},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_setting"


def test_template_settings_type_and_length_are_422(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/settings"
    bad_type = client.patch(
        base, headers=h, json={"settings": {"show_trust_badges": "yes"}}
    )
    assert bad_type.status_code == 422
    over = client.patch(
        base, headers=h, json={"settings": {"announcement_text": "x" * 121}}
    )
    assert over.status_code == 422


def test_template_settings_reset_soft_deletes(
    client: TestClient, two_stores: TenantContext
) -> None:
    """DELETE resets to defaults; a later save re-creates the row (unique holds)."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/settings"

    client.patch(base, headers=h, json={"settings": {"announcement_text": "hi"}})
    reset = client.delete(base, headers=h)
    assert reset.status_code == 200
    assert reset.json()["settings"] == {}
    assert client.get(base, headers=h).json()["settings"] == {}
    again = client.patch(
        base, headers=h, json={"settings": {"announcement_text": "again"}}
    )
    assert again.status_code == 200
    assert again.json()["settings"]["announcement_text"] == "again"


def test_template_settings_viewer_cannot_write(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    viewer = create_user(db)
    create_member(db, store=a, user=viewer, role_key="catalog")
    vh = member_headers(client, db, viewer)
    base = f"{BASE}/{a.id}/layout/settings"
    assert client.get(base, headers=vh).status_code == 200
    assert client.patch(base, headers=vh, json={"settings": {}}).status_code == 403
    assert client.delete(base, headers=vh).status_code == 403


def test_my_templates_lists_customized(
    client: TestClient, two_stores: TenantContext
) -> None:
    """`/settings/mine` lists the templates the store has customized."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout"
    assert client.get(f"{base}/settings/mine", headers=h).json() == []
    client.patch(
        f"{base}/settings",
        headers=h,
        json={"settings": {"announcement_text": "x"}},
    )
    assert client.get(f"{base}/settings/mine", headers=h).json() == ["aurora"]
    client.delete(f"{base}/settings", headers=h)
    assert client.get(f"{base}/settings/mine", headers=h).json() == []


# --- Editorial pages -------------------------------------------------------


def test_pages_crud(client: TestClient, two_stores: TenantContext) -> None:
    """Create, list, update and delete a page; create drops the read cache."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/pages"

    cache_set(f"{a.id}:home", "stale", prefix="store")
    created = client.post(
        base, headers=h, json={"slug": "sobre", "title": "Sobre", "body": "Olá"}
    )
    assert created.status_code == 200
    page_id = created.json()["id"]
    assert created.json()["is_published"] is False
    assert cache_get(f"{a.id}:home", prefix="store") is None

    listed = client.get(base, headers=h)
    assert [p["slug"] for p in listed.json()] == ["sobre"]

    updated = client.patch(
        f"{base}/{page_id}",
        headers=h,
        json={"slug": "about", "body": "Hi", "is_published": True},
    )
    assert updated.status_code == 200
    assert updated.json()["slug"] == "about"
    assert updated.json()["is_published"] is True

    assert client.delete(f"{base}/{page_id}", headers=h).status_code == 204
    assert client.get(base, headers=h).json() == []


def test_page_duplicate_slug_is_409(
    client: TestClient, two_stores: TenantContext
) -> None:
    """Two active pages cannot share a slug (on create or rename)."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/pages"

    client.post(base, headers=h, json={"slug": "sobre", "title": "A"})
    dup = client.post(base, headers=h, json={"slug": "sobre", "title": "B"})
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "duplicate_slug"

    other = client.post(base, headers=h, json={"slug": "termos", "title": "C"})
    rename = client.patch(
        f"{base}/{other.json()['id']}", headers=h, json={"slug": "sobre"}
    )
    assert rename.status_code == 409


def test_page_update_delete_not_found_is_404(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    missing = "00000000-0000-0000-0000-000000000000"
    assert (
        client.patch(
            f"{BASE}/{a.id}/layout/pages/{missing}", headers=h, json={"title": "x"}
        ).status_code
        == 404
    )
    assert (
        client.delete(f"{BASE}/{a.id}/layout/pages/{missing}", headers=h).status_code
        == 404
    )


def test_pages_viewer_cannot_write(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    viewer = create_user(db)
    create_member(db, store=a, user=viewer, role_key="catalog")
    vh = member_headers(client, db, viewer)
    base = f"{BASE}/{a.id}/layout/pages"
    assert client.get(base, headers=vh).status_code == 200
    assert (
        client.post(base, headers=vh, json={"slug": "s", "title": "t"}).status_code
        == 403
    )


# --- Banners ---------------------------------------------------------------


def test_banners_crud(client: TestClient, two_stores: TenantContext) -> None:
    """Banners are created, listed by position, updated and deleted."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/banners"

    client.post(
        base, headers=h, json={"image_url": "https://cdn/b2.png", "position": 2}
    )
    first = client.post(
        base, headers=h, json={"image_url": "https://cdn/b1.png", "position": 1}
    )
    listed = client.get(base, headers=h).json()
    assert [b["position"] for b in listed] == [1, 2]

    updated = client.patch(
        f"{base}/{first.json()['id']}", headers=h, json={"is_active": False}
    )
    assert updated.json()["is_active"] is False
    assert client.delete(f"{base}/{first.json()['id']}", headers=h).status_code == 204
    assert [b["image_url"] for b in client.get(base, headers=h).json()] == [
        "https://cdn/b2.png"
    ]


# --- Menus & items ---------------------------------------------------------


def test_menus_crud_with_items(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    """Menus carry ordered items; deleting a menu soft-deletes its items."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/menus"

    menu = client.post(base, headers=h, json={"name": "Rodapé", "location": "footer"})
    assert menu.status_code == 200
    menu_id = menu.json()["id"]
    assert menu.json()["items"] == []

    client.post(
        f"{base}/{menu_id}/items",
        headers=h,
        json={"label": "Sobre", "url": "/pages/sobre", "position": 0},
    )
    item_b = client.post(
        f"{base}/{menu_id}/items",
        headers=h,
        json={"label": "Termos", "url": "/pages/termos", "position": 1},
    )
    listed = client.get(base, headers=h).json()
    assert [i["label"] for i in listed[0]["items"]] == ["Sobre", "Termos"]

    assert (
        client.delete(
            f"{BASE}/{a.id}/layout/menu-items/{item_b.json()['id']}", headers=h
        ).status_code
        == 204
    )
    assert len(client.get(base, headers=h).json()[0]["items"]) == 1

    # Deleting the menu cascades to (soft-deletes) its remaining items.
    assert client.delete(f"{base}/{menu_id}", headers=h).status_code == 204
    assert client.get(base, headers=h).json() == []
    active_items = db.exec(
        select(ContentMenuItem).where(
            ContentMenuItem.menu_id == menu_id,
            col(ContentMenuItem.deleted_at).is_(None),
        )
    ).all()
    assert active_items == []


def test_add_item_to_missing_menu_is_404(
    client: TestClient, two_stores: TenantContext
) -> None:
    """An item cannot be added to a non-existent menu (no orphan items)."""
    a = two_stores.store_a
    missing = "00000000-0000-0000-0000-000000000000"
    resp = client.post(
        f"{BASE}/{a.id}/layout/menus/{missing}/items",
        headers=two_stores.owner_a_headers,
        json={"label": "x", "url": "/"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "menu_not_found"


def test_menu_and_item_update(client: TestClient, two_stores: TenantContext) -> None:
    """A menu can be renamed/relocated and its items edited."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/layout/menus"

    menu_id = client.post(base, headers=h, json={"name": "Topo"}).json()["id"]
    renamed = client.patch(
        f"{base}/{menu_id}", headers=h, json={"name": "Rodapé", "location": "footer"}
    )
    assert renamed.json()["name"] == "Rodapé"
    assert renamed.json()["location"] == "footer"

    item_id = client.post(
        f"{base}/{menu_id}/items", headers=h, json={"label": "A", "url": "/a"}
    ).json()["id"]
    edited = client.patch(
        f"{BASE}/{a.id}/layout/menu-items/{item_id}", headers=h, json={"label": "B"}
    )
    assert edited.json()["label"] == "B"


def test_content_not_found_is_404(
    client: TestClient, two_stores: TenantContext
) -> None:
    """Updating/deleting a missing banner, menu or item all 404."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    missing = "00000000-0000-0000-0000-000000000000"
    layout = f"{BASE}/{a.id}/layout"
    assert (
        client.patch(
            f"{layout}/banners/{missing}", headers=h, json={"title": "x"}
        ).status_code
        == 404
    )
    assert client.delete(f"{layout}/banners/{missing}", headers=h).status_code == 404
    assert (
        client.patch(
            f"{layout}/menus/{missing}", headers=h, json={"name": "x"}
        ).status_code
        == 404
    )
    assert client.delete(f"{layout}/menus/{missing}", headers=h).status_code == 404
    assert (
        client.patch(
            f"{layout}/menu-items/{missing}", headers=h, json={"label": "x"}
        ).status_code
        == 404
    )
    assert client.delete(f"{layout}/menu-items/{missing}", headers=h).status_code == 404
