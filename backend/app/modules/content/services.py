"""Content services: store theme/layout read + write, with cache invalidation.

Panel-facing logic (``P3-CONTENT-02``): list templates, read/apply/edit a store's
theme settings. Writes drop the storefront read caches (doc 13) consumed by
``P3-SF-01``. Store access/permission is enforced by ``require_permission`` in the
routes; these functions operate on the given ``store_id``.
"""

import uuid

from sqlmodel import Session

from app.core.api import AppError
from app.core.cache import cache_delete
from app.db.base import get_datetime_utc
from app.modules.content import repositories
from app.modules.content.models import (
    ContentBanner,
    ContentMenu,
    ContentMenuItem,
    ContentPage,
    ContentStoreTemplateSettings,
    ContentStoreThemeSettings,
    ContentThemeTemplate,
)
from app.modules.content.schemas import (
    ContentBannerCreate,
    ContentBannerUpdate,
    ContentMenuCreate,
    ContentMenuItemCreate,
    ContentMenuItemPublic,
    ContentMenuItemUpdate,
    ContentMenuPublic,
    ContentMenuUpdate,
    ContentPageCreate,
    ContentPageUpdate,
    TemplateSettingsPublic,
    ThemeUpdate,
)

DEFAULT_TEMPLATE_ID = "aurora"
_CACHE_SUFFIXES = ("theme", "home", "settings")


def invalidate_layout_cache(store_id: uuid.UUID) -> None:
    """Drop the storefront read caches affected by a layout change (doc 13).

    Args:
        store_id: Store whose ``store:{id}:theme|home|settings`` keys are dropped.
    """
    for suffix in _CACHE_SUFFIXES:
        cache_delete(f"{store_id}:{suffix}", prefix="store")


def list_templates(*, session: Session) -> list[ContentThemeTemplate]:
    """Return the global theme templates available to a store.

    Args:
        session: Active database session.

    Returns:
        The active templates.
    """
    return repositories.list_active_templates(session=session)


def _require_active_template(session: Session, template_id: str) -> None:
    """Ensure ``template_id`` is an existing, active template.

    Args:
        session: Active database session.
        template_id: Template key to validate.

    Raises:
        AppError: 400 if the template does not exist or is inactive.
    """
    template = session.get(ContentThemeTemplate, template_id)
    if template is None or not template.is_active:
        raise AppError(
            "invalid_template",
            f"Theme template '{template_id}' is not available",
            status_code=400,
        )


def get_or_create_theme_settings(
    *, session: Session, store_id: uuid.UUID
) -> ContentStoreThemeSettings:
    """Return the store's theme settings, creating a default row if absent.

    A store with no settings yet gets one with the default template
    (``aurora``), so the panel and storefront always have a row to read.

    Args:
        session: Active database session.
        store_id: The store whose settings are fetched/created.

    Returns:
        The store's :class:`ContentStoreThemeSettings`.
    """
    settings = repositories.get_store_theme_settings(session=session, store_id=store_id)
    if settings is None:
        settings = ContentStoreThemeSettings(
            store_id=store_id, active_template_id=DEFAULT_TEMPLATE_ID
        )
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


def update_theme_settings(
    *, session: Session, store_id: uuid.UUID, data: ThemeUpdate
) -> ContentStoreThemeSettings:
    """Apply a template and/or edit appearance, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The store being updated.
        data: Partial theme update (only set fields are applied).

    Returns:
        The updated settings row.

    Raises:
        AppError: 400 if ``active_template_id`` is set to an unavailable template.
    """
    fields = data.model_dump(exclude_unset=True)
    new_template = fields.get("active_template_id")
    if new_template is not None:
        _require_active_template(session, new_template)
    settings = get_or_create_theme_settings(session=session, store_id=store_id)
    for key, value in fields.items():
        setattr(settings, key, value)
    session.add(settings)
    session.commit()
    session.refresh(settings)
    invalidate_layout_cache(store_id)
    return settings


