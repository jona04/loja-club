"""API request/response schemas for the content module."""

import uuid

from sqlmodel import SQLModel

from app.modules.content.enums import MenuLocation
from app.modules.content.models import (
    ContentPageBase,
    ContentStoreThemeSettingsBase,
    ContentThemeTemplateBase,
)


class ThemeTemplatePublic(ContentThemeTemplateBase):
    """Public representation of a global theme template."""

    id: str


class StoreThemeSettingsPublic(ContentStoreThemeSettingsBase):
    """Public representation of a store's theme/appearance settings."""

    id: uuid.UUID
    store_id: uuid.UUID


class ContentPagePublic(ContentPageBase):
    """Public representation of an editorial page."""

    id: uuid.UUID
    store_id: uuid.UUID


class ContentMenuItemPublic(SQLModel):
    """Public representation of a single menu item."""

    id: uuid.UUID
    menu_id: uuid.UUID
    label: str
    url: str
    position: int


class ContentMenuPublic(SQLModel):
    """Public representation of a navigation menu and its ordered items."""

    id: uuid.UUID
    store_id: uuid.UUID
    name: str
    location: MenuLocation
    items: list[ContentMenuItemPublic] = []


class ContentBannerPublic(SQLModel):
    """Public representation of a storefront banner."""

    id: uuid.UUID
    store_id: uuid.UUID
    image_url: str
    link_url: str | None = None
    title: str | None = None
    is_active: bool
    position: int
