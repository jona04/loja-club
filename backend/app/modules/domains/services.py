"""Domain services: platform subdomains, availability and cache invalidation."""

import uuid

from sqlmodel import Session, col, select

from app.core.cache import cache_delete
from app.core.config import settings
from app.modules.domains.enums import DomainStatus, DomainType, SslStatus
from app.modules.domains.models import DomainHost


def subdomain_host(slug: str) -> str:
    """Return the platform host for a store slug (``{slug}.{DOMAIN}``).

    Args:
        slug: The store slug.

    Returns:
        The fully-qualified platform host.
    """
    return f"{slug}.{settings.DOMAIN}"


def invalidate_domain_cache(host: str) -> None:
    """Invalidate the cached host->store resolution for ``host``.

    Args:
        host: The host whose ``domain:{host}`` cache entry is dropped.
    """
    cache_delete(host, prefix="domain")


def is_subdomain_available(*, session: Session, slug: str) -> bool:
    """Return whether the platform subdomain for ``slug`` is free.

    Args:
        session: Active database session.
        slug: Store slug to check.

    Returns:
        True if no active (non-deleted) host uses ``{slug}.{DOMAIN}``.
    """
    host = subdomain_host(slug)
    existing = session.exec(
        select(DomainHost).where(
            DomainHost.host == host, col(DomainHost.deleted_at).is_(None)
        )
    ).first()
    return existing is None


def create_platform_subdomain(
    *, session: Session, store_id: uuid.UUID, slug: str
) -> DomainHost:
    """Create the automatic platform subdomain for a store (doc 06).

    Flushes (not commits) so the caller can include it in the atomic
    store-creation transaction. Invalidates any stale host cache entry.

    Args:
        session: Active database session.
        store_id: The store the subdomain belongs to.
        slug: Store slug; the host becomes ``{slug}.{DOMAIN}``.

    Returns:
        The created (active) DomainHost.
    """
    host = subdomain_host(slug)
    domain = DomainHost(
        store_id=store_id,
        host=host,
        type=DomainType.platform_subdomain,
        status=DomainStatus.active,
        ssl_status=SslStatus.issued,
    )
    session.add(domain)
    session.flush()
    invalidate_domain_cache(host)
    return domain
