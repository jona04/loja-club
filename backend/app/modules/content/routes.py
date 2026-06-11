"""HTTP routes for the content module (panel), under ``/stores/{store_id}/layout``.

Gated by ``layout.*`` permissions (doc 08); writes invalidate the storefront read
caches consumed by ``P3-SF-01``. Public storefront endpoints live in ``P3-SF-01``.
"""

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.modules.content import services
from app.modules.content.models import ContentStoreThemeSettings, ContentThemeTemplate
from app.modules.content.schemas import (
    StoreThemeSettingsPublic,
    TemplateSettingsPublic,
    TemplateSettingsUpdate,
    ThemeTemplatePublic,
    ThemeUpdate,
)
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/stores/{store_id}/layout", tags=["content"])


@router.get(
    "/templates",
    response_model=list[ThemeTemplatePublic],
    dependencies=[Depends(require_permission("layout.view"))],
)
def list_templates(session: SessionDep) -> list[ContentThemeTemplate]:
    """List the global theme templates available to the store.

    ``store_id`` is consumed by the ``require_permission`` dependency (path); the
    templates themselves are global, so the handler does not need it.
    """
    return services.list_templates(session=session)


@router.get(
    "",
    response_model=StoreThemeSettingsPublic,
    dependencies=[Depends(require_permission("layout.view"))],
)
def get_layout(store_id: uuid.UUID, session: SessionDep) -> ContentStoreThemeSettings:
    """Return the store's theme settings (creating a default row if absent)."""
    return services.get_or_create_theme_settings(session=session, store_id=store_id)


@router.get(
    "/preview/{template_id}",
    response_model=StoreThemeSettingsPublic,
    dependencies=[Depends(require_permission("layout.preview"))],
)
def preview_layout(
    store_id: uuid.UUID, template_id: str, session: SessionDep
) -> StoreThemeSettingsPublic:
    """Return the store's settings as they would look with ``template_id`` active."""
    return services.preview_theme_settings(
        session=session, store_id=store_id, template_id=template_id
    )


@router.patch(
    "",
    response_model=StoreThemeSettingsPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def update_layout(
    store_id: uuid.UUID, data: ThemeUpdate, session: SessionDep
) -> ContentStoreThemeSettings:
    """Apply a template and/or edit appearance; invalidates the read caches."""
    return services.update_theme_settings(session=session, store_id=store_id, data=data)


@router.get(
    "/settings",
    response_model=TemplateSettingsPublic,
    dependencies=[Depends(require_permission("layout.view"))],
)
def get_layout_settings(
    store_id: uuid.UUID, session: SessionDep
) -> TemplateSettingsPublic:
    """Return the store's saved chrome overrides for its active template."""
    return services.get_active_template_settings(session=session, store_id=store_id)


@router.get(
    "/settings/mine",
    response_model=list[str],
    dependencies=[Depends(require_permission("layout.view"))],
)
def list_my_templates(store_id: uuid.UUID, session: SessionDep) -> list[str]:
    """Return the ids of templates the store has customized ("my templates")."""
    return services.list_customized_templates(session=session, store_id=store_id)


@router.patch(
    "/settings",
    response_model=TemplateSettingsPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def update_layout_settings(
    store_id: uuid.UUID, data: TemplateSettingsUpdate, session: SessionDep
) -> TemplateSettingsPublic:
    """Validate + save the active template's chrome overrides; drops the caches."""
    return services.update_active_template_settings(
        session=session, store_id=store_id, settings=data.settings
    )


@router.delete(
    "/settings",
    response_model=TemplateSettingsPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def reset_layout_settings(
    store_id: uuid.UUID, session: SessionDep
) -> TemplateSettingsPublic:
    """Reset (soft-delete) the active template's overrides to the schema defaults."""
    return services.reset_active_template_settings(session=session, store_id=store_id)
