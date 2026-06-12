"""Integration tests for the checkout flow + store policies (P6-CHK-01)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import InventoryItem, Product
from app.modules.customers.models import CustomerProfile
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.orders.enums import OrderStatus
from app.modules.orders.models import Order, OrderAddress
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store, StoreSettings
from tests.utils.store import (
    TenantContext,
    create_member,
    create_user,
    member_headers,
)

SF = "/api/v1/storefront"
STORES = "/api/v1/stores"


def _store(db: Session, slug: str) -> tuple[Store, str]:
    store = Store(
        name="L", slug=slug, currency="BRL", locale="pt-BR", status=StoreStatus.active
    )
    db.add(store)
    db.flush()
    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
    db.flush()
    return store, host


def _product(
    db: Session, store: Store, *, stock: int = 10, price: int = 1500
) -> Product:
    product = Product(
        store_id=store.id,
        name="Caneca",
        slug="caneca",
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=price,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=stock))
    db.flush()
    return product


def _method(
    db: Session,
    store: Store,
    mtype: ShippingMethodType = ShippingMethodType.local_pickup,
    price: int | None = None,
    active: bool = True,
) -> ShippingMethod:
    method = ShippingMethod(
        store_id=store.id,
        type=mtype,
        name=mtype.value,
        price_amount_minor=price,
        is_active=active,
    )
    db.add(method)
    db.flush()
    return method


def _body(method_id: uuid.UUID) -> dict[str, object]:
    return {
        "contact": {
            "name": "Ana",
            "email": "ana@x.com",
            "phone": "(86) 99999-0000",
            "region": "BR",
        },
        "address": {
            "line1": "Rua A",
            "number": "123",
            "line2": "Apto 4",
            "neighborhood": "Centro",
            "city": "SP",
            "state": "SP",
            "postal_code": "01000-000",
            "country": "BR",
        },
        "shipping_method_id": str(method_id),
    }


def test_checkout_creates_pending_order(client: TestClient, db: Session) -> None:
    store, host = _store(db, "chk-create")
    product = _product(db, store, stock=10, price=1500)
    method = _method(db, store, ShippingMethodType.fixed_shipping, price=900)
    h = {"host": host}

    client.post(
        f"{SF}/cart/items",
        headers=h,
        json={"product_id": str(product.id), "quantity": 2},
    )
    resp = client.post(f"{SF}/checkout", headers=h, json=_body(method.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pending_payment"
    assert body["order_number"] == 1
    assert body["subtotal_amount_minor"] == 3000
    assert body["shipping_amount_minor"] == 900
    assert body["total_amount_minor"] == 3900
    assert body["items"][0]["name"] == "Caneca"

    customer = db.exec(
        select(CustomerProfile).where(CustomerProfile.store_id == store.id)
    ).one()
    assert customer.email == "ana@x.com"
    assert customer.phone_e164 == "+5586999990000"  # dedup normalization

    inv = db.exec(
        select(InventoryItem).where(InventoryItem.product_id == product.id)
    ).one()
    assert inv.quantity == 8  # decremented

    order = db.exec(select(Order).where(Order.store_id == store.id)).one()
    assert order.status == OrderStatus.pending_payment  # not paid automatically

    addr = db.exec(select(OrderAddress).where(OrderAddress.order_id == order.id)).one()
    assert (addr.number, addr.neighborhood, addr.postal_code, addr.state) == (
        "123",
        "Centro",
        "01000-000",
        "SP",
    )


def test_empty_cart_checkout_is_422(client: TestClient, db: Session) -> None:
    store, host = _store(db, "chk-empty")
    method = _method(db, store)
    resp = client.post(f"{SF}/checkout", headers={"host": host}, json=_body(method.id))
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "empty_cart"


def test_unavailable_method_is_404(client: TestClient, db: Session) -> None:
    store, host = _store(db, "chk-method")
    product = _product(db, store)
    inactive = _method(db, store, active=False)
    h = {"host": host}
    client.post(
        f"{SF}/cart/items",
        headers=h,
        json={"product_id": str(product.id), "quantity": 1},
    )
    resp = client.post(f"{SF}/checkout", headers=h, json=_body(inactive.id))
    assert resp.status_code == 404


def test_checkout_isolated_between_stores(client: TestClient, db: Session) -> None:
    store_a, host_a = _store(db, "chk-iso-a")
    _, host_b = _store(db, "chk-iso-b")
    product_a = _product(db, store_a)
    method_b = _method(db, _store(db, "chk-iso-b2")[0])
    client.post(
        f"{SF}/cart/items",
        headers={"host": host_a},
        json={"product_id": str(product_a.id), "quantity": 1},
    )
    # Store B's cart is its own (empty) → checkout 422.
    resp = client.post(
        f"{SF}/checkout", headers={"host": host_b}, json=_body(method_b.id)
    )
    assert resp.status_code == 422


# --- store policies (panel + storefront) ---


def test_policies_panel_crud(client: TestClient, two_stores: TenantContext) -> None:
    a = two_stores.store_a
    h = two_stores.owner_a_headers
    base = f"{STORES}/{a.id}/checkout/policies"
    upd = client.patch(
        base, headers=h, json={"return_policy": "30 dias", "privacy_policy": "LGPD"}
    )
    assert upd.status_code == 200
    assert upd.json()["return_policy"] == "30 dias"
    got = client.get(base, headers=h)
    assert got.json()["privacy_policy"] == "LGPD"


def test_policies_viewer_cannot_update(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    viewer = create_user(db)
    create_member(db, store=a, user=viewer, role_key="support")  # checkout.view only
    vh = member_headers(client, db, viewer)
    base = f"{STORES}/{a.id}/checkout/policies"
    assert client.get(base, headers=vh).status_code == 200
    assert (
        client.patch(base, headers=vh, json={"return_policy": "x"}).status_code == 403
    )


def test_policies_exposed_in_storefront(client: TestClient, db: Session) -> None:
    store, host = _store(db, "chk-policies-sf")
    db.add(StoreSettings(store_id=store.id, return_policy="Troca em 7 dias"))
    db.flush()
    resp = client.get(f"{SF}/home", headers={"host": host})
    assert resp.status_code == 200
    assert resp.json()["store"]["return_policy"] == "Troca em 7 dias"
