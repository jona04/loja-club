"""Content repositories: seeding and queries for the content module."""

import json
import uuid
from pathlib import Path

from sqlmodel import Session, col, select

from app.core import storage
from app.modules.content.models import (
    ContentBanner,
    ContentMenu,
    ContentMenuItem,
    ContentPage,
    ContentStoreTemplateSettings,
    ContentStoreThemeSettings,
    ContentThemeTemplate,
)

_TEMPLATES_DIR = (
    Path(__file__).resolve().parents[4] / "frontend-storefront" / "templates"
)


def _load_settings_schema(template_id: str) -> list[dict[str, object]] | None:
    """Load a template's editable-field manifest from its ``settings-schema.json``.

    Args:
        template_id: The template id (folder under the storefront templates).

    Returns:
        The parsed schema, or ``None`` when the file is absent.
    """
    path = _TEMPLATES_DIR / template_id / "settings-schema.json"
    if not path.is_file():
        return None
    schema: list[dict[str, object]] = json.loads(path.read_text(encoding="utf-8"))
    return schema


def list_active_templates(*, session: Session) -> list[ContentThemeTemplate]:
    """Return the global theme templates available for selection.

    Args:
        session: Active database session.

    Returns:
        The active templates (e.g. ``classic``/``modern``).
    """
    return list(
        session.exec(
            select(ContentThemeTemplate).where(
                col(ContentThemeTemplate.is_active).is_(True)
            )
        ).all()
    )


def get_store_theme_settings(
    *, session: Session, store_id: uuid.UUID
) -> ContentStoreThemeSettings | None:
    """Return a store's theme settings row, or ``None`` if it has none yet.

    Args:
        session: Active database session.
        store_id: The store whose settings are fetched.

    Returns:
        The store's :class:`ContentStoreThemeSettings`, or ``None``.
    """
    return session.exec(
        select(ContentStoreThemeSettings).where(
            ContentStoreThemeSettings.store_id == store_id
        )
    ).first()


def get_store_template_settings(
    *, session: Session, store_id: uuid.UUID, template_id: str
) -> ContentStoreTemplateSettings | None:
    """Return a store's active overrides row for a template, or ``None``.

    Args:
        session: Active database session.
        store_id: The store whose overrides are fetched.
        template_id: The template the overrides belong to.

    Returns:
        The active :class:`ContentStoreTemplateSettings` row, or ``None``.
    """
    return session.exec(
        select(ContentStoreTemplateSettings).where(
            ContentStoreTemplateSettings.store_id == store_id,
            ContentStoreTemplateSettings.template_id == template_id,
            col(ContentStoreTemplateSettings.deleted_at).is_(None),
        )
    ).first()


def list_store_template_settings(
    *, session: Session, store_id: uuid.UUID
) -> list[ContentStoreTemplateSettings]:
    """Return all active per-template settings rows of a store.

    Args:
        session: Active database session.
        store_id: The store whose customized templates are listed.

    Returns:
        The store's active :class:`ContentStoreTemplateSettings` rows.
    """
    return list(
        session.exec(
            select(ContentStoreTemplateSettings).where(
                ContentStoreTemplateSettings.store_id == store_id,
                col(ContentStoreTemplateSettings.deleted_at).is_(None),
            )
        ).all()
    )


def list_pages(*, session: Session, store_id: uuid.UUID) -> list[ContentPage]:
    """Return a store's active editorial pages, newest first.

    Args:
        session: Active database session.
        store_id: The store whose pages are listed.

    Returns:
        The store's non-deleted :class:`ContentPage` rows.
    """
    return list(
        session.exec(
            select(ContentPage)
            .where(
                ContentPage.store_id == store_id,
                col(ContentPage.deleted_at).is_(None),
            )
            .order_by(col(ContentPage.created_at).desc())
        ).all()
    )


def get_page(
    *, session: Session, store_id: uuid.UUID, page_id: uuid.UUID
) -> ContentPage | None:
    """Return a store's active page by id, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        page_id: The page id.

    Returns:
        The :class:`ContentPage`, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(ContentPage).where(
            ContentPage.id == page_id,
            ContentPage.store_id == store_id,
            col(ContentPage.deleted_at).is_(None),
        )
    ).first()


def get_page_by_slug(
    *, session: Session, store_id: uuid.UUID, slug: str
) -> ContentPage | None:
    """Return a store's active page by slug, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        slug: The page slug (unique among active pages of the store).

    Returns:
        The :class:`ContentPage`, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(ContentPage).where(
            ContentPage.store_id == store_id,
            ContentPage.slug == slug,
            col(ContentPage.deleted_at).is_(None),
        )
    ).first()


