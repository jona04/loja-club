"""Integration tests for the seeded permission catalog and role map."""

from sqlmodel import Session, col, select

from app.modules.stores.models import (
    StorePermission,
    StoreRole,
    StoreRolePermission,
)
from app.modules.stores.permissions import PERMISSIONS, ROLE_PERMISSIONS
from app.modules.stores.repositories import seed_store_permissions


def _role_permission_keys(db: Session, role_key: str) -> set[str]:
    role = db.exec(select(StoreRole).where(StoreRole.key == role_key)).one()
    keys = db.exec(
        select(StorePermission.key)
        .join(
            StoreRolePermission,
            col(StoreRolePermission.permission_id) == col(StorePermission.id),
        )
        .where(StoreRolePermission.role_id == role.id)
    ).all()
    return set(keys)


def test_catalog_seeded(db: Session) -> None:
    keys = {p.key for p in db.exec(select(StorePermission)).all()}
    assert keys == set(PERMISSIONS)


def test_module_derived_from_key(db: Session) -> None:
    perm = db.exec(
        select(StorePermission).where(StorePermission.key == "catalog.product.view")
    ).one()
    assert perm.module == "catalog"


def test_owner_grants_full_catalog(db: Session) -> None:
    assert _role_permission_keys(db, "owner") == set(PERMISSIONS)


def test_support_grants_match_map(db: Session) -> None:
    assert _role_permission_keys(db, "support") == ROLE_PERMISSIONS["support"]


def test_seed_is_idempotent(db: Session) -> None:
    before = len(db.exec(select(StoreRolePermission)).all())
    seed_store_permissions(session=db)
    after = len(db.exec(select(StoreRolePermission)).all())
    assert before == after
