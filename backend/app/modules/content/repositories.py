"""Content repositories: seeding and queries for the content module."""

from sqlmodel import Session, select

from app.modules.content.models import ContentThemeTemplate

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
