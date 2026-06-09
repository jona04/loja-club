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
CANONICAL_TEMPLATES: list[dict[str, str]] = [
    {
        "id": "classic",
        "name": "Clássico",
        "description": "Layout tradicional, com foco no catálogo.",
    },
    {
        "id": "modern",
        "name": "Moderno",
        "description": "Layout amplo, com destaque visual.",
    },
]


def seed_content_templates(*, session: Session) -> None:
    """Seed the global storefront theme templates (idempotent).

    Inserts any canonical template (``classic``/``modern``) that is missing;
    existing rows are left untouched. Safe to run repeatedly — used by prestart
    and the test fixtures.

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
                )
            )
            created = True
    if created:
        session.commit()
