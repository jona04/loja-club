"""Enumerations for the platform_admin module."""

from enum import Enum


class PlatformRole(str, Enum):
    """Global platform-admin roles (doc 08). Not scoped to a store.

    - ``platform_owner``: holds the full ``platform.*`` catalog.
    - ``platform_ops``: store/user operation + support + plans/webhooks/audit (read).
    - ``platform_finance``: stores/plans/audit (read + plan updates).
    - ``platform_support``: support with impersonation + read access.
    - ``platform_catalog``: 3D models + templates management.
    """

    platform_owner = "platform_owner"
    platform_ops = "platform_ops"
    platform_finance = "platform_finance"
    platform_support = "platform_support"
    platform_catalog = "platform_catalog"
