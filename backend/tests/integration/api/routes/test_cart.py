"""Integration tests for the public cart routes (P6-CART-01)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.catalog.enums import (
    ProductStatus,
    ProductType,
    ProductVariantStatus,
)
from app.modules.catalog.models import InventoryItem, Product, ProductVariant
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store

CART = "/api/v1/storefront/cart"


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
    db: Session,
    store: Store,
    *,
    slug: str = "prod",
    price: int = 1500,
    ptype: ProductType = ProductType.image,
    stock: int | None = None,
) -> Product:
    product = Product(
        store_id=store.id,
        name=slug.title(),
        slug=slug,
        type=ptype,
        status=ProductStatus.published,
        price_amount_minor=price,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    if stock is not None:
        db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=stock))
        db.flush()
    return product


def test_add_and_subtotal(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-add")
    product = _product(db, store, price=1500, stock=10)
    resp = client.post(
        f"{CART}/items",
        headers={"host": host},
        json={"product_id": str(product.id), "quantity": 2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["item_count"] == 2
    assert body["subtotal_amount_minor"] == 3000
    assert body["currency"] == "BRL"
    assert body["items"][0]["name"] == "Prod"
    assert body["items"][0]["line_total_amount_minor"] == 3000


def test_add_merges_same_line(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-merge")
    product = _product(db, store, stock=10)
    h = {"host": host}
    client.post(
        f"{CART}/items", headers=h, json={"product_id": str(product.id), "quantity": 1}
    )
    body = client.post(
        f"{CART}/items", headers=h, json={"product_id": str(product.id), "quantity": 2}
    ).json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3


def test_stock_enforced(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-stock")
    product = _product(db, store, stock=3)
    h = {"host": host}
    over = client.post(
        f"{CART}/items", headers=h, json={"product_id": str(product.id), "quantity": 4}
    )
    assert over.status_code == 409
    assert over.json()["error"]["code"] == "insufficient_stock"
    ok = client.post(
        f"{CART}/items", headers=h, json={"product_id": str(product.id), "quantity": 3}
    )
    assert ok.status_code == 200


def test_untracked_product_has_no_limit(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-untracked")
    product = _product(db, store, stock=None)  # no inventory row
    resp = client.post(
        f"{CART}/items",
        headers={"host": host},
        json={"product_id": str(product.id), "quantity": 99},
    )
    assert resp.status_code == 200
    assert resp.json()["item_count"] == 99


def test_update_and_remove(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-upd")
    product = _product(db, store, stock=10)
    h = {"host": host}
    added = client.post(
        f"{CART}/items", headers=h, json={"product_id": str(product.id), "quantity": 1}
    ).json()
    item_id = added["items"][0]["id"]
    upd = client.patch(f"{CART}/items/{item_id}", headers=h, json={"quantity": 5})
    assert upd.json()["item_count"] == 5
    rem = client.delete(f"{CART}/items/{item_id}", headers=h)
    assert rem.json()["items"] == []
    assert rem.json()["item_count"] == 0


def test_gate_blocks_customizable(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-gate")
    product = _product(db, store, ptype=ProductType.image_3d_customizable, stock=10)
    resp = client.post(
        f"{CART}/items",
        headers={"host": host},
        json={"product_id": str(product.id), "quantity": 1},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "customization_required"


def test_item_not_found_is_404(client: TestClient, db: Session) -> None:
    _, host = _store(db, "cart-404")
    missing = "00000000-0000-0000-0000-000000000000"
    resp = client.delete(f"{CART}/items/{missing}", headers={"host": host})
    assert resp.status_code == 404


def test_product_not_found_is_404(client: TestClient, db: Session) -> None:
    _, host = _store(db, "cart-prod404")
    missing = "00000000-0000-0000-0000-000000000000"
    resp = client.post(
        f"{CART}/items",
        headers={"host": host},
        json={"product_id": missing, "quantity": 1},
    )
    assert resp.status_code == 404


def test_variant_price_and_not_found(client: TestClient, db: Session) -> None:
    store, host = _store(db, "cart-variant")
    product = _product(db, store, price=1500, stock=10)
    variant = ProductVariant(
        store_id=store.id,
        product_id=product.id,
        name="G",
        status=ProductVariantStatus.active,
        price_override_amount_minor=2000,
        price_override_currency="BRL",
    )
    db.add(variant)
    db.flush()
    body = client.post(
        f"{CART}/items",
        headers={"host": host},
        json={
            "product_id": str(product.id),
            "variant_id": str(variant.id),
            "quantity": 1,
        },
    ).json()
    assert body["items"][0]["unit_price_amount_minor"] == 2000
    assert body["items"][0]["variant_id"] == str(variant.id)

    missing = "00000000-0000-0000-0000-000000000000"
    bad = client.post(
        f"{CART}/items",
        headers={"host": host},
        json={"product_id": str(product.id), "variant_id": missing, "quantity": 1},
    )
    assert bad.status_code == 404


def test_isolated_between_stores(client: TestClient, db: Session) -> None:
    store_a, host_a = _store(db, "cart-iso-a")
    _, host_b = _store(db, "cart-iso-b")
    product_a = _product(db, store_a, slug="pa", stock=10)
    client.post(
        f"{CART}/items",
        headers={"host": host_a},
        json={"product_id": str(product_a.id), "quantity": 1},
    )
    # Store B's cart is independent (its own guest session) → empty.
    resp = client.get(CART, headers={"host": host_b})
    assert resp.json()["items"] == []
