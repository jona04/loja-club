"""API schemas for platform-admin store operations."""

import uuid
from datetime import datetime

from sqlmodel import SQLModel

from app.modules.stores.enums import StoreStatus
from app.modules.stores.schemas import StoreMemberPublic, StoreSettingsPublic


class StoreAdminListItem(SQLModel):
    """A store as listed in the platform admin (cross-store)."""

    id: uuid.UUID
    name: str
    slug: str
    status: StoreStatus
    created_at: datetime


class StoreAdminDetail(StoreAdminListItem):
    """A store's admin detail: identity + settings + members.

    Orders/volume/webhooks/commissions are **not** included here yet — those
    modules do not exist in the codebase yet.
    """

    settings: StoreSettingsPublic | None = None
    members: list[StoreMemberPublic] = []
