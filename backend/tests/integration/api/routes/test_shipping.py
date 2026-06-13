"""Integration tests for the shipping panel routes + public read (P6-SHIP-01)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store
from tests.utils.store import (
    TenantContext,
    create_member,
    create_user,
    member_headers,
)

BASE = "/api/v1/stores"
SF = "/api/v1/storefront"


def test_crud_and_validation(client: TestClient, two_stores: TenantContext) -> None:
    """Owner creates/lists/updates/deletes methods; a fixed method needs a price."""
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{BASE}/{a.id}/shipping/methods"

    pickup = client.post(
        base, headers=h, json={"type": "local_pickup", "name": "Retirada"}
    )
    assert pickup.status_code == 200
    fixed = client.post(
        base,
        headers=h,
        json={"type": "fixed_shipping", "name": "Fixo", "price_amount_minor": 1500},
    )
    assert fixed.status_code == 200
    assert fixed.json()["price_amount_minor"] == 1500

    bad = client.post(base, headers=h, json={"type": "fixed_shipping", "name": "X"})
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "invalid_shipping_method"

    assert {m["type"] for m in client.get(base, headers=h).json()} == {
        "local_pickup",
        "fixed_shipping",
    }

    upd = client.patch(
        f"{base}/{pickup.json()['id']}", headers=h, json={"is_active": False}
    )
    assert upd.json()["is_active"] is False

    assert client.delete(f"{base}/{fixed.json()['id']}", headers=h).status_code == 204
    assert {m["type"] for m in client.get(base, headers=h).json()} == {"local_pickup"}


def test_update_missing_is_404(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    missing = "00000000-0000-0000-0000-000000000000"
    resp = client.patch(
        f"{BASE}/{a.id}/shipping/methods/{missing}",
        headers=two_stores.owner_a_headers,
        json={"name": "x"},
    )
    assert resp.status_code == 404


def test_view_role_cannot_write(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    viewer = create_user(db)
    create_member(db, store=a, user=viewer, role_key="support")  # shipping.view only
    vh = member_headers(client, db, viewer)
    base = f"{BASE}/{a.id}/shipping/methods"
    assert client.get(base, headers=vh).status_code == 200
    blocked = client.post(base, headers=vh, json={"type": "local_pickup", "name": "X"})
    assert blocked.status_code == 403


def _published(db: Session, slug: str) -> tuple[Store, str]:
    store = Store(
        name="L", slug=slug, currency="BRL", locale="pt-BR", status=StoreStatus.active
    )
    db.add(store)
    db.flush()
    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
    db.flush()
    return store, host


def test_public_lists_active_only(client: TestClient, db: Session) -> None:
    store, host = _published(db, "ship-public")
    db.add(
        ShippingMethod(
            store_id=store.id,
            type=ShippingMethodType.local_pickup,
            name="Retirada",
            is_active=True,
        )
    )
    db.add(
        ShippingMethod(
            store_id=store.id,
            type=ShippingMethodType.fixed_shipping,
            name="Fixo",
            price_amount_minor=1500,
            is_active=False,
        )
    )
    db.flush()
    resp = client.get(f"{SF}/shipping-methods", headers={"host": host})
    assert resp.status_code == 200
    assert {m["type"] for m in resp.json()} == {"local_pickup"}


def test_public_isolated_between_stores(client: TestClient, db: Session) -> None:
    a, host_a = _published(db, "ship-iso-a")
    b, _ = _published(db, "ship-iso-b")
    db.add(
        ShippingMethod(
            store_id=a.id,
            type=ShippingMethodType.local_pickup,
            name="A",
            is_active=True,
        )
    )
    db.add(
        ShippingMethod(
            store_id=b.id,
            type=ShippingMethodType.local_pickup,
            name="B",
            is_active=True,
        )
    )
    db.flush()
    resp = client.get(f"{SF}/shipping-methods", headers={"host": host_a})
    assert {m["name"] for m in resp.json()} == {"A"}
