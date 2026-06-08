"""Enumerations for the stores module."""

from enum import Enum


class StoreStatus(str, Enum):
    """Lifecycle status of a store (doc 09).

    - ``draft``: created, not yet published (not served on the storefront).
    - ``active``: published/live — the only status the storefront serves.
    - ``paused``: taken offline by the merchant (reversible via publish).
    - ``suspended``/``blocked``: turned off by the platform (Fase 7); the
      dashboard guard blocks access.

    Removing a store is a **soft delete** (``deleted_at``), never a status.
    """

    draft = "draft"
    active = "active"
    paused = "paused"
    suspended = "suspended"
    blocked = "blocked"


class MembershipStatus(str, Enum):
    """Lifecycle status of a store membership."""

    invited = "invited"
    active = "active"
    removed = "removed"
