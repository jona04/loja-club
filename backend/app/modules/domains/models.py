"""Domain host model: subdomains/custom domains that route to a store (doc 06).

API schemas live in ``schemas.py``; enums in ``enums.py``.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, text
from sqlmodel import Field

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.modules.domains.enums import DomainStatus, DomainType, SslStatus


class DomainHost(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    """A host (platform subdomain or custom domain) that routes to a store.

    ``host`` is unique among non-deleted rows, so an archived store's host can
    be reused (mirrors the store ``slug``). The V1 has no "primary domain": any
    active host of a store renders the same store (doc 06).
    """

    __tablename__ = "domain_hosts"
    __table_args__ = (
        Index(
            "ix_domain_hosts_host_active",
            "host",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_domain_hosts_store_status", "store_id", "status"),
    )

    store_id: uuid.UUID = Field(foreign_key="store_stores.id", index=True)
    host: str = Field(max_length=255)
    type: DomainType = Field(default=DomainType.platform_subdomain)
    status: DomainStatus = Field(default=DomainStatus.pending)
    ssl_status: SslStatus = Field(default=SslStatus.pending)
    verified_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
