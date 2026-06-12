"""Integration tests for the orders panel routes (P6-ORD-02)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.modules.cart.enums import CartStatus
from app.modules.cart.models import CartCart, CartItem
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import InventoryItem, Product
from app.modules.customers.schemas import AddressInput
from app.modules.customers.services import create_or_update_customer
from app.modules.orders.models import Order
from app.modules.orders.services import create_order
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.stores.models import Store
from tests.utils.store import (
    TenantContext,
    create_member,
    create_user,
    member_headers,
)


def _make_order(
    db: Session, store: Store, *, stock: int = 10, qty: int = 2, price: int = 1500
) -> tuple[Order, Product]:
    """Create a `pending_payment` order in the store (product + cart + checkout)."""
    suffix = uuid.uuid4().hex[:8]
    product = Product(
        store_id=store.id,
        name="Caneca",
        slug=f"caneca-{suffix}",
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=price,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=stock))
    db.flush()
    cart = CartCart(
        store_id=store.id,
        guest_session_id=f"g-{suffix}",
        status=CartStatus.active,
    )
    db.add(cart)
    db.flush()
    db.add(
        CartItem(
            store_id=store.id,
            cart_id=cart.id,
            product_id=product.id,
            quantity=qty,
            unit_price_amount_minor=price,
            unit_price_currency="BRL",
        )
    )
    db.flush()
    method = ShippingMethod(
        store_id=store.id,
        type=ShippingMethodType.fixed_shipping,
        name="Frete",
        price_amount_minor=900,
    )
    db.add(method)
    db.flush()
    customer = create_or_update_customer(
        session=db, store_id=store.id, name="Ana", email=f"ana-{suffix}@x.com"
    )
    order = create_order(
        session=db,
        cart=cart,
        customer=customer,
        address=AddressInput(line1="Rua A", city="SP", country="BR"),
        shipping_method=method,
    )
    return order, product


def _base(store: Store) -> str:
    return f"/api/v1/stores/{store.id}/orders"


def test_list_and_detail(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    order, _ = _make_order(db, store)
    _make_order(db, store)

    listing = client.get(_base(store), headers=h)
    assert listing.status_code == 200
    body = listing.json()
    assert body["count"] == 2
    row = next(r for r in body["data"] if r["id"] == str(order.id))
    assert row["order_number"] == order.order_number
    assert row["customer_name"] == "Ana"
    assert row["item_count"] == 2

    detail = client.get(f"{_base(store)}/{order.id}", headers=h)
    assert detail.status_code == 200
    d = detail.json()
    assert len(d["items"]) == 1
    assert d["address"]["city"] == "SP"
    assert d["customer"]["name"] == "Ana"
    assert [h["status"] for h in d["status_history"]] == ["pending_payment"]
    assert d["notes"] == []


def test_list_status_filter(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    _make_order(db, store)
    assert (
        client.get(f"{_base(store)}?status=pending_payment", headers=h).json()["count"]
        == 1
    )
    assert client.get(f"{_base(store)}?status=paid", headers=h).json()["count"] == 0


def test_mark_paid(client: TestClient, db: Session, two_stores: TenantContext) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    order, _ = _make_order(db, store)
    resp = client.patch(
        f"{_base(store)}/{order.id}/status", headers=h, json={"status": "paid"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "paid"
    assert [h["status"] for h in body["status_history"]] == [
        "pending_payment",
        "paid",
    ]


def test_invalid_transition_is_409(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    order, _ = _make_order(db, store)
    resp = client.patch(
        f"{_base(store)}/{order.id}/status", headers=h, json={"status": "shipped"}
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "invalid_transition"


def test_cancel_restocks(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    order, product = _make_order(db, store, stock=10, qty=2)
    inv = db.exec(
        select(InventoryItem).where(InventoryItem.product_id == product.id)
    ).one()
    assert inv.quantity == 8  # decremented at creation

    resp = client.post(f"{_base(store)}/{order.id}/cancel", headers=h)
    assert resp.status_code == 200
    assert resp.json()["status"] == "canceled"
    db.refresh(inv)
    assert inv.quantity == 10  # restocked


def test_add_note(client: TestClient, db: Session, two_stores: TenantContext) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    order, _ = _make_order(db, store)
    created = client.post(
        f"{_base(store)}/{order.id}/notes", headers=h, json={"body": "ligar p/ cliente"}
    )
    assert created.status_code == 201
    assert created.json()["body"] == "ligar p/ cliente"

    detail = client.get(f"{_base(store)}/{order.id}", headers=h)
    assert [n["body"] for n in detail.json()["notes"]] == ["ligar p/ cliente"]


def test_view_gated(client: TestClient, db: Session, two_stores: TenantContext) -> None:
    store = two_stores.store_a
    _make_order(db, store)
    no_orders = create_user(db)
    create_member(db, store=store, user=no_orders, role_key="catalog")  # no orders.*
    headers = member_headers(client, db, no_orders)
    assert client.get(_base(store), headers=headers).status_code == 403


def test_cancel_requires_permission(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store = two_stores.store_a
    order, _ = _make_order(db, store)
    viewer = create_user(db)
    create_member(db, store=store, user=viewer, role_key="support")  # no orders.cancel
    headers = member_headers(client, db, viewer)
    assert client.get(_base(store), headers=headers).status_code == 200  # can view
    assert (
        client.post(f"{_base(store)}/{order.id}/cancel", headers=headers).status_code
        == 403
    )


def test_isolated_between_stores(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    order_b, _ = _make_order(db, two_stores.store_b)
    # Store A's owner cannot reach store B's order.
    resp = client.get(
        f"{_base(two_stores.store_a)}/{order_b.id}",
        headers=two_stores.owner_a_headers,
    )
    assert resp.status_code == 404
