"""Content tables: theme templates/settings, pages, menus, banners (doc 10/07).

``content_theme_templates`` is **global** (seeded, shared by every store, never
soft-deleted); everything else is per-store (``store_id``) and soft-deleted
(doc 07). Contact/business data (``logo_url``, description, ...) lives in
``store_settings`` (Fase 1), not here — the theme is appearance/layout only.
API schemas live in ``schemas.py``; enums in ``enums.py``.
"""

import uuid

from sqlalchemy import JSON, Column, Index, text
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, StoreScopedMixin, TimestampMixin, UUIDMixin
from app.modules.content.enums import MenuLocation


class ContentThemeTemplateBase(SQLModel):
    """Shared fields of a global storefront theme template (doc 10)."""

    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    preview_image_url: str | None = Field(default=None, max_length=2048)


class ContentThemeTemplate(TimestampMixin, ContentThemeTemplateBase, table=True):
    """A global storefront theme template (e.g. ``classic``/``modern``).

    Global (no ``store_id``) and seeded; never soft-deleted. ``id`` is the
    template key referenced by ``content_store_theme_settings.active_template_id``.
    ``is_active`` gates which templates the merchant may select (read in
    ``P3-CONTENT-02``).
    """

    __tablename__ = "content_theme_templates"

    id: str = Field(primary_key=True, max_length=50)
    settings_schema: list[dict[str, object]] | None = Field(
        default=None, sa_column=Column(JSON)
    )


class ContentStoreThemeSettingsBase(SQLModel):
    """Shared per-store appearance fields (doc 10)."""

    active_template_id: str = Field(
        foreign_key="content_theme_templates.id", index=True
    )
    banner_image_url: str | None = Field(default=None, max_length=2048)
    headline: str | None = Field(default=None, max_length=255)
    featured_collection_id: uuid.UUID | None = Field(
        default=None, foreign_key="catalog_collections.id", index=True
    )
    # Prepared for future theming (doc 10); not edited in V1.
    primary_color: str | None = Field(default=None, max_length=32)
    background_color: str | None = Field(default=None, max_length=32)
    font_family: str | None = Field(default=None, max_length=255)


class ContentStoreThemeSettings(
    UUIDMixin, TimestampMixin, ContentStoreThemeSettingsBase, table=True
):
    """Per-store theme/appearance settings (exactly one row per store).

    ``store_id`` is unique (1:1 with ``store_stores``), like ``store_settings``.
    Contact/business data (``logo_url``, description, ...) stays in
    ``store_settings`` (Fase 1), not here.
    """

    __tablename__ = "content_store_theme_settings"

    store_id: uuid.UUID = Field(foreign_key="store_stores.id", unique=True, index=True)


class ContentStoreTemplateSettings(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """Per-store x per-template chrome values (schema-driven settings).

    Holds a store's overrides for a template's ``settings_schema`` fields, as a
    JSON object keyed by the schema ``key``. Unique per (store, template) among
    non-deleted rows; resetting = soft-delete (re-selecting falls back to the
    schema defaults). The universal appearance (banner/headline/colors) stays in
    :class:`ContentStoreThemeSettings`; this covers each template's own chrome.
    """

    __tablename__ = "content_store_template_settings"
    __table_args__ = (
        Index(
            "ix_content_store_template_settings_store_template_active",
            "store_id",
            "template_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    template_id: str = Field(foreign_key="content_theme_templates.id", index=True)
    settings: dict[str, object] = Field(default_factory=dict, sa_column=Column(JSON))


class ContentPageBase(SQLModel):
    """Shared editorial page fields (doc 10)."""

    slug: str = Field(max_length=255)
    title: str = Field(max_length=255)
    body: str | None = Field(default=None)
    is_published: bool = Field(default=False)


class ContentPage(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    ContentPageBase,
    table=True,
):
    """An editorial page of a store (e.g. "About").

    ``slug`` is unique among non-deleted pages of the same store (partial unique
    index on ``deleted_at IS NULL``). ``is_published`` gates storefront exposure
    (only published pages are served — ``P3-SF-01``).
    """

    __tablename__ = "content_pages"
    __table_args__ = (
        Index(
            "ix_content_pages_store_slug_active",
            "store_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class ContentMenu(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A store navigation menu, addressed by ``location`` (header/footer)."""

    __tablename__ = "content_menus"
    __table_args__ = (Index("ix_content_menus_store_location", "store_id", "location"),)

    name: str = Field(max_length=255)
    location: MenuLocation = Field(default=MenuLocation.header)


class ContentMenuItem(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """An item of a :class:`ContentMenu`, ordered by ``position``."""

    __tablename__ = "content_menu_items"
    __table_args__ = (
        Index(
            "ix_content_menu_items_store_menu_position",
            "store_id",
            "menu_id",
            "position",
        ),
    )

    menu_id: uuid.UUID = Field(foreign_key="content_menus.id", index=True)
    label: str = Field(max_length=255)
    url: str = Field(max_length=2048)
    position: int = Field(default=0)


class ContentBanner(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, StoreScopedMixin, table=True
):
    """A storefront banner of a store, ordered by ``position``.

    ``is_active`` gates storefront exposure (only active banners are served —
    ``P3-SF-01``).
    """

    __tablename__ = "content_banners"
    __table_args__ = (
        Index("ix_content_banners_store_position", "store_id", "position"),
    )

    image_url: str = Field(max_length=2048)
    link_url: str | None = Field(default=None, max_length=2048)
    title: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    position: int = Field(default=0)
