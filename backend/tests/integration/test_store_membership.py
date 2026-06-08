"""Integration tests for store membership (store_roles, store_members)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.base import get_datetime_utc
from app.modules.accounts import repositories
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate
from app.modules.stores.models import Store, StoreMember, StoreRole
from tests.utils.utils import random_email, random_lower_string

_ROLE_KEYS = {"owner", "admin", "manager", "support", "catalog", "marketing"}


def _role(db: Session, key: str = "owner") -> StoreRole:
    return db.exec(select(StoreRole).where(StoreRole.key == key)).one()


def _store(db: Session, slug: str) -> Store:
    store = Store(name="Loja", slug=slug, currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    return store


def _user(db: Session) -> User:
    return repositories.create_user(
        session=db,
        user_create=UserCreate(email=random_email(), password=random_lower_string()),
    )


def test_roles_seeded(db: Session) -> None:
    keys = {r.key for r in db.exec(select(StoreRole)).all()}
    assert _ROLE_KEYS <= keys


def test_unique_active_membership(db: Session) -> None:
    store = _store(db, "mem-uniq")
    user = _user(db)
    owner = _role(db, "owner")
    db.add(StoreMember(store_id=store.id, user_id=user.id, role_id=owner.id))
    db.flush()
    with pytest.raises(IntegrityError):
        db.add(StoreMember(store_id=store.id, user_id=user.id, role_id=owner.id))
        db.flush()


def test_soft_delete_frees_reinvite(db: Session) -> None:
    store = _store(db, "mem-reinvite")
    user = _user(db)
    owner = _role(db, "owner")
    m1 = StoreMember(store_id=store.id, user_id=user.id, role_id=owner.id)
    db.add(m1)
    db.flush()
    m1.deleted_at = get_datetime_utc()
    db.add(m1)
    db.flush()
    m2 = StoreMember(store_id=store.id, user_id=user.id, role_id=owner.id)
    db.add(m2)
    db.flush()
    rows = db.exec(
        select(StoreMember).where(
            StoreMember.store_id == store.id, StoreMember.user_id == user.id
        )
    ).all()
    assert len(rows) == 2


def test_member_of_two_stores_with_different_roles(db: Session) -> None:
    user = _user(db)
    store_a = _store(db, "mem-a")
    store_b = _store(db, "mem-b")
    owner = _role(db, "owner")
    support = _role(db, "support")
    db.add(StoreMember(store_id=store_a.id, user_id=user.id, role_id=owner.id))
    db.add(StoreMember(store_id=store_b.id, user_id=user.id, role_id=support.id))
    db.flush()
    members = db.exec(select(StoreMember).where(StoreMember.user_id == user.id)).all()
    assert {m.role_id for m in members} == {owner.id, support.id}
