"""API request/response schemas for the content module."""

import uuid

from sqlmodel import Field, SQLModel

from app.modules.content.enums import MenuLocation
from app.modules.content.models import (
    ContentPageBase,
    ContentStoreThemeSettingsBase,
    ContentThemeTemplateBase,
)


class ThemeUpdate(SQLModel):
    """Partial theme update: apply a template and/or edit appearance.

    Only the fields actually sent are applied (``exclude_unset``). Setting
    ``active_template_id`` validates the target is an available template.
    """

    active_template_id: str | None = None
    banner_image_url: str | None = Field(default=None, max_length=2048)
    headline: str | None = Field(default=None, max_length=255)
    featured_collection_id: uuid.UUID | None = None


class ThemeTemplatePublic(ContentThemeTemplateBase):
    """Public representation of a global theme template (with its editable schema)."""

    id: str
    settings_schema: list[dict[str, object]] | None = None


class TemplateSettingsPublic(SQLModel):
    """A store's saved chrome overrides for a template (keyed by schema ``key``)."""

    template_id: str
    settings: dict[str, object] = {}


class TemplateSettingsUpdate(SQLModel):
    """Patch the store's chrome overrides for the active template."""

    settings: dict[str, object]


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
