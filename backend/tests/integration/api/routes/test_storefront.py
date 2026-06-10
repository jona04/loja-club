"""Integration tests for the public storefront API (host-resolved reads)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.cache import cache_get
from app.modules.catalog.enums import ProductStatus
from app.modules.catalog.models import Category, Product, ProductCategory
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store

BASE = "/api/v1/storefront"


def _published_store(
    db: Session, *, slug: str, status: StoreStatus = StoreStatus.active
) -> tuple[Store, str]:
    store = Store(name="Loja", slug=slug, currency="USD", locale="en-US", status=status)
    db.add(store)
    db.flush()
    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
    db.flush()
    return store, host


def _product(
    db: Session,
    store_id: uuid.UUID,
    *,
    slug: str,
    status: ProductStatus = ProductStatus.published,
    featured: bool = False,
) -> Product:
    product = Product(
        store_id=store_id,
        name=slug.title(),
        slug=slug,
        status=status,
        price_amount_minor=1500,
        price_currency="USD",
        is_featured=featured,
    )
    db.add(product)
    db.flush()
    return product


def test_home_for_published_store(client: TestClient, db: Session) -> None:
    store, host = _published_store(db, slug="sf-home")
    mug = _product(db, store.id, slug="mug", featured=True)
    category = Category(store_id=store.id, name="Canecas", slug="canecas")
    db.add(category)
    db.flush()
    db.add(
        ProductCategory(store_id=store.id, product_id=mug.id, category_id=category.id)
    )
    db.flush()
    resp = client.get(f"{BASE}/home", headers={"host": host})
    assert resp.status_code == 200
    body = resp.json()
    assert body["store"]["slug"] == "sf-home"
    assert body["theme"]["active_template_id"] == "aurora"  # default, no row
    assert any(p["slug"] == "mug" for p in body["featured_products"])
    # category sections (for templates like Bazar): the mug's category appears.
    assert any(
        p["slug"] == "mug" for s in body["category_sections"] for p in s["products"]
    )


def test_unknown_host_is_not_found(client: TestClient) -> None:
    resp = client.get(f"{BASE}/home", headers={"host": "nope.localhost"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "store_not_found"


def test_unpublished_store_is_not_found(client: TestClient, db: Session) -> None:
    _, host = _published_store(db, slug="sf-draft", status=StoreStatus.draft)
    resp = client.get(f"{BASE}/home", headers={"host": host})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "store_not_found"


def test_only_published_products_listed(client: TestClient, db: Session) -> None:
    store, host = _published_store(db, slug="sf-prod")
    _product(db, store.id, slug="pub", status=ProductStatus.published)
    _product(db, store.id, slug="drafted", status=ProductStatus.draft)
    resp = client.get(f"{BASE}/products", headers={"host": host})
    assert resp.status_code == 200
    assert {p["slug"] for p in resp.json()["data"]} == {"pub"}


def test_product_by_slug_and_cache(client: TestClient, db: Session) -> None:
    store, host = _published_store(db, slug="sf-slug")
    _product(db, store.id, slug="mug")
    resp = client.get(f"{BASE}/products/mug", headers={"host": host})
    assert resp.status_code == 200
    assert resp.json()["slug"] == "mug"
    assert cache_get(f"{store.id}:product:mug", prefix="store") is not None
    assert (
        client.get(f"{BASE}/products/nope", headers={"host": host}).status_code == 404
    )


def test_products_isolated_between_stores(client: TestClient, db: Session) -> None:
    store_a, host_a = _published_store(db, slug="sf-a")
    store_b, _ = _published_store(db, slug="sf-b")
    _product(db, store_a.id, slug="a-prod")
    _product(db, store_b.id, slug="b-prod")
    resp = client.get(f"{BASE}/products", headers={"host": host_a})
    assert {p["slug"] for p in resp.json()["data"]} == {"a-prod"}


def test_products_filtered_by_category(client: TestClient, db: Session) -> None:
    store, host = _published_store(db, slug="sf-cat")
    category = Category(store_id=store.id, name="Canecas", slug="canecas")
    db.add(category)
    db.flush()
    in_cat = _product(db, store.id, slug="in-cat")
    _product(db, store.id, slug="out-cat")
    db.add(
        ProductCategory(
            store_id=store.id, product_id=in_cat.id, category_id=category.id
        )
    )
    db.flush()
    resp = client.get(f"{BASE}/products?category=canecas", headers={"host": host})
    assert resp.status_code == 200
    assert {p["slug"] for p in resp.json()["data"]} == {"in-cat"}
