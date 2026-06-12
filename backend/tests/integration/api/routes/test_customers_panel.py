"""Integration tests for the customers panel routes (P6-CUST-02)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.cart.enums import CartStatus
from app.modules.cart.models import CartCart, CartItem
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import InventoryItem, Product
from app.modules.customers.models import CustomerProfile
from app.modules.customers.schemas import AddressInput
from app.modules.customers.services import create_or_update_customer
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


def _customer(
    db: Session,
    store: Store,
    *,
    name: str = "Ana",
    email: str | None = "ana@x.com",
    phone: str | None = "(86) 99999-0000",
    with_address: bool = True,
) -> CustomerProfile:
    address = (
        AddressInput(line1="Rua A", city="SP", country="BR") if with_address else None
    )
    return create_or_update_customer(
        session=db,
        store_id=store.id,
        name=name,
        email=email,
        phone=phone,
        region="BR" if phone else None,
        address=address,
    )


def _order_for(db: Session, store: Store, customer: CustomerProfile) -> None:
    suffix = uuid.uuid4().hex[:8]
    product = Product(
        store_id=store.id,
        name="Caneca",
        slug=f"caneca-{suffix}",
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=1500,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=10))
    db.flush()
    cart = CartCart(
        store_id=store.id, guest_session_id=f"g-{suffix}", status=CartStatus.active
    )
    db.add(cart)
    db.flush()
    db.add(
        CartItem(
            store_id=store.id,
            cart_id=cart.id,
            product_id=product.id,
            quantity=1,
            unit_price_amount_minor=1500,
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
    create_order(
        session=db,
        cart=cart,
        customer=customer,
        address=AddressInput(line1="Rua A", city="SP", country="BR"),
        shipping_method=method,
    )


def _base(store: Store) -> str:
    return f"/api/v1/stores/{store.id}/customers"


def test_list_and_search(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    _customer(db, store, name="Ana", email="ana@x.com", phone="(86) 99999-0000")
    _customer(db, store, name="Bob", email="bob@y.com", phone="(11) 98888-0000")

    assert client.get(_base(store), headers=h).json()["count"] == 2
    by_name = client.get(f"{_base(store)}?search=ana", headers=h).json()
    assert by_name["count"] == 1
    assert by_name["data"][0]["name"] == "Ana"
    assert client.get(f"{_base(store)}?search=bob@y", headers=h).json()["count"] == 1
    # Phone digits are stored as E.164; a digit substring still matches.
    assert client.get(f"{_base(store)}?search=98888", headers=h).json()["count"] == 1


def test_detail_with_history(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    customer = _customer(db, store)
    _order_for(db, store, customer)

    resp = client.get(f"{_base(store)}/{customer.id}", headers=h)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Ana"
    assert body["phone_e164"] == "+5586999990000"
    assert len(body["addresses"]) == 1
    assert body["addresses"][0]["city"] == "SP"
    assert len(body["orders"]) == 1
    assert body["orders"][0]["order_number"] == 1


def test_detail_without_orders(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    customer = _customer(db, store, with_address=False)
    body = client.get(f"{_base(store)}/{customer.id}", headers=h).json()
    assert body["orders"] == []
    assert body["addresses"] == []


def test_view_gated(client: TestClient, db: Session, two_stores: TenantContext) -> None:
    store = two_stores.store_a
    _customer(db, store)
    no_view = create_user(db)
    create_member(db, store=store, user=no_view, role_key="catalog")  # no customers.*
    headers = member_headers(client, db, no_view)
    assert client.get(_base(store), headers=headers).status_code == 403


def test_isolated_between_stores(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    customer_b = _customer(db, two_stores.store_b)
    resp = client.get(
        f"{_base(two_stores.store_a)}/{customer_b.id}",
        headers=two_stores.owner_a_headers,
    )
    assert resp.status_code == 404
