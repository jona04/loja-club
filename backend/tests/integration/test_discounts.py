"""Integration tests for coupons: CRUD, validation, cart + checkout (P6-DISC-01)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.api import AppError
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import InventoryItem, Product
from app.modules.discounts import services as discounts
from app.modules.discounts.enums import CouponType
from app.modules.discounts.models import DiscountCouponRedemption
from app.modules.discounts.schemas import CouponCreate
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.orders.models import Order
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

SF = "/api/v1/storefront"


def _coupons_base(store: Store) -> str:
    return f"/api/v1/stores/{store.id}/discounts/coupons"


def _make_coupon(
    db: Session,
    store_id: uuid.UUID,
    *,
    code: str = "SAVE10",
    coupon_type: CouponType = CouponType.percentage,
    value: int = 10,
    **kwargs: object,
) -> uuid.UUID:
    coupon = discounts.create_coupon(
        session=db,
        store_id=store_id,
        data=CouponCreate(code=code, type=coupon_type, value=value, **kwargs),
    )
    return coupon.id


def _sf_store(db: Session, slug: str) -> tuple[Store, str, str, str]:
    """Create an active store (host + product + method); return (store, host, pid, mid)."""
    store = Store(
        name="L", slug=slug, currency="BRL", locale="pt-BR", status=StoreStatus.active
    )
    db.add(store)
    db.flush()
    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
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
    return store, host, str(product.id), str(method.id)


def _fill_cart(client: TestClient, host: str, product_id: str, qty: int = 2) -> None:
    client.post(
        f"{SF}/cart/items",
        headers={"host": host},
        json={"product_id": product_id, "quantity": qty},
    )


def _checkout_body(method_id: str) -> dict[str, object]:
    return {
        "contact": {"name": "Ana", "email": "ana@x.com"},
        "address": {"line1": "Rua A", "city": "SP", "country": "BR"},
        "shipping_method_id": method_id,
    }


# --- panel CRUD + gating ---


def test_crud(client: TestClient, two_stores: TenantContext) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    base = _coupons_base(store)
    created = client.post(
        base, headers=h, json={"code": "save10", "type": "percentage", "value": 10}
    )
    assert created.status_code == 201
    assert created.json()["code"] == "SAVE10"  # normalized
    coupon_id = created.json()["id"]

    assert any(c["id"] == coupon_id for c in client.get(base, headers=h).json())

    updated = client.patch(f"{base}/{coupon_id}", headers=h, json={"value": 20})
    assert updated.json()["value"] == 20

    assert client.delete(f"{base}/{coupon_id}", headers=h).status_code == 204
    assert client.get(base, headers=h).json() == []


def test_crud_gated(client: TestClient, db: Session, two_stores: TenantContext) -> None:
    store = two_stores.store_a
    base = _coupons_base(store)
    viewer = create_user(db)
    create_member(db, store=store, user=viewer, role_key="support")  # no discounts.*
    headers = member_headers(client, db, viewer)
    assert client.get(base, headers=headers).status_code == 403
    assert (
        client.post(
            base, headers=headers, json={"code": "X", "type": "fixed", "value": 100}
        ).status_code
        == 403
    )


def test_invalid_percentage_value(
    client: TestClient, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    resp = client.post(
        _coupons_base(store),
        headers=h,
        json={"code": "BAD", "type": "percentage", "value": 150},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_coupon_value"


def test_duplicate_active_code_409(
    client: TestClient, two_stores: TenantContext
) -> None:
    store, h = two_stores.store_a, two_stores.owner_a_headers
    base = _coupons_base(store)
    body = {"code": "DUP", "type": "fixed", "value": 500}
    assert client.post(base, headers=h, json=body).status_code == 201
    dup = client.post(base, headers=h, json=body)
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "coupon_code_exists"


# --- cart application ---


def test_apply_percentage_coupon(client: TestClient, db: Session) -> None:
    store, host, product_id, _ = _sf_store(db, "disc-pct")
    _make_coupon(db, store.id, code="SAVE10", value=10)
    _fill_cart(client, host, product_id, qty=2)  # subtotal 3000
    resp = client.post(
        f"{SF}/cart/coupon", headers={"host": host}, json={"code": "save10"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["coupon_code"] == "SAVE10"
    assert body["subtotal_amount_minor"] == 3000
    assert body["discount_amount_minor"] == 300
    assert body["total_amount_minor"] == 2700

    removed = client.request("DELETE", f"{SF}/cart/coupon", headers={"host": host})
    assert removed.json()["discount_amount_minor"] == 0
    assert removed.json()["coupon_code"] is None


def test_apply_below_minimum_is_422(client: TestClient, db: Session) -> None:
    store, host, product_id, _ = _sf_store(db, "disc-min")
    _make_coupon(db, store.id, code="BIG", value=10, min_subtotal_amount_minor=5000)
    _fill_cart(client, host, product_id, qty=1)  # subtotal 1500 < 5000
    resp = client.post(
        f"{SF}/cart/coupon", headers={"host": host}, json={"code": "BIG"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "coupon_below_minimum"


def test_apply_expired_is_422(client: TestClient, db: Session) -> None:
    store, host, product_id, _ = _sf_store(db, "disc-exp")
    _make_coupon(
        db,
        store.id,
        code="OLD",
        value=10,
        valid_until=datetime.now(timezone.utc) - timedelta(days=1),
    )
    _fill_cart(client, host, product_id, qty=1)
    resp = client.post(
        f"{SF}/cart/coupon", headers={"host": host}, json={"code": "OLD"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "coupon_expired"


def test_coupon_isolated_between_stores(client: TestClient, db: Session) -> None:
    store_a, host_a, product_a, _ = _sf_store(db, "disc-iso-a")
    store_b, _, _, _ = _sf_store(db, "disc-iso-b")
    _make_coupon(db, store_b.id, code="ONLYB", value=10)  # exists only in store B
    _fill_cart(client, host_a, product_a, qty=1)
    resp = client.post(
        f"{SF}/cart/coupon", headers={"host": host_a}, json={"code": "ONLYB"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_coupon"


# --- checkout application + redemption ---


def test_checkout_applies_coupon_and_records_redemption(
    client: TestClient, db: Session
) -> None:
    store, host, product_id, method_id = _sf_store(db, "disc-checkout")
    coupon_id = _make_coupon(db, store.id, code="SAVE10", value=10)
    _fill_cart(client, host, product_id, qty=2)  # subtotal 3000
    client.post(f"{SF}/cart/coupon", headers={"host": host}, json={"code": "SAVE10"})

    resp = client.post(
        f"{SF}/checkout", headers={"host": host}, json=_checkout_body(method_id)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["discount_amount_minor"] == 300
    assert body["total_amount_minor"] == 3000 + 900 - 300

    order = db.exec(select(Order).where(Order.store_id == store.id)).one()
    assert order.discount_amount_minor == 300
    assert (
        discounts.redemptions_count(session=db, store_id=store.id, coupon_id=coupon_id)
        == 1
    )


def test_usage_limit_blocks_validation(db: Session) -> None:
    store, _, _, _ = _sf_store(db, "disc-usage")
    coupon_id = _make_coupon(db, store.id, code="ONCE", value=10, max_redemptions=1)
    db.add(
        DiscountCouponRedemption(store_id=store.id, coupon_id=coupon_id, order_id=None)
    )
    db.commit()
    with pytest.raises(AppError) as exc:
        discounts.validate_coupon(
            session=db, store_id=store.id, code="ONCE", subtotal_amount_minor=3000
        )
    assert exc.value.code == "coupon_usage_exceeded"
