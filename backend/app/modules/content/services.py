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
from app.modules.content import repositories
from app.modules.content.models import ContentStoreThemeSettings, ContentThemeTemplate
from app.modules.content.schemas import StoreThemeSettingsPublic, ThemeUpdate

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
    (``classic``), so the panel and storefront always have a row to read.

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


def preview_theme_settings(
    *, session: Session, store_id: uuid.UUID, template_id: str
) -> StoreThemeSettingsPublic:
    """Return the store's settings as they would look with ``template_id`` active.

    Does not persist the change — only the response carries the previewed
    template, so the panel can render it before applying.

    Args:
        session: Active database session.
        store_id: The store to preview.
        template_id: The template to preview.

    Returns:
        The store's settings with ``active_template_id`` overridden.

    Raises:
        AppError: 400 if ``template_id`` is not an available template.
    """
    _require_active_template(session, template_id)
    settings = get_or_create_theme_settings(session=session, store_id=store_id)
    return StoreThemeSettingsPublic(
        id=settings.id,
        store_id=settings.store_id,
        active_template_id=template_id,
        banner_image_url=settings.banner_image_url,
        headline=settings.headline,
        featured_collection_id=settings.featured_collection_id,
        primary_color=settings.primary_color,
        background_color=settings.background_color,
        font_family=settings.font_family,
    )
