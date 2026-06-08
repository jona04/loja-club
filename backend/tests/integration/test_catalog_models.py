"""Integration tests for the catalog models (products, variants, categories...)."""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.base import get_datetime_utc
from app.modules.catalog.enums import ProductStatus, ProductVariantStatus
from app.modules.catalog.models import (
    Category,
    InventoryItem,
    Product,
    ProductVariant,
)
from tests.utils.store import create_store


def _make_product(
    db: Session, store_id: uuid.UUID, *, slug: str = "mug", name: str = "Mug"
) -> Product:
    """Persist a minimal product for ``store_id`` and return it."""
    product = Product(
        store_id=store_id,
        name=name,
        slug=slug,
        price_amount_minor=1500,
        price_currency="USD",
    )
    db.add(product)
    db.flush()
    return product


def test_product_defaults(db: Session) -> None:
    store = create_store(db)
    product = _make_product(db, store.id)
    assert product.id is not None
    assert product.status == ProductStatus.draft
    assert product.is_featured is False
    assert product.price_amount_minor == 1500
    assert product.price_currency == "USD"
    assert product.deleted_at is None


def test_product_slug_unique_per_active_store(db: Session) -> None:
    store = create_store(db)
    _make_product(db, store.id, slug="dup")
    with pytest.raises(IntegrityError):
        _make_product(db, store.id, slug="dup", name="Other")


def test_product_slug_reusable_across_stores(db: Session) -> None:
    store_a = create_store(db, slug="store-a")
    store_b = create_store(db, slug="store-b")
    _make_product(db, store_a.id, slug="same")
    other = _make_product(db, store_b.id, slug="same")
    assert other.id is not None


def test_product_slug_reusable_after_soft_delete(db: Session) -> None:
    store = create_store(db)
    first = _make_product(db, store.id, slug="reuse")
    first.deleted_at = get_datetime_utc()
    db.add(first)
    db.flush()
    second = _make_product(db, store.id, slug="reuse", name="New")
    assert second.id != first.id
    rows = db.exec(select(Product).where(Product.slug == "reuse")).all()
    assert len(rows) == 2


def test_product_store_id_foreign_key_enforced(db: Session) -> None:
    with pytest.raises(IntegrityError):
        _make_product(db, uuid.uuid4())


def test_category_slug_unique_per_active_store(db: Session) -> None:
    store = create_store(db)
    db.add(Category(store_id=store.id, name="Mugs", slug="mugs"))
    db.flush()
    with pytest.raises(IntegrityError):
        db.add(Category(store_id=store.id, name="Mugs 2", slug="mugs"))
        db.flush()


def test_variant_and_inventory_chain(db: Session) -> None:
    store = create_store(db)
    product = _make_product(db, store.id)
    variant = ProductVariant(store_id=store.id, product_id=product.id, name="Size M")
    db.add(variant)
    db.flush()
    inventory = InventoryItem(
        store_id=store.id, product_id=product.id, variant_id=variant.id, quantity=10
    )
    db.add(inventory)
    db.flush()
    assert variant.status == ProductVariantStatus.active
    assert inventory.quantity == 10
