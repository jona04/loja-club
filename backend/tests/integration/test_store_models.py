"""Integration tests for the store models (store_stores, store_settings)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.base import get_datetime_utc
from app.modules.stores.models import Store, StoreSettings, StoreStatus


def _make_store(db: Session, slug: str = "loja-a", name: str = "Loja A") -> Store:
    store = Store(name=name, slug=slug, currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    return store


def test_create_store_defaults(db: Session) -> None:
    store = _make_store(db)
    assert store.id is not None
    assert store.status == StoreStatus.draft
    assert store.currency == "USD"
    assert store.locale == "en-US"
    assert store.created_at is not None
    assert store.updated_at is not None
    assert store.deleted_at is None


def test_slug_unique_among_non_deleted(db: Session) -> None:
    _make_store(db, slug="dup")
    with pytest.raises(IntegrityError):
        _make_store(db, slug="dup", name="Loja B")


def test_slug_reusable_after_soft_delete(db: Session) -> None:
    s1 = _make_store(db, slug="reuse")
    s1.deleted_at = get_datetime_utc()
    db.add(s1)
    db.flush()
    s2 = _make_store(db, slug="reuse", name="Loja B")
    assert s2.id != s1.id
    rows = db.exec(select(Store).where(Store.slug == "reuse")).all()
    assert len(rows) == 2


def test_store_settings_one_per_store(db: Session) -> None:
    store = _make_store(db, slug="cfg")
    db.add(StoreSettings(store_id=store.id, public_name="Loja"))
    db.flush()
    with pytest.raises(IntegrityError):
        db.add(StoreSettings(store_id=store.id, public_name="Dup"))
        db.flush()
