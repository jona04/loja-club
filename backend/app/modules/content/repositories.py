"""Content repositories: seeding and queries for the content module."""

import uuid

from sqlmodel import Session, col, select

from app.modules.content.models import ContentStoreThemeSettings, ContentThemeTemplate


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


# The storefront templates shipped in V1 (doc 10). Authoritative for the seed.
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
    existing = {t.id for t in session.exec(select(ContentThemeTemplate)).all()}
    created = False
    for template in CANONICAL_TEMPLATES:
        if template["id"] not in existing:
            session.add(
                ContentThemeTemplate(
                    id=template["id"],
                    name=template["name"],
                    description=template["description"],
                    preview_image_url=template["preview_image_url"],
                )
            )
            created = True
    if created:
        session.commit()
