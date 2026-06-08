"""Tenancy services: host->store resolution (storefront) and scoped fetch."""

import uuid
from typing import Any, TypeVar, cast

from sqlmodel import Session, SQLModel, col, select

from app.core.cache import cache_get, cache_set
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.stores.models import Store

# Cached host->store resolutions live for a few minutes; domain mutations
# invalidate eagerly (see domains.services.invalidate_domain_cache).
_DOMAIN_CACHE_TTL = 300

T = TypeVar("T", bound=SQLModel)


def resolve_store_by_host(*, session: Session, host: str) -> Store | None:
    """Resolve the active store served at ``host`` (storefront), cached.

    Checks the ``domain:{host}`` cache first; on miss, looks up an active
    ``domain_hosts`` row and caches the resolved store id. An unknown/inactive
    host returns ``None`` (the caller renders "loja não encontrada"; INV-T4).

    Args:
        session: Active database session.
        host: The request ``Host`` header value.

    Returns:
        The resolved active store, or ``None``.
    """
    cached = cache_get(host, prefix="domain")
    if cached is not None:
        store = session.get(Store, uuid.UUID(cached))
        if store is not None and store.deleted_at is None:
            return store

    domain = session.exec(
        select(DomainHost).where(
            DomainHost.host == host,
            DomainHost.status == DomainStatus.active,
            col(DomainHost.deleted_at).is_(None),
        )
    ).first()
    if domain is None:
        return None
    store = session.get(Store, domain.store_id)
    if store is None or store.deleted_at is not None:
        return None
    cache_set(host, str(store.id), ttl=_DOMAIN_CACHE_TTL, prefix="domain")
    return store


def get_store_scoped(
    *,
    session: Session,
    model: type[T],
    store_id: uuid.UUID,
    resource_id: uuid.UUID,
) -> T | None:
    """Fetch a store-scoped row by ``(store_id, id)``, excluding soft-deleted.

    Enforces INV-T2/T3: commercial resources are never fetched by id alone. The
    ``model`` must carry ``store_id``, ``id`` and ``deleted_at`` (mixins).

    Args:
        session: Active database session.
        model: The store-scoped table model.
        store_id: The active store id.
        resource_id: The resource id within the store.

    Returns:
        The matching row, or ``None``.
    """
    # The model carries store_id/id/deleted_at (mixins); access them via an
    # Any cast so both type checkers accept the dynamic column references.
    scoped = cast(Any, model)
    return session.exec(
        select(model).where(
            scoped.store_id == store_id,
            scoped.id == resource_id,
            col(scoped.deleted_at).is_(None),
        )
    ).first()