def _schema_fields(template: ContentThemeTemplate) -> dict[str, dict[str, object]]:
    """Map a template's ``settings_schema`` to ``{key: field-definition}``.

    Args:
        template: The template whose schema is indexed.

    Returns:
        The schema fields keyed by their ``key`` (empty if no schema).
    """
    schema = template.settings_schema or []
    return {str(field["key"]): field for field in schema if "key" in field}


def resolve_template_settings(
    template: ContentThemeTemplate, overrides: dict[str, object]
) -> dict[str, object]:
    """Merge a template's schema defaults with a store's overrides (override wins).

    Args:
        template: The active template (its schema provides the defaults).
        overrides: The store's saved values (only keys in the schema apply).

    Returns:
        The resolved chrome settings (one entry per schema field).
    """
    fields = _schema_fields(template)
    resolved: dict[str, object] = {
        key: field.get("default") for key, field in fields.items()
    }
    for key, value in overrides.items():
        if key in fields:
            resolved[key] = value
    return resolved


def _validate_settings(
    template: ContentThemeTemplate, settings: dict[str, object]
) -> None:
    """Validate a settings patch against the template's schema.

    Args:
        template: The template whose schema is the contract.
        settings: The proposed overrides.

    Raises:
        AppError: 422 for unknown keys or values violating the field's type/limit.
    """
    fields = _schema_fields(template)
    for key, value in settings.items():
        field = fields.get(key)
        if field is None:
            raise AppError(
                "invalid_setting",
                f"Unknown setting '{key}' for this template",
                status_code=422,
            )
        ftype = field.get("type")
        if ftype == "boolean":
            if not isinstance(value, bool):
                raise AppError(
                    "invalid_setting", f"'{key}' must be a boolean", status_code=422
                )
        elif ftype in ("text", "textarea", "image", "select"):
            if not isinstance(value, str):
                raise AppError(
                    "invalid_setting", f"'{key}' must be a string", status_code=422
                )
            max_length = field.get("max_length")
            if isinstance(max_length, int) and len(value) > max_length:
                raise AppError(
                    "invalid_setting",
                    f"'{key}' exceeds {max_length} characters",
                    status_code=422,
                )
            options = field.get("options")
            if ftype == "select" and isinstance(options, list) and value not in options:
                raise AppError(
                    "invalid_setting", f"'{key}' is not a valid option", status_code=422
                )


def get_active_template_settings(
    *, session: Session, store_id: uuid.UUID
) -> TemplateSettingsPublic:
    """Return the store's saved overrides for its active template.

    Args:
        session: Active database session.
        store_id: The store whose overrides are fetched.

    Returns:
        The active template id + the store's saved overrides (empty if none).
    """
    theme = get_or_create_theme_settings(session=session, store_id=store_id)
    row = repositories.get_store_template_settings(
        session=session, store_id=store_id, template_id=theme.active_template_id
    )
    return TemplateSettingsPublic(
        template_id=theme.active_template_id,
        settings=row.settings if row else {},
    )


def list_customized_templates(*, session: Session, store_id: uuid.UUID) -> list[str]:
    """Return the ids of the templates the store has customized ("my templates").

    Args:
        session: Active database session.
        store_id: The store whose customized templates are listed.

    Returns:
        The template ids that have active per-store settings.
    """
    rows = repositories.list_store_template_settings(session=session, store_id=store_id)
    return [row.template_id for row in rows]


def update_active_template_settings(
    *, session: Session, store_id: uuid.UUID, settings: dict[str, object]
) -> TemplateSettingsPublic:
    """Validate and upsert the active template's overrides, then drop the caches.

    Args:
        session: Active database session.
        store_id: The store being updated.
        settings: The new overrides (validated against the active template's schema).

    Returns:
        The active template id + the saved overrides.

    Raises:
        AppError: 400 if the active template is missing; 422 on invalid values.
    """
    theme = get_or_create_theme_settings(session=session, store_id=store_id)
    template = session.get(ContentThemeTemplate, theme.active_template_id)
    if template is None:
        raise AppError("invalid_template", "Active template not found", status_code=400)
    _validate_settings(template, settings)
    row = repositories.get_store_template_settings(
        session=session, store_id=store_id, template_id=theme.active_template_id
    )
    if row is None:
        row = ContentStoreTemplateSettings(
            store_id=store_id,
            template_id=theme.active_template_id,
            settings=settings,
        )
    else:
        row.settings = settings
    session.add(row)
    session.commit()
    session.refresh(row)
    invalidate_layout_cache(store_id)
    return TemplateSettingsPublic(template_id=row.template_id, settings=row.settings)


