"""Integration tests for tenancy: get_active_store, host resolution, scoping."""

import uuid

import pytest
from sqlmodel import Session, select

from app.core.api import AppError
from app.modules.accounts import repositories
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate
from app.modules.domains.models import DomainHost
from app.modules.domains.services import create_platform_subdomain
from app.modules.stores.enums import MembershipStatus
from app.modules.stores.models import Store, StoreMember, StoreRole
from app.modules.tenancy.deps import get_active_store
from app.modules.tenancy.services import get_store_scoped, resolve_store_by_host
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


def _owner_role(db: Session) -> StoreRole:
    return db.exec(select(StoreRole).where(StoreRole.key == "owner")).one()


def _add_member(db: Session, store: Store, user: User, role: StoreRole) -> StoreMember:
    member = StoreMember(
        store_id=store.id,
        user_id=user.id,
        role_id=role.id,
        status=MembershipStatus.active,
    )
    db.add(member)
    db.flush()
    return member


def test_get_active_store_member(db: Session) -> None:
    store = _store(db, "ten-a")
    user = _user(db)
    _add_member(db, store, user, _owner_role(db))
    result = get_active_store(store_id=store.id, session=db, current_user=user)
    assert result.id == store.id


def test_get_active_store_non_member_forbidden(db: Session) -> None:
    store = _store(db, "ten-b")
    outsider = _user(db)
    with pytest.raises(AppError) as exc:
        get_active_store(store_id=store.id, session=db, current_user=outsider)
    assert exc.value.status_code == 403


def test_get_active_store_not_found(db: Session) -> None:
    user = _user(db)
    with pytest.raises(AppError) as exc:
        get_active_store(store_id=uuid.uuid4(), session=db, current_user=user)
    assert exc.value.status_code == 404


def test_resolve_store_by_host(db: Session) -> None:
    store = _store(db, "ten-host")
    domain = create_platform_subdomain(session=db, store_id=store.id, slug="ten-host")
    resolved = resolve_store_by_host(session=db, host=domain.host)
    assert resolved is not None
    assert resolved.id == store.id


def test_resolve_unknown_host_returns_none(db: Session) -> None:
    assert resolve_store_by_host(session=db, host="nope.loja.localhost") is None


def test_resolve_uses_cache(db: Session) -> None:
    store = _store(db, "ten-cache")
    domain = create_platform_subdomain(session=db, store_id=store.id, slug="ten-cache")
    first = resolve_store_by_host(session=db, host=domain.host)
    assert first is not None and first.id == store.id
    # Drop the domain row; a cached resolution still resolves (cache was used).
    db.delete(domain)
    db.flush()
    cached = resolve_store_by_host(session=db, host=domain.host)
    assert cached is not None and cached.id == store.id


def test_get_store_scoped_isolation(db: Session) -> None:
    store = _store(db, "ten-scoped")
    other = _store(db, "ten-other")
    domain = create_platform_subdomain(session=db, store_id=store.id, slug="ten-scoped")
    found = get_store_scoped(
        session=db, model=DomainHost, store_id=store.id, resource_id=domain.id
    )
    assert found is not None
    missing = get_store_scoped(
        session=db, model=DomainHost, store_id=other.id, resource_id=domain.id
    )
    assert missing is None
