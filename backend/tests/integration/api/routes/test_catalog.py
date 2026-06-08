"""Integration tests for the catalog routes (panel API)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.media.models import MediaFile
from tests.utils.store import TenantContext, create_member, create_user, member_headers

BASE = "/api/v1/stores"


def _create_product(
    client: TestClient,
    store_id: uuid.UUID,
    headers: dict[str, str],
    *,
    name: str = "Mug",
    slug: str = "mug",
) -> dict[str, object]:
    body = {"name": name, "slug": slug, "price_amount_minor": 1500}
    resp = client.post(f"{BASE}/{store_id}/products", headers=headers, json=body)
    data: dict[str, object] = resp.json()
    data["_status"] = resp.status_code
    return data


def test_create_get_list_product(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    created = _create_product(client, a.id, h)
    assert created["_status"] == 201
    assert created["status"] == "draft"
    assert created["price_currency"] == "USD"  # inherited from the store

    got = client.get(f"{BASE}/{a.id}/products/{created['id']}", headers=h)
    assert got.status_code == 200

    listed = client.get(f"{BASE}/{a.id}/products", headers=h)
    assert listed.status_code == 200
    assert listed.json()["count"] == 1


def test_update_product(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)["id"]
    upd = client.patch(
        f"{BASE}/{a.id}/products/{pid}",
        headers=h,
        json={"name": "New", "price_amount_minor": 2000, "slug": "new-slug"},
    )
    assert upd.status_code == 200
    body = upd.json()
    assert body["name"] == "New"
    assert body["slug"] == "new-slug"
    assert body["price_amount_minor"] == 2000


def test_publish_unpublish_archive(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)["id"]

    assert (
        client.post(f"{BASE}/{a.id}/products/{pid}/publish", headers=h).json()["status"]
        == "published"
    )
    assert (
        client.post(f"{BASE}/{a.id}/products/{pid}/unpublish", headers=h).json()[
            "status"
        ]
        == "draft"
    )
    assert (
        client.post(f"{BASE}/{a.id}/products/{pid}/archive", headers=h).status_code
        == 200
    )
    # archived = soft-deleted → no longer reachable
    assert client.get(f"{BASE}/{a.id}/products/{pid}", headers=h).status_code == 404


def test_slug_auto_disambiguates_and_follows_draft_name(
    client: TestClient, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    url = f"{BASE}/{a.id}/products"

    # same name, no explicit slug → auto-suffix (camiseta, camiseta-2, …)
    p1 = client.post(
        url, headers=h, json={"name": "Camiseta", "price_amount_minor": 1000}
    ).json()
    p2 = client.post(
        url, headers=h, json={"name": "Camiseta", "price_amount_minor": 1000}
    ).json()
    assert p1["slug"] == "camiseta"
    assert p2["slug"] == "camiseta-2"

    # draft: renaming makes the slug follow the name
    upd = client.patch(f"{url}/{p1['id']}", headers=h, json={"name": "Camiseta Azul"})
    assert upd.json()["slug"] == "camiseta-azul"

    # published: the slug freezes (stable public URL)
    client.post(f"{url}/{p1['id']}/publish", headers=h)
    upd2 = client.patch(f"{url}/{p1['id']}", headers=h, json={"name": "Camiseta Verde"})
    assert upd2.json()["slug"] == "camiseta-azul"


def test_slug_unique_per_store_but_free_across_stores(
    client: TestClient, two_stores: TenantContext
) -> None:
    a, b = two_stores.store_a, two_stores.store_b
    assert _create_product(client, a.id, two_stores.owner_a_headers)["_status"] == 201
    # same slug, same store → conflict
    dup = _create_product(client, a.id, two_stores.owner_a_headers, name="Mug 2")
    assert dup["_status"] == 409
    # same slug, different store → allowed
    assert _create_product(client, b.id, two_stores.owner_b_headers)["_status"] == 201


def test_isolation_store_b_cannot_see_a(
    client: TestClient, two_stores: TenantContext
) -> None:
    a, b = two_stores.store_a, two_stores.store_b
    pid = _create_product(client, a.id, two_stores.owner_a_headers)["id"]
    # store B's owner asking under store B never finds A's product
    assert (
        client.get(
            f"{BASE}/{b.id}/products/{pid}", headers=two_stores.owner_b_headers
        ).status_code
        == 404
    )


def test_gating_support_cannot_create(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    support = create_user(db)
    create_member(db, store=two_stores.store_a, user=support, role_key="support")
    headers = member_headers(client, db, support)
    resp = client.post(
        f"{BASE}/{two_stores.store_a.id}/products",
        headers=headers,
        json={"name": "X", "slug": "x", "price_amount_minor": 100},
    )
    assert resp.status_code == 403


def test_inventory_set_upserts(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)["id"]
    inv_url = f"{BASE}/{a.id}/products/{pid}/inventory"
    # no stock set yet → GET returns null
    assert client.get(inv_url, headers=h).json() is None
    r1 = client.put(inv_url, headers=h, json={"quantity": 10})
    assert r1.status_code == 200 and r1.json()["quantity"] == 10
    r2 = client.put(inv_url, headers=h, json={"quantity": 4})
    assert r2.json()["quantity"] == 4  # same row updated
    # GET now reflects the stored quantity (so the edit form can pre-fill it)
    assert client.get(inv_url, headers=h).json()["quantity"] == 4


def test_category_crud(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    created = client.post(f"{BASE}/{a.id}/categories", headers=h, json={"name": "Mugs"})
    assert created.status_code == 201
    cid = created.json()["id"]
    assert created.json()["slug"] == "mugs"  # derived from the name

    upd = client.patch(
        f"{BASE}/{a.id}/categories/{cid}", headers=h, json={"name": "Cups"}
    )
    assert upd.status_code == 200 and upd.json()["name"] == "Cups"
    assert client.get(f"{BASE}/{a.id}/categories", headers=h).json()["count"] == 1
    assert (
        client.post(f"{BASE}/{a.id}/categories/{cid}/archive", headers=h).status_code
        == 204
    )
    assert client.get(f"{BASE}/{a.id}/categories", headers=h).json()["count"] == 0


def test_variant_crud(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)["id"]
    created = client.post(
        f"{BASE}/{a.id}/products/{pid}/variants",
        headers=h,
        json={"name": "Size M", "attributes": {"size": "M"}},
    )
    assert created.status_code == 201
    vid = created.json()["id"]
    assert created.json()["status"] == "active"
    upd = client.patch(
        f"{BASE}/{a.id}/products/{pid}/variants/{vid}", headers=h, json={"sku": "M-1"}
    )
    assert upd.json()["sku"] == "M-1"
    assert (
        client.get(f"{BASE}/{a.id}/products/{pid}/variants", headers=h).json()["count"]
        == 1
    )
    assert (
        client.post(
            f"{BASE}/{a.id}/products/{pid}/variants/{vid}/archive", headers=h
        ).status_code
        == 204
    )


def test_images_attach_list_remove_and_isolation(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, b = two_stores.store_a, two_stores.store_b
    h = two_stores.owner_a_headers
    pid = _create_product(client, a.id, h)["id"]

    media_a = MediaFile(
        store_id=a.id,
        owner_type="product",
        key=f"public/{a.id}/media/{uuid.uuid4()}.png",
        url="https://cdn.test/x.png",
        content_type="image/png",
        size=10,
    )
    media_b = MediaFile(
        store_id=b.id,
        owner_type="product",
        key=f"public/{b.id}/media/{uuid.uuid4()}.png",
        url="https://cdn.test/y.png",
        content_type="image/png",
        size=10,
    )
    db.add(media_a)
    db.add(media_b)
    db.commit()
    db.refresh(media_a)
    db.refresh(media_b)

    # attach store A's media → ok
    attached = client.post(
        f"{BASE}/{a.id}/products/{pid}/images",
        headers=h,
        json={"media_file_id": str(media_a.id), "position": 0},
    )
    assert attached.status_code == 201
    iid = attached.json()["id"]
    # enriched with the media's url + status (no separate media GET needed)
    assert attached.json()["status"] == "processing"
    assert attached.json()["url"] == "https://cdn.test/x.png"
    listed = client.get(f"{BASE}/{a.id}/products/{pid}/images", headers=h).json()
    assert listed[0]["id"] == iid
    assert listed[0]["url"] == "https://cdn.test/x.png"

    # attaching another store's media → 404 (isolation)
    cross = client.post(
        f"{BASE}/{a.id}/products/{pid}/images",
        headers=h,
        json={"media_file_id": str(media_b.id)},
    )
    assert cross.status_code == 404

    assert (
        client.delete(
            f"{BASE}/{a.id}/products/{pid}/images/{iid}", headers=h
        ).status_code
        == 204
    )
    assert client.get(f"{BASE}/{a.id}/products/{pid}/images", headers=h).json() == []
