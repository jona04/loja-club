"""Enumerations for the domains module (doc 06)."""

from enum import Enum


class DomainType(str, Enum):
    """Kind of host bound to a store."""

    platform_subdomain = "platform_subdomain"
    custom_domain = "custom_domain"


class DomainStatus(str, Enum):
    """Lifecycle status of a domain host."""

    pending = "pending"
    active = "active"
    failed = "failed"
    blocked = "blocked"


class SslStatus(str, Enum):
    """SSL provisioning status of a domain host."""

    pending = "pending"
    issued = "issued"
    failed = "failed"