def reset_active_template_settings(
    *, session: Session, store_id: uuid.UUID
) -> TemplateSettingsPublic:
    """Soft-delete the active template's overrides (reset to schema defaults).

    Args:
        session: Active database session.
        store_id: The store being reset.

    Returns:
        The active template id with empty overrides.
    """
    theme = get_or_create_theme_settings(session=session, store_id=store_id)
    row = repositories.get_store_template_settings(
        session=session, store_id=store_id, template_id=theme.active_template_id
    )
    if row is not None:
        row.deleted_at = get_datetime_utc()
        session.add(row)
        session.commit()
        invalidate_layout_cache(store_id)
    return TemplateSettingsPublic(template_id=theme.active_template_id, settings={})


def resolve_active_settings(
    *, session: Session, store_id: uuid.UUID, active_template_id: str
) -> dict[str, object]:
    """Return the active template's resolved chrome (defaults ⊕ overrides).

    Used by the public storefront theme. Unknown/inactive template -> empty.

    Args:
        session: Active database session.
        store_id: The store whose overrides apply.
        active_template_id: The template currently active for the store.

    Returns:
        The resolved settings (one entry per schema field), or empty.
    """
    template = session.get(ContentThemeTemplate, active_template_id)
    if template is None:
        return {}
    row = repositories.get_store_template_settings(
        session=session, store_id=store_id, template_id=active_template_id
    )
    overrides = row.settings if row else {}
    return resolve_template_settings(template, overrides)


# --- Editorial pages -------------------------------------------------------


def list_pages(*, session: Session, store_id: uuid.UUID) -> list[ContentPage]:
    """Return the store's active editorial pages (newest first).

    Args:
        session: Active database session.
        store_id: The store whose pages are listed.

    Returns:
        The store's :class:`ContentPage` rows.
    """
    return repositories.list_pages(session=session, store_id=store_id)


