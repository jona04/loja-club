"""Content repositories: seeding and queries for the content module."""

import json
import uuid
from pathlib import Path

from sqlmodel import Session, col, select

from app.modules.content.models import (
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


# The storefront templates shipped in V1. Authoritative for the seed.
# ``preview_image_url`` is served by the dashboard (hardcoded; CloudFront later).
CANONICAL_TEMPLATES: list[dict[str, str]] = [
    {
        "id": "aurora",
        "name": "Aurora",
        "description": "Premium minimalista: home curada com destaques.",
        "preview_image_url": "/templates/aurora_preview.png",
    },
    {
        "id": "bazar",
        "name": "Bazar",
        "description": "Vibrante marketplace: home por seções de categoria.",
        "preview_image_url": "/templates/bazar_preview.png",
    },
    {
        "id": "studio",
        "name": "Studio",
        "description": "Catálogo com sidebar de categorias e filtros.",
        "preview_image_url": "/templates/studio_preview.png",
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
        row = existing.get(template["id"])
        if row is None:
            session.add(
                ContentThemeTemplate(
                    id=template["id"],
                    name=template["name"],
                    description=template["description"],
                    preview_image_url=template["preview_image_url"],
                    settings_schema=schema,
                )
            )
            changed = True
        elif row.settings_schema != schema:
            row.settings_schema = schema
            session.add(row)
            changed = True
    if changed:
        session.commit()
