"""Enumerations for the stores module."""

from enum import Enum


class StoreStatus(str, Enum):
    """Lifecycle status of a store (doc 09)."""

    draft = "draft"
    active = "active"
    paused = "paused"
    suspended = "suspended"
    blocked = "blocked"
    archived = "archived"
