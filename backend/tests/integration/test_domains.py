"""Integration tests for the domains module (domain_hosts + subdomain + cache)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.cache import cache_get, cache_set
from app.core.config import settings
from app.modules.domains.enums import DomainStatus, DomainType
from app.modules.domains.models import DomainHost
from app.modules.domains.services import (
    create_platform_subdomain,
    is_subdomain_available,
    subdomain_host,
)
from app.modules.stores.models import Store


def _store(db: Session, slug: str) -> Store:
    store = Store(name="Loja", slug=slug, currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    return store


def test_create_platform_subdomain(db: Session) -> None:
    store = _store(db, "brindes")
    domain = create_platform_subdomain(session=db, store_id=store.id, slug="brindes")
    assert domain.host == f"brindes.{settings.DOMAIN}"
    assert domain.type == DomainType.platform_subdomain
    assert domain.status == DomainStatus.active


def test_host_unique_among_active(db: Session) -> None:
    store = _store(db, "uniq")
    create_platform_subdomain(session=db, store_id=store.id, slug="uniq")
    with pytest.raises(IntegrityError):
        db.add(DomainHost(store_id=store.id, host=f"uniq.{settings.DOMAIN}"))
        db.flush()


def test_is_subdomain_available(db: Session) -> None:
    store = _store(db, "avail")
    assert is_subdomain_available(session=db, slug="avail") is True
    create_platform_subdomain(session=db, store_id=store.id, slug="avail")
    assert is_subdomain_available(session=db, slug="avail") is False


def test_create_invalidates_domain_cache(db: Session) -> None:
    store = _store(db, "cachekey")
    host = subdomain_host("cachekey")
    cache_set(host, "stale", prefix="domain")
    assert cache_get(host, prefix="domain") == "stale"
    create_platform_subdomain(session=db, store_id=store.id, slug="cachekey")
    assert cache_get(host, prefix="domain") is None
