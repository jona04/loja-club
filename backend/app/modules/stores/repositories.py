"""Data access and seeding for the stores module."""

from sqlmodel import Session, select

from app.modules.stores.models import StoreRole

# Canonical fixed set of store roles (doc 08) — single source for seeding.
STORE_ROLES: list[tuple[str, str]] = [
    ("owner", "Owner"),
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("support", "Support"),
    ("catalog", "Catalog"),
    ("marketing", "Marketing"),
]


def seed_store_roles(session: Session) -> None:
    """Seed the fixed set of store roles, idempotently.

    Args:
        session: Active database session.
    """
    existing = {role.key for role in session.exec(select(StoreRole)).all()}
    new_roles = [
        StoreRole(key=key, name=name)
        for key, name in STORE_ROLES
        if key not in existing
    ]
    if new_roles:
        session.add_all(new_roles)
        session.commit()
