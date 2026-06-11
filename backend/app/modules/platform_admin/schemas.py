"""API schemas for platform-admin operations (stores, templates)."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

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


class ThemeTemplateAdminPublic(SQLModel):
    """A theme template as managed in the platform admin."""

    id: str
    name: str
    description: str | None = None
    is_active: bool
    preview_image_url: str | None = None
    settings_schema: list[dict[str, object]] | None = None


class ThemeTemplateCreate(SQLModel):
    """Payload to register a theme template (its code must already exist)."""

    id: str = Field(max_length=50)
    name: str = Field(max_length=255)
    description: str | None = None
    is_active: bool = True
    preview_image_url: str | None = Field(default=None, max_length=2048)


class ThemeTemplateUpdate(SQLModel):
    """Patch payload for a theme template (unset fields are ignored)."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    is_active: bool | None = None
    preview_image_url: str | None = Field(default=None, max_length=2048)


class PlatformMe(SQLModel):
    """The signed-in user and their platform roles (empty if not an admin)."""

    id: uuid.UUID
    email: str
    full_name: str | None = None
    is_platform_admin: bool
    platform_roles: list[str] = []
