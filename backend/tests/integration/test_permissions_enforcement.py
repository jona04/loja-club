"""Integration tests for require_permission and the active-membership guard."""

import pytest
from sqlmodel import Session, select

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.accounts import repositories
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate
from app.modules.stores.enums import MembershipStatus, StoreStatus
from app.modules.stores.models import Store, StoreMember, StoreRole
from app.modules.tenancy.deps import get_active_membership, require_permission
from tests.utils.utils import random_email, random_lower_string


def _user(db: Session) -> User:
    return repositories.create_user(
        session=db,
        user_create=UserCreate(email=random_email(), password=random_lower_string()),
    )


def _store(db: Session, slug: str) -> Store:
    store = Store(name="Loja", slug=slug, currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    return store


def _member(db: Session, store: Store, user: User, role_key: str) -> StoreMember:
    role = db.exec(select(StoreRole).where(StoreRole.key == role_key)).one()
    member = StoreMember(
        store_id=store.id,
        user_id=user.id,
        role_id=role.id,
        status=MembershipStatus.active,
    )
    db.add(member)
    db.flush()
    return member


def test_get_active_membership_non_member_forbidden(db: Session) -> None:
    store = _store(db, "perm-a")
    outsider = _user(db)
    with pytest.raises(AppError) as exc:
        get_active_membership(store_id=store.id, session=db, current_user=outsider)
    assert exc.value.status_code == 403


def test_get_active_membership_suspended_store_unavailable(db: Session) -> None:
    store = _store(db, "perm-susp")
    store.status = StoreStatus.suspended
    db.add(store)
    db.flush()
    user = _user(db)
    _member(db, store, user, "owner")
    with pytest.raises(AppError) as exc:
        get_active_membership(store_id=store.id, session=db, current_user=user)
    assert exc.value.status_code == 403
    assert exc.value.code == "store_unavailable"


def test_get_active_membership_deleted_store_not_found(db: Session) -> None:
    store = _store(db, "perm-del")
    store.deleted_at = get_datetime_utc()
    db.add(store)
    db.flush()
    user = _user(db)
    _member(db, store, user, "owner")
    with pytest.raises(AppError) as exc:
        get_active_membership(store_id=store.id, session=db, current_user=user)
    assert exc.value.status_code == 404


def test_require_permission_owner_allowed(db: Session) -> None:
    store = _store(db, "perm-owner")
    membership = _member(db, store, _user(db), "owner")
    dep = require_permission("settings.update")
    result = dep(membership=membership, session=db)
    assert result.id == membership.id


def test_require_permission_support_denied(db: Session) -> None:
    store = _store(db, "perm-support")
    membership = _member(db, store, _user(db), "support")
    dep = require_permission("layout.update")  # support is not granted this
    with pytest.raises(AppError) as exc:
        dep(membership=membership, session=db)
    assert exc.value.status_code == 403


def test_require_permission_support_allowed_for_granted(db: Session) -> None:
    store = _store(db, "perm-support2")
    membership = _member(db, store, _user(db), "support")
    dep = require_permission("orders.view")  # support is granted this
    result = dep(membership=membership, session=db)
    assert result.id == membership.id
