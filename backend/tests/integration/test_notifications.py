"""Integration tests for order notification emails + health (P6-NOTIF-01).

The emails must be **enqueued** to the worker (never sent inline, INV-F5) and a
queue failure must not break the order. Tests patch ``enqueue`` to observe the
dispatch without touching Redis.
"""

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlmodel import Session, select

from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import InventoryItem, Product
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.orders.models import Order
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store, StoreSettings
from tests.utils.store import TenantContext

SF = "/api/v1/storefront"


def _store(
    db: Session, slug: str, *, contact_email: str | None = "shop@x.com"
) -> tuple[str, str, str]:
    """Create an active store (host + 1 product + 1 method); return ids."""
    store = Store(
        name="L", slug=slug, currency="BRL", locale="pt-BR", status=StoreStatus.active
    )
    db.add(store)
    db.flush()
    db.add(StoreSettings(store_id=store.id, contact_email=contact_email))
    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
    db.flush()
    product = Product(
        store_id=store.id,
        name="Caneca",
        slug=f"caneca-{slug}",
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=1500,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=10))
    method = ShippingMethod(
        store_id=store.id,
        type=ShippingMethodType.fixed_shipping,
        name="Frete",
        price_amount_minor=900,
    )
    db.add(method)
    db.flush()
    return host, str(product.id), str(method.id)


def _checkout(
    client: TestClient,
    host: str,
    product_id: str,
    method_id: str,
    *,
    email: str | None = "ana@x.com",
) -> Response:
    client.post(
        f"{SF}/cart/items",
        headers={"host": host},
        json={"product_id": product_id, "quantity": 1},
    )
    response: Response = client.post(
        f"{SF}/checkout", headers={"host": host}, json=_body(method_id, email=email)
    )
    return response


def _body(method_id: str, *, email: str | None = "ana@x.com") -> dict[str, object]:
    contact: dict[str, object] = {"name": "Ana"}
    if email:
        contact["email"] = email
    else:
        contact["phone"] = "(86) 99999-0000"
        contact["region"] = "BR"
    return {
        "contact": contact,
        "address": {"line1": "Rua A", "city": "SP", "country": "BR"},
        "shipping_method_id": method_id,
    }


def test_checkout_enqueues_customer_and_merchant_emails(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    enqueue = AsyncMock()
    monkeypatch.setattr("app.modules.notifications.services.enqueue", enqueue)
    host, product_id, method_id = _store(db, "notif-both")
    resp = _checkout(client, host, product_id, method_id)
    assert resp.status_code == 200
    # Both emails were enqueued to the worker (never sent inline).
    assert enqueue.await_count == 2
    assert all(c.args[0] == "send_order_email" for c in enqueue.await_args_list)
    recipients = {c.kwargs["email_to"] for c in enqueue.await_args_list}
    assert recipients == {"ana@x.com", "shop@x.com"}


def test_checkout_without_customer_email_enqueues_only_merchant(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    enqueue = AsyncMock()
    monkeypatch.setattr("app.modules.notifications.services.enqueue", enqueue)
    host, product_id, method_id = _store(db, "notif-merchant")
    resp = _checkout(client, host, product_id, method_id, email=None)
    assert resp.status_code == 200
    assert enqueue.await_count == 1
    assert enqueue.await_args_list[0].kwargs["email_to"] == "shop@x.com"


def test_enqueue_failure_does_not_break_the_order(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    enqueue = AsyncMock(side_effect=RuntimeError("redis down"))
    monkeypatch.setattr("app.modules.notifications.services.enqueue", enqueue)
    host, product_id, method_id = _store(db, "notif-fail")
    resp = _checkout(client, host, product_id, method_id)
    # The email dispatch is best-effort: the order is still placed.
    assert resp.status_code == 200
    order = db.exec(select(Order)).first()
    assert order is not None


def test_health_db(client: TestClient) -> None:
    assert client.get("/health/db").status_code == 200


def test_milestone_full_flow(
    client: TestClient,
    db: Session,
    two_stores: TenantContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Fase 6 milestone end-to-end (integration): store with an owner →
    product → storefront cart → checkout → order (emails enqueued) → panel lists
    it → mark paid. The merchant email resolves to the owner here (no
    ``contact_email`` set)."""
    enqueue = AsyncMock()
    monkeypatch.setattr("app.modules.notifications.services.enqueue", enqueue)
    store, h = two_stores.store_a, two_stores.owner_a_headers

    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
    product = Product(
        store_id=store.id,
        name="Caneca",
        slug="caneca-milestone",
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=1500,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=10))
    method = ShippingMethod(
        store_id=store.id,
        type=ShippingMethodType.fixed_shipping,
        name="Frete",
        price_amount_minor=900,
    )
    db.add(method)
    db.flush()

    # Storefront: add to cart → checkout (no login).
    checkout = _checkout(client, host, str(product.id), str(method.id))
    assert checkout.status_code == 200
    order_id = checkout.json()["id"]
    # Emails enqueued (customer + merchant-via-owner), never inline.
    assert enqueue.await_count == 2

    # Panel: the merchant sees the order and marks it paid.
    listing = client.get(f"/api/v1/stores/{store.id}/orders", headers=h)
    assert listing.status_code == 200
    assert any(row["id"] == order_id for row in listing.json()["data"])
    paid = client.patch(
        f"/api/v1/stores/{store.id}/orders/{order_id}/status",
        headers=h,
        json={"status": "paid"},
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"
