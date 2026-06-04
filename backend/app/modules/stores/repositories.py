"""Data access and seeding for the stores module."""

from sqlmodel import Session, select

from app.modules.stores.models import (
    StorePermission,
    StoreRole,
    StoreRolePermission,
)
from app.modules.stores.permissions import PERMISSIONS, ROLE_PERMISSIONS

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


def seed_store_permissions(session: Session) -> None:
    """Seed the permission catalog and the role->permission map, idempotently.

    Requires the roles to be seeded first (``seed_store_roles``).

    Args:
        session: Active database session.
    """
    existing_perms = {p.key for p in session.exec(select(StorePermission)).all()}
    new_perms = [
        StorePermission(key=key, module=key.split(".", 1)[0])
        for key in PERMISSIONS
        if key not in existing_perms
    ]
    if new_perms:
        session.add_all(new_perms)
        session.commit()

    perm_ids = {p.key: p.id for p in session.exec(select(StorePermission)).all()}
    role_ids = {r.key: r.id for r in session.exec(select(StoreRole)).all()}
    existing_grants = {
        (g.role_id, g.permission_id)
        for g in session.exec(select(StoreRolePermission)).all()
    }
    new_grants: list[StoreRolePermission] = []
    for role_key, perm_keys in ROLE_PERMISSIONS.items():
        role_id = role_ids.get(role_key)
        if role_id is None:
            continue
        for perm_key in perm_keys:
            perm_id = perm_ids.get(perm_key)
            if perm_id is not None and (role_id, perm_id) not in existing_grants:
                new_grants.append(
                    StoreRolePermission(role_id=role_id, permission_id=perm_id)
                )
    if new_grants:
        session.add_all(new_grants)
        session.commit()