def list_banners(*, session: Session, store_id: uuid.UUID) -> list[ContentBanner]:
    """Return a store's active banners, ordered by ``position``.

    Args:
        session: Active database session.
        store_id: The store whose banners are listed.

    Returns:
        The store's non-deleted :class:`ContentBanner` rows.
    """
    return list(
        session.exec(
            select(ContentBanner)
            .where(
                ContentBanner.store_id == store_id,
                col(ContentBanner.deleted_at).is_(None),
            )
            .order_by(col(ContentBanner.position))
        ).all()
    )


def get_banner(
    *, session: Session, store_id: uuid.UUID, banner_id: uuid.UUID
) -> ContentBanner | None:
    """Return a store's active banner by id, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        banner_id: The banner id.

    Returns:
        The :class:`ContentBanner`, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(ContentBanner).where(
            ContentBanner.id == banner_id,
            ContentBanner.store_id == store_id,
            col(ContentBanner.deleted_at).is_(None),
        )
    ).first()


def list_menus(*, session: Session, store_id: uuid.UUID) -> list[ContentMenu]:
    """Return a store's active navigation menus.

    Args:
        session: Active database session.
        store_id: The store whose menus are listed.

    Returns:
        The store's non-deleted :class:`ContentMenu` rows.
    """
    return list(
        session.exec(
            select(ContentMenu).where(
                ContentMenu.store_id == store_id,
                col(ContentMenu.deleted_at).is_(None),
            )
        ).all()
    )


def get_menu(
    *, session: Session, store_id: uuid.UUID, menu_id: uuid.UUID
) -> ContentMenu | None:
    """Return a store's active menu by id, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        menu_id: The menu id.

    Returns:
        The :class:`ContentMenu`, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(ContentMenu).where(
            ContentMenu.id == menu_id,
            ContentMenu.store_id == store_id,
            col(ContentMenu.deleted_at).is_(None),
        )
    ).first()


def list_menu_items(
    *, session: Session, store_id: uuid.UUID, menu_id: uuid.UUID
) -> list[ContentMenuItem]:
    """Return a menu's active items, ordered by ``position``.

    Args:
        session: Active database session.
        store_id: The owning store.
        menu_id: The menu whose items are listed.

    Returns:
        The menu's non-deleted :class:`ContentMenuItem` rows.
    """
    return list(
        session.exec(
            select(ContentMenuItem)
            .where(
                ContentMenuItem.store_id == store_id,
                ContentMenuItem.menu_id == menu_id,
                col(ContentMenuItem.deleted_at).is_(None),
            )
            .order_by(col(ContentMenuItem.position))
        ).all()
    )


def get_menu_item(
    *, session: Session, store_id: uuid.UUID, item_id: uuid.UUID
) -> ContentMenuItem | None:
    """Return a store's active menu item by id, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        item_id: The menu item id.

    Returns:
        The :class:`ContentMenuItem`, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(ContentMenuItem).where(
            ContentMenuItem.id == item_id,
            ContentMenuItem.store_id == store_id,
            col(ContentMenuItem.deleted_at).is_(None),
        )
    ).first()


# The storefront templates shipped in V1. Authoritative for the seed. The
# thumbnail (``preview.png`` per template) is served from the CDN; the seed
# derives ``preview_image_url`` from its key (the file is uploaded by
# ``import_assets.import_template_thumbnail``).
CANONICAL_TEMPLATES: list[dict[str, str]] = [
    {
        "id": "aurora",
        "name": "Aurora",
        "description": "Premium minimalista: home curada com destaques.",
    },
    {
        "id": "bazar",
        "name": "Bazar",
        "description": "Vibrante marketplace: home por seções de categoria.",
    },
    {
        "id": "studio",
        "name": "Studio",
        "description": "Catálogo com sidebar de categorias e filtros.",
    },
]


def seed_content_templates(*, session: Session) -> None:
    """Seed the global storefront theme templates (idempotent).

    Inserts any canonical template (``aurora``/``bazar``/``studio``) that is
    missing; existing rows are left untouched. Safe to run repeatedly — used by
    prestart and the test fixtures.

    Args:
        session: Active database session used to query and seed.
    """
    existing = {t.id: t for t in session.exec(select(ContentThemeTemplate)).all()}
    changed = False
    for template in CANONICAL_TEMPLATES:
        schema = _load_settings_schema(template["id"])
        preview_url = storage.public_url(
            f"public/templates/{template['id']}/preview.png"
        )
        row = existing.get(template["id"])
        if row is None:
            session.add(
                ContentThemeTemplate(
                    id=template["id"],
                    name=template["name"],
                    description=template["description"],
                    preview_image_url=preview_url,
                    settings_schema=schema,
                )
            )
            changed = True
        elif row.settings_schema != schema or row.preview_image_url != preview_url:
            row.settings_schema = schema
            row.preview_image_url = preview_url
            session.add(row)
            changed = True
    if changed:
        session.commit()
