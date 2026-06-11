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
    ContentStoreTemplateSettings,
    ContentStoreThemeSettings,
    ContentThemeTemplate,
)
from app.modules.content.schemas import (
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
