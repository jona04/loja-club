"""API request/response schemas for the stores module."""

import uuid

from app.modules.stores.models import StoreBase, StoreSettingsBase


class StorePublic(StoreBase):
    """Store as returned via the API."""

    id: uuid.UUID


class StoreSettingsPublic(StoreSettingsBase):
    """Store settings as returned via the API."""

    id: uuid.UUID
    store_id: uuid.UUID
    social_links: dict[str, str] | None = None