def _require_unique_page_slug(
    session: Session,
    store_id: uuid.UUID,
    slug: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> None:
    """Ensure no other active page of the store already uses ``slug``.

    Args:
        session: Active database session.
        store_id: The owning store.
        slug: The slug being claimed.
        exclude_id: A page id to ignore (the one being updated).

    Raises:
        AppError: 409 if another active page already uses the slug.
    """
    existing = repositories.get_page_by_slug(
        session=session, store_id=store_id, slug=slug
    )
    if existing is not None and existing.id != exclude_id:
        raise AppError(
            "duplicate_slug",
            f"A page with slug '{slug}' already exists",
            status_code=409,
        )


def create_page(
    *, session: Session, store_id: uuid.UUID, data: ContentPageCreate
) -> ContentPage:
    """Create an editorial page, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        data: The page payload.

    Returns:
        The created page.

    Raises:
        AppError: 409 if the slug is already used by an active page.
    """
    _require_unique_page_slug(session, store_id, data.slug)
    page = ContentPage(store_id=store_id, **data.model_dump())
    session.add(page)
    session.commit()
    session.refresh(page)
    invalidate_layout_cache(store_id)
    return page


def update_page(
    *,
    session: Session,
    store_id: uuid.UUID,
    page_id: uuid.UUID,
    data: ContentPageUpdate,
) -> ContentPage:
    """Update an editorial page, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        page_id: The page to update.
        data: Partial update (only set fields apply).

    Returns:
        The updated page.

    Raises:
        AppError: 404 if the page is missing; 409 on a slug clash.
    """
    page = repositories.get_page(session=session, store_id=store_id, page_id=page_id)
    if page is None:
        raise AppError("page_not_found", "Page not found", status_code=404)
    fields = data.model_dump(exclude_unset=True)
    new_slug = fields.get("slug")
    if new_slug is not None and new_slug != page.slug:
        _require_unique_page_slug(session, store_id, new_slug, exclude_id=page_id)
    for key, value in fields.items():
        setattr(page, key, value)
    session.add(page)
    session.commit()
    session.refresh(page)
    invalidate_layout_cache(store_id)
    return page


def delete_page(*, session: Session, store_id: uuid.UUID, page_id: uuid.UUID) -> None:
    """Soft-delete an editorial page, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        page_id: The page to delete.

    Raises:
        AppError: 404 if the page is missing.
    """
    page = repositories.get_page(session=session, store_id=store_id, page_id=page_id)
    if page is None:
        raise AppError("page_not_found", "Page not found", status_code=404)
    page.deleted_at = get_datetime_utc()
    session.add(page)
    session.commit()
    invalidate_layout_cache(store_id)


# --- Banners ---------------------------------------------------------------


def list_banners(*, session: Session, store_id: uuid.UUID) -> list[ContentBanner]:
    """Return the store's active banners (ordered by position).

    Args:
        session: Active database session.
        store_id: The store whose banners are listed.

    Returns:
        The store's :class:`ContentBanner` rows.
    """
    return repositories.list_banners(session=session, store_id=store_id)


def create_banner(
    *, session: Session, store_id: uuid.UUID, data: ContentBannerCreate
) -> ContentBanner:
    """Create a storefront banner, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        data: The banner payload.

    Returns:
        The created banner.
    """
    banner = ContentBanner(store_id=store_id, **data.model_dump())
    session.add(banner)
    session.commit()
    session.refresh(banner)
    invalidate_layout_cache(store_id)
    return banner


def update_banner(
    *,
    session: Session,
    store_id: uuid.UUID,
    banner_id: uuid.UUID,
    data: ContentBannerUpdate,
) -> ContentBanner:
    """Update a storefront banner, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        banner_id: The banner to update.
        data: Partial update (only set fields apply).

    Returns:
        The updated banner.

    Raises:
        AppError: 404 if the banner is missing.
    """
    banner = repositories.get_banner(
        session=session, store_id=store_id, banner_id=banner_id
    )
    if banner is None:
        raise AppError("banner_not_found", "Banner not found", status_code=404)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)
    session.add(banner)
    session.commit()
    session.refresh(banner)
    invalidate_layout_cache(store_id)
    return banner


def delete_banner(
    *, session: Session, store_id: uuid.UUID, banner_id: uuid.UUID
) -> None:
    """Soft-delete a storefront banner, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        banner_id: The banner to delete.

    Raises:
        AppError: 404 if the banner is missing.
    """
    banner = repositories.get_banner(
        session=session, store_id=store_id, banner_id=banner_id
    )
    if banner is None:
        raise AppError("banner_not_found", "Banner not found", status_code=404)
    banner.deleted_at = get_datetime_utc()
    session.add(banner)
    session.commit()
    invalidate_layout_cache(store_id)


# --- Menus & items ---------------------------------------------------------


def _menu_public(
    session: Session, store_id: uuid.UUID, menu: ContentMenu
) -> ContentMenuPublic:
    """Assemble a menu's public representation with its ordered items.

    Args:
        session: Active database session.
        store_id: The owning store.
        menu: The menu to represent.

    Returns:
        The :class:`ContentMenuPublic` (menu + items).
    """
    items = repositories.list_menu_items(
        session=session, store_id=store_id, menu_id=menu.id
    )
    return ContentMenuPublic(
        id=menu.id,
        store_id=store_id,
        name=menu.name,
        location=menu.location,
        items=[ContentMenuItemPublic.model_validate(item) for item in items],
    )


def list_menus(*, session: Session, store_id: uuid.UUID) -> list[ContentMenuPublic]:
    """Return the store's active navigation menus with their items.

    Args:
        session: Active database session.
        store_id: The store whose menus are listed.

    Returns:
        The store's menus, each with its ordered items.
    """
    menus = repositories.list_menus(session=session, store_id=store_id)
    return [_menu_public(session, store_id, menu) for menu in menus]


