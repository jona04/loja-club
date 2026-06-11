"""HTTP routes for the content module (panel), under ``/stores/{store_id}/layout``.

Gated by ``layout.*`` permissions (doc 08); writes invalidate the storefront read
caches consumed by ``P3-SF-01``. Public storefront endpoints live in ``P3-SF-01``.
"""

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.modules.content import services
from app.modules.content.models import (
    ContentBanner,
    ContentPage,
    ContentStoreThemeSettings,
    ContentThemeTemplate,
)
from app.modules.content.schemas import (
    ContentBannerCreate,
    ContentBannerPublic,
    ContentBannerUpdate,
    ContentMenuCreate,
    ContentMenuItemCreate,
    ContentMenuItemPublic,
    ContentMenuItemUpdate,
    ContentMenuPublic,
    ContentMenuUpdate,
    ContentPageCreate,
    ContentPagePublic,
    ContentPageUpdate,
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


# --- Editorial pages -------------------------------------------------------


@router.get(
    "/pages",
    response_model=list[ContentPagePublic],
    dependencies=[Depends(require_permission("layout.view"))],
)
def list_pages(store_id: uuid.UUID, session: SessionDep) -> list[ContentPage]:
    """List the store's editorial pages."""
    return services.list_pages(session=session, store_id=store_id)


@router.post(
    "/pages",
    response_model=ContentPagePublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def create_page(
    store_id: uuid.UUID, data: ContentPageCreate, session: SessionDep
) -> ContentPage:
    """Create an editorial page; invalidates the read caches."""
    return services.create_page(session=session, store_id=store_id, data=data)


@router.patch(
    "/pages/{page_id}",
    response_model=ContentPagePublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def update_page(
    store_id: uuid.UUID,
    page_id: uuid.UUID,
    data: ContentPageUpdate,
    session: SessionDep,
) -> ContentPage:
    """Update an editorial page; invalidates the read caches."""
    return services.update_page(
        session=session, store_id=store_id, page_id=page_id, data=data
    )


@router.delete(
    "/pages/{page_id}",
    status_code=204,
    dependencies=[Depends(require_permission("layout.update"))],
)
def delete_page(store_id: uuid.UUID, page_id: uuid.UUID, session: SessionDep) -> None:
    """Soft-delete an editorial page; invalidates the read caches."""
    services.delete_page(session=session, store_id=store_id, page_id=page_id)


# --- Banners ---------------------------------------------------------------


@router.get(
    "/banners",
    response_model=list[ContentBannerPublic],
    dependencies=[Depends(require_permission("layout.view"))],
)
def list_banners(store_id: uuid.UUID, session: SessionDep) -> list[ContentBanner]:
    """List the store's banners (ordered by position)."""
    return services.list_banners(session=session, store_id=store_id)


@router.post(
    "/banners",
    response_model=ContentBannerPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def create_banner(
    store_id: uuid.UUID, data: ContentBannerCreate, session: SessionDep
) -> ContentBanner:
    """Create a storefront banner; invalidates the read caches."""
    return services.create_banner(session=session, store_id=store_id, data=data)


@router.patch(
    "/banners/{banner_id}",
    response_model=ContentBannerPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def update_banner(
    store_id: uuid.UUID,
    banner_id: uuid.UUID,
    data: ContentBannerUpdate,
    session: SessionDep,
) -> ContentBanner:
    """Update a storefront banner; invalidates the read caches."""
    return services.update_banner(
        session=session, store_id=store_id, banner_id=banner_id, data=data
    )


@router.delete(
    "/banners/{banner_id}",
    status_code=204,
    dependencies=[Depends(require_permission("layout.update"))],
)
def delete_banner(
    store_id: uuid.UUID, banner_id: uuid.UUID, session: SessionDep
) -> None:
    """Soft-delete a storefront banner; invalidates the read caches."""
    services.delete_banner(session=session, store_id=store_id, banner_id=banner_id)


# --- Menus & items ---------------------------------------------------------


@router.get(
    "/menus",
    response_model=list[ContentMenuPublic],
    dependencies=[Depends(require_permission("layout.view"))],
)
def list_menus(store_id: uuid.UUID, session: SessionDep) -> list[ContentMenuPublic]:
    """List the store's navigation menus with their items."""
    return services.list_menus(session=session, store_id=store_id)


@router.post(
    "/menus",
    response_model=ContentMenuPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def create_menu(
    store_id: uuid.UUID, data: ContentMenuCreate, session: SessionDep
) -> ContentMenuPublic:
    """Create a navigation menu; invalidates the read caches."""
    return services.create_menu(session=session, store_id=store_id, data=data)


@router.patch(
    "/menus/{menu_id}",
    response_model=ContentMenuPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def update_menu(
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    data: ContentMenuUpdate,
    session: SessionDep,
) -> ContentMenuPublic:
    """Update a navigation menu; invalidates the read caches."""
    return services.update_menu(
        session=session, store_id=store_id, menu_id=menu_id, data=data
    )


@router.delete(
    "/menus/{menu_id}",
    status_code=204,
    dependencies=[Depends(require_permission("layout.update"))],
)
def delete_menu(store_id: uuid.UUID, menu_id: uuid.UUID, session: SessionDep) -> None:
    """Soft-delete a menu and its items; invalidates the read caches."""
    services.delete_menu(session=session, store_id=store_id, menu_id=menu_id)


@router.post(
    "/menus/{menu_id}/items",
    response_model=ContentMenuItemPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def add_menu_item(
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    data: ContentMenuItemCreate,
    session: SessionDep,
) -> ContentMenuItemPublic:
    """Add an item to a menu; invalidates the read caches."""
    return services.add_menu_item(
        session=session, store_id=store_id, menu_id=menu_id, data=data
    )


@router.patch(
    "/menu-items/{item_id}",
    response_model=ContentMenuItemPublic,
    dependencies=[Depends(require_permission("layout.update"))],
)
def update_menu_item(
    store_id: uuid.UUID,
    item_id: uuid.UUID,
    data: ContentMenuItemUpdate,
    session: SessionDep,
) -> ContentMenuItemPublic:
    """Update a menu item; invalidates the read caches."""
    return services.update_menu_item(
        session=session, store_id=store_id, item_id=item_id, data=data
    )


@router.delete(
    "/menu-items/{item_id}",
    status_code=204,
    dependencies=[Depends(require_permission("layout.update"))],
)
def delete_menu_item(
    store_id: uuid.UUID, item_id: uuid.UUID, session: SessionDep
) -> None:
    """Soft-delete a menu item; invalidates the read caches."""
    services.delete_menu_item(session=session, store_id=store_id, item_id=item_id)
