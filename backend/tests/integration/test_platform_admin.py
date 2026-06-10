"""Integration tests for the platform_admin foundation (P4-PLAT-01).

Covers the global ``platform.*`` role->permission map (doc 08), the
``require_platform_permission`` dependency, the bootstrap superuser becoming a
platform owner (seed), the migrated ``get_current_active_superuser`` gate and the
minimal ``audit_logs`` recording.
"""

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_active_superuser
from app.core.api import AppError
from app.core.config import settings
from app.modules.accounts import repositories
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate
from app.modules.audit.models import AuditLog
from app.modules.audit.services import record_audit
from app.modules.platform_admin.deps import require_platform_permission
from app.modules.platform_admin.enums import PlatformRole
from app.modules.platform_admin.permissions import PLATFORM_PERMISSIONS
from app.modules.platform_admin.repositories import (
    assign_platform_role,
    user_platform_permissions,
    user_platform_roles,
)
from tests.utils.utils import random_email, random_lower_string


def _user(db: Session) -> User:
    return repositories.create_user(
        session=db,
        user_create=UserCreate(email=random_email(), password=random_lower_string()),
    )


def test_owner_holds_full_catalog(db: Session) -> None:
    user = _user(db)
    assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_owner.value
    )
    assert user_platform_permissions(session=db, user_id=user.id) == set(
        PLATFORM_PERMISSIONS
    )


def test_finance_holds_limited_set(db: Session) -> None:
    user = _user(db)
    assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_finance.value
    )
    perms = user_platform_permissions(session=db, user_id=user.id)
    assert perms == {
        "platform.stores.view",
        "platform.plans.view",
        "platform.plans.update",
        "platform.audit.view",
    }
    assert "platform.stores.block" not in perms


def test_no_role_has_no_permissions(db: Session) -> None:
    user = _user(db)
    assert user_platform_permissions(session=db, user_id=user.id) == set()


def test_assign_platform_role_is_idempotent(db: Session) -> None:
    user = _user(db)
    first = assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_ops.value
    )
    second = assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_ops.value
    )
    assert first.id == second.id


def test_require_platform_permission_allows_granted(db: Session) -> None:
    user = _user(db)
    assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_ops.value
    )
    dep = require_platform_permission("platform.stores.block")
    assert dep(current_user=user, session=db).id == user.id


def test_require_platform_permission_denies_missing(db: Session) -> None:
    user = _user(db)
    assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_finance.value
    )
    dep = require_platform_permission("platform.stores.block")  # finance lacks this
    with pytest.raises(AppError) as exc:
        dep(current_user=user, session=db)
    assert exc.value.status_code == 403


def test_require_platform_permission_denies_no_role(db: Session) -> None:
    user = _user(db)
    dep = require_platform_permission("platform.stores.view")
    with pytest.raises(AppError) as exc:
        dep(current_user=user, session=db)
    assert exc.value.status_code == 403


def test_seeded_superuser_is_platform_owner(db: Session) -> None:
    superuser = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).one()
    roles = user_platform_roles(session=db, user_id=superuser.id)
    assert PlatformRole.platform_owner.value in roles


def test_get_current_active_superuser_requires_platform_owner(db: Session) -> None:
    user = _user(db)
    with pytest.raises(HTTPException) as exc:
        get_current_active_superuser(current_user=user, session=db)
    assert exc.value.status_code == 403
    assign_platform_role(
        session=db, user_id=user.id, role=PlatformRole.platform_owner.value
    )
    assert get_current_active_superuser(current_user=user, session=db).id == user.id


def test_record_audit_persists_entry(db: Session) -> None:
    user = _user(db)
    entry = record_audit(
        session=db,
        user_id=user.id,
        action="platform.stores.block",
        target_type="store",
        target_id="abc-123",
    )
    db.commit()
    found = db.exec(select(AuditLog).where(AuditLog.id == entry.id)).one()
    assert found.action == "platform.stores.block"
    assert found.user_id == user.id
    assert found.target_id == "abc-123"
