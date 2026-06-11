"""Integration tests for platform-admin store operations."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.api import AppError
from app.core.config import settings
from app.db.base import get_datetime_utc
from app.modules.audit.models import AuditLog
from app.modules.platform_admin import services
from app.modules.stores.enums import StoreStatus
from app.modules.tenancy.deps import get_active_membership
from tests.utils.store import create_member, create_store, create_user


def test_list_stores_excludes_soft_deleted(db: Session) -> None:
    create_store(db, slug="padm-a")
    create_store(db, slug="padm-b")
    gone = create_store(db, slug="padm-gone")
    gone.deleted_at = get_datetime_utc()
    db.add(gone)
    db.flush()
    stores, _count = services.list_stores(session=db, skip=0, limit=100)
    slugs = {s.slug for s in stores}
    assert {"padm-a", "padm-b"} <= slugs
    assert "padm-gone" not in slugs


def test_list_stores_search(db: Session) -> None:
    create_store(db, slug="searchable-xyz")
    create_store(db, slug="other-store")
    stores, count = services.list_stores(session=db, skip=0, limit=50, search="xyz")
    assert [s.slug for s in stores] == ["searchable-xyz"]
    assert count == 1


def test_get_store_detail_includes_members(db: Session) -> None:
    store = create_store(db, slug="padm-detail")
    owner = create_user(db)
    create_member(db, store=store, user=owner, role_key="owner")
    detail = services.get_store_detail(session=db, store_id=store.id)
    assert detail.id == store.id
    assert [m.user_id for m in detail.members] == [owner.id]
    assert detail.members[0].role == "owner"


def test_get_store_detail_not_found(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        services.get_store_detail(session=db, store_id=uuid.uuid4())
    assert exc.value.status_code == 404


def test_block_store_sets_status_and_audits(db: Session) -> None:
    store = create_store(db, slug="padm-block")
    owner = create_user(db)
    create_member(db, store=store, user=owner, role_key="owner")
    actor = create_user(db)
    services.set_store_status(
        session=db,
        actor=actor,
        store_id=store.id,
        status=StoreStatus.blocked,
        action="platform.stores.block",
    )
    db.refresh(store)
    assert store.status == StoreStatus.blocked
    entry = db.exec(
        select(AuditLog).where(AuditLog.action == "platform.stores.block")
    ).first()
    assert entry is not None
    assert entry.store_id == store.id
    assert entry.user_id == actor.id
    # the dashboard guard now bars the member from the blocked store
    with pytest.raises(AppError) as exc:
        get_active_membership(store_id=store.id, session=db, current_user=owner)
    assert exc.value.code == "store_unavailable"


def test_list_stores_requires_platform_permission(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/stores", headers=normal_user_token_headers
    )
    assert r.status_code == 403


def test_list_stores_as_platform_owner(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/stores", headers=superuser_token_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body


def test_block_store_over_http(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    store = create_store(db, slug="padm-http-block")
    r = client.post(
        f"{settings.API_V1_STR}/platform/stores/{store.id}/block",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "blocked"
