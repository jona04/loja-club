"""Integration tests for the template demo store seeding."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, func, select

from app.modules.catalog.enums import ProductStatus
from app.modules.catalog.models import Category, Product, ProductImage
from app.modules.content import import_assets
from app.modules.content.demo_store import seed_demo_stores, seed_template_demo_store
from app.modules.content.models import ContentStoreThemeSettings, ContentThemeTemplate
from app.modules.domains.models import DomainHost
from app.modules.stores.models import Store

_TID = "demotest"


def _demo() -> dict[str, Any]:
    return {
        "categories": [
            {"name": "Canecas", "slug": "canecas"},
            {"name": "Camisetas", "slug": "camisetas"},
        ],
        "products": [
            {
                "name": "Caneca",
                "slug": "caneca",
                "price": 5900,
                "category": "canecas",
                "image": "https://cdn.x/public/templates/demotest/a.png",
            },
            {
                "name": "Camiseta",
                "slug": "camiseta",
                "price": 7900,
                "category": "camisetas",
                "image": "https://cdn.x/public/templates/demotest/b.png",
            },
        ],
    }


def _register_template(db: Session) -> None:
    """Register the test template so the demo store's FK to it resolves."""
    db.add(ContentThemeTemplate(id=_TID, name="Demo Test"))
    db.flush()


def test_seed_builds_demo_store(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    """The demo store is built from the demo: active template + published catalog."""
    _register_template(db)
    monkeypatch.setattr(import_assets, "load_demo", lambda _id: _demo())

    store = seed_template_demo_store(session=db, template_id=_TID)
    assert store is not None
    assert store.slug == "demotest-demo"

    theme = db.exec(
        select(ContentStoreThemeSettings).where(
            ContentStoreThemeSettings.store_id == store.id
        )
    ).one()
    assert theme.active_template_id == _TID

    host = db.exec(select(DomainHost).where(DomainHost.store_id == store.id)).one()
    assert host.host == "demotest-demo.localhost"

    assert (
        len(db.exec(select(Category).where(Category.store_id == store.id)).all()) == 2
    )
    products = db.exec(select(Product).where(Product.store_id == store.id)).all()
    assert len(products) == 2
    assert all(p.status == ProductStatus.published for p in products)
    images = db.exec(
        select(ProductImage).where(ProductImage.store_id == store.id)
    ).all()
    assert len(images) == 2


def test_seed_is_idempotent(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    """Re-seeding the same template reuses the store and never duplicates."""
    _register_template(db)
    monkeypatch.setattr(import_assets, "load_demo", lambda _id: _demo())

    first = seed_template_demo_store(session=db, template_id=_TID)
    second = seed_template_demo_store(session=db, template_id=_TID)
    assert first is not None and second is not None
    assert first.id == second.id
    count = db.exec(
        select(func.count()).select_from(Product).where(Product.store_id == first.id)
    ).one()
    assert count == 2


def test_seed_unknown_template_returns_none(db: Session) -> None:
    assert (
        seed_template_demo_store(session=db, template_id="really-does-not-exist")
        is None
    )


def test_demo_store_served_by_storefront(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The demo store is served like any storefront, resolved by its host."""
    _register_template(db)
    monkeypatch.setattr(import_assets, "load_demo", lambda _id: _demo())
    seed_template_demo_store(session=db, template_id=_TID)

    resp = client.get(
        "/api/v1/storefront/home", headers={"host": "demotest-demo.localhost"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["store"]["slug"] == "demotest-demo"
    assert body["theme"]["active_template_id"] == _TID
    assert body["featured_products"]


def test_seed_demo_stores_covers_active_templates(db: Session) -> None:
    """The bulk seed builds a demo store for every active (shipped) template."""
    seed_demo_stores(session=db)
    slugs = set(db.exec(select(Store.slug).where(col(Store.slug).like("%-demo"))).all())
    assert {"aurora-demo", "bazar-demo", "studio-demo"} <= slugs
