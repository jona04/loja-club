"""Data access and seeding for the stores module."""

import uuid
from collections.abc import Sequence

from sqlmodel import Session, col, func, select

from app.modules.accounts.models import User
from app.modules.stores.enums import MembershipStatus
from app.modules.stores.models import (
    Store,
    StoreMember,
    StorePermission,
    StoreRole,
    StoreRolePermission,
)
from app.modules.stores.permissions import PERMISSIONS, ROLE_PERMISSIONS
from app.modules.stores.schemas import StoreMemberPublic

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


def get_role_by_key(*, session: Session, key: str) -> StoreRole | None:
    """Return the seeded role with ``key``, or None."""
    return session.exec(select(StoreRole).where(StoreRole.key == key)).first()


def list_my_stores(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[Sequence[Store], int]:
    """Return the active, non-deleted stores the user is an active member of."""
    base = (
        select(Store)
        .join(StoreMember, col(StoreMember.store_id) == col(Store.id))
        .where(
            StoreMember.user_id == user_id,
            StoreMember.status == MembershipStatus.active,
            col(StoreMember.deleted_at).is_(None),
            col(Store.deleted_at).is_(None),
        )
    )
    count = session.exec(select(func.count()).select_from(base.subquery())).one()
    stores = session.exec(
        base.order_by(col(Store.created_at).desc()).offset(skip).limit(limit)
    ).all()
    return stores, count


def get_membership(
    *, session: Session, store_id: uuid.UUID, user_id: uuid.UUID
) -> StoreMember | None:
    """Return the user's non-deleted membership in the store, or None."""
    return session.exec(
        select(StoreMember).where(
            StoreMember.store_id == store_id,
            StoreMember.user_id == user_id,
            col(StoreMember.deleted_at).is_(None),
        )
    ).first()


def list_members(
    *, session: Session, store_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[StoreMemberPublic], int]:
    """Return the store's non-deleted members (with email + role key)."""
    base = (
        select(StoreMember, User.email, StoreRole.key)
        .join(User, col(User.id) == col(StoreMember.user_id))
        .join(StoreRole, col(StoreRole.id) == col(StoreMember.role_id))
        .where(
            StoreMember.store_id == store_id,
            col(StoreMember.deleted_at).is_(None),
        )
    )
    count = session.exec(select(func.count()).select_from(base.subquery())).one()
    rows = session.exec(base.offset(skip).limit(limit)).all()
    members = [
        StoreMemberPublic(
            id=member.id,
            user_id=member.user_id,
            email=email,
            role=role_key,
            status=member.status,
        )
        for member, email, role_key in rows
    ]
    return members, count


def role_permission_keys(*, session: Session, role_id: uuid.UUID) -> list[str]:
    """Return the permission keys granted to ``role_id``."""
    keys = session.exec(
        select(StorePermission.key)
        .join(
            StoreRolePermission,
            col(StoreRolePermission.permission_id) == col(StorePermission.id),
        )
        .where(StoreRolePermission.role_id == role_id)
    ).all()
    return list(keys)
