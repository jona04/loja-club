"""Integration tests for platform-admin user operations and the soft-delete guard."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.api import AppError
from app.core.config import settings
from app.db.base import get_datetime_utc
from app.modules.accounts import repositories
from app.modules.audit.models import AuditLog
from app.modules.platform_admin import services
from tests.utils.store import create_user


def _soft_delete(db: Session, user: object) -> None:
    user.deleted_at = get_datetime_utc()  # type: ignore[attr-defined]
    db.add(user)
    db.flush()


def test_list_users_excludes_soft_deleted(db: Session) -> None:
    keep = create_user(db)
    gone = create_user(db)
    _soft_delete(db, gone)
    users, _count = services.list_users(session=db, skip=0, limit=200)
    ids = {u.id for u in users}
    assert keep.id in ids
    assert gone.id not in ids


def test_get_user_soft_deleted_not_found(db: Session) -> None:
    gone = create_user(db)
    _soft_delete(db, gone)
    with pytest.raises(AppError) as exc:
        services.get_user(session=db, user_id=gone.id)
    assert exc.value.status_code == 404


def test_get_active_user_excludes_soft_deleted(db: Session) -> None:
    gone = create_user(db)
    _soft_delete(db, gone)
    assert repositories.get_active_user(session=db, user_id=gone.id) is None


def test_impersonate_issues_token_and_records(db: Session) -> None:
    actor = create_user(db)
    target = create_user(db)
    token = services.impersonate(session=db, actor=actor, user_id=target.id)
    assert isinstance(token, str)
    assert token
    entry = db.exec(
        select(AuditLog).where(AuditLog.action == "platform.support.impersonate")
    ).first()
    assert entry is not None
    assert entry.user_id == actor.id
    assert entry.target_id == str(target.id)


def test_impersonate_missing_user_not_found(db: Session) -> None:
    actor = create_user(db)
    with pytest.raises(AppError) as exc:
        services.impersonate(session=db, actor=actor, user_id=uuid.uuid4())
    assert exc.value.status_code == 404


def test_read_user_by_id_hides_soft_deleted(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    gone = create_user(db)
    _soft_delete(db, gone)
    r = client.get(
        f"{settings.API_V1_STR}/users/{gone.id}", headers=superuser_token_headers
    )
    assert r.status_code == 404


def test_list_users_requires_platform_permission(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/users", headers=normal_user_token_headers
    )
    assert r.status_code == 403


def test_impersonate_over_http(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    target = create_user(db)
    r = client.post(
        f"{settings.API_V1_STR}/platform/users/{target.id}/impersonate",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["access_token"]