def create_menu(
    *, session: Session, store_id: uuid.UUID, data: ContentMenuCreate
) -> ContentMenuPublic:
    """Create a navigation menu, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        data: The menu payload.

    Returns:
        The created menu (with no items yet).
    """
    menu = ContentMenu(store_id=store_id, **data.model_dump())
    session.add(menu)
    session.commit()
    session.refresh(menu)
    invalidate_layout_cache(store_id)
    return _menu_public(session, store_id, menu)


def update_menu(
    *,
    session: Session,
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    data: ContentMenuUpdate,
) -> ContentMenuPublic:
    """Update a navigation menu, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        menu_id: The menu to update.
        data: Partial update (only set fields apply).

    Returns:
        The updated menu with its items.

    Raises:
        AppError: 404 if the menu is missing.
    """
    menu = repositories.get_menu(session=session, store_id=store_id, menu_id=menu_id)
    if menu is None:
        raise AppError("menu_not_found", "Menu not found", status_code=404)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(menu, key, value)
    session.add(menu)
    session.commit()
    session.refresh(menu)
    invalidate_layout_cache(store_id)
    return _menu_public(session, store_id, menu)


def delete_menu(*, session: Session, store_id: uuid.UUID, menu_id: uuid.UUID) -> None:
    """Soft-delete a menu and its items, then invalidate the read caches.

    Deleting the menu also soft-deletes its items, so no orphan items remain.

    Args:
        session: Active database session.
        store_id: The owning store.
        menu_id: The menu to delete.

    Raises:
        AppError: 404 if the menu is missing.
    """
    menu = repositories.get_menu(session=session, store_id=store_id, menu_id=menu_id)
    if menu is None:
        raise AppError("menu_not_found", "Menu not found", status_code=404)
    now = get_datetime_utc()
    menu.deleted_at = now
    session.add(menu)
    for item in repositories.list_menu_items(
        session=session, store_id=store_id, menu_id=menu_id
    ):
        item.deleted_at = now
        session.add(item)
    session.commit()
    invalidate_layout_cache(store_id)


def add_menu_item(
    *,
    session: Session,
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    data: ContentMenuItemCreate,
) -> ContentMenuItemPublic:
    """Add an item to a menu, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        menu_id: The menu the item belongs to.
        data: The item payload.

    Returns:
        The created menu item.

    Raises:
        AppError: 404 if the menu is missing (no orphan items are created).
    """
    menu = repositories.get_menu(session=session, store_id=store_id, menu_id=menu_id)
    if menu is None:
        raise AppError("menu_not_found", "Menu not found", status_code=404)
    item = ContentMenuItem(store_id=store_id, menu_id=menu_id, **data.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    invalidate_layout_cache(store_id)
    return ContentMenuItemPublic.model_validate(item)


def update_menu_item(
    *,
    session: Session,
    store_id: uuid.UUID,
    item_id: uuid.UUID,
    data: ContentMenuItemUpdate,
) -> ContentMenuItemPublic:
    """Update a menu item, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        item_id: The item to update.
        data: Partial update (only set fields apply).

    Returns:
        The updated menu item.

    Raises:
        AppError: 404 if the item is missing.
    """
    item = repositories.get_menu_item(
        session=session, store_id=store_id, item_id=item_id
    )
    if item is None:
        raise AppError("menu_item_not_found", "Menu item not found", status_code=404)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    invalidate_layout_cache(store_id)
    return ContentMenuItemPublic.model_validate(item)


def delete_menu_item(
    *, session: Session, store_id: uuid.UUID, item_id: uuid.UUID
) -> None:
    """Soft-delete a menu item, then invalidate the read caches.

    Args:
        session: Active database session.
        store_id: The owning store.
        item_id: The item to delete.

    Raises:
        AppError: 404 if the item is missing.
    """
    item = repositories.get_menu_item(
        session=session, store_id=store_id, item_id=item_id
    )
    if item is None:
        raise AppError("menu_item_not_found", "Menu item not found", status_code=404)
    item.deleted_at = get_datetime_utc()
    session.add(item)
    session.commit()
    invalidate_layout_cache(store_id)
