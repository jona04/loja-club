"""Cross-tenant isolation suite: Store A must never see or touch Store B.

Built on the shared multi-tenant factories (``two_stores`` + ``tests.utils.store``)
that later commercial features reuse. Isolation is asserted on the **observable
result** (403/404/absence), never on internal SQL.
"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.store import TenantContext, create_member, create_user, member_headers

API = settings.API_V1_STR


def test_member_cannot_read_other_store(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.get(
        f"{API}/stores/{two_stores.store_b.id}", headers=two_stores.owner_a_headers
    )
    assert r.status_code == 403


def test_member_cannot_edit_other_store_settings(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.patch(
        f"{API}/stores/{two_stores.store_b.id}/settings",
        headers=two_stores.owner_a_headers,
        json={"public_name": "hijack"},
    )
    assert r.status_code == 403


def test_member_cannot_list_other_store_members(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.get(
        f"{API}/stores/{two_stores.store_b.id}/members",
        headers=two_stores.owner_a_headers,
    )
    assert r.status_code == 403


def test_member_cannot_publish_other_store(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.post(
        f"{API}/stores/{two_stores.store_b.id}/publish",
        headers=two_stores.owner_a_headers,
    )
    assert r.status_code == 403


def test_member_cannot_read_membership_on_other_store(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.get(
        f"{API}/stores/{two_stores.store_b.id}/me",
        headers=two_stores.owner_a_headers,
    )
    assert r.status_code == 403


def test_list_returns_only_own_store(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.get(f"{API}/stores/", headers=two_stores.owner_a_headers)
    assert r.status_code == 200
    ids = {s["id"] for s in r.json()["data"]}
    assert str(two_stores.store_a.id) in ids
    assert str(two_stores.store_b.id) not in ids


def test_unknown_store_is_not_found(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.get(f"{API}/stores/{uuid.uuid4()}", headers=two_stores.owner_a_headers)
    assert r.status_code == 404


# --- per-role permission smoke (on the shared factories) ---


def test_owner_allowed_to_edit_settings(
    client: TestClient, two_stores: TenantContext
) -> None:
    r = client.patch(
        f"{API}/stores/{two_stores.store_a.id}/settings",
        headers=two_stores.owner_a_headers,
        json={"public_name": "Shop A"},
    )
    assert r.status_code == 200


def test_support_denied_settings_and_team(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    support = create_user(db)
    create_member(db, store=two_stores.store_a, user=support, role_key="support")
    headers = member_headers(client, db, support)
    settings_resp = client.patch(
        f"{API}/stores/{two_stores.store_a.id}/settings",
        headers=headers,
        json={"public_name": "nope"},
    )
    members_resp = client.get(
        f"{API}/stores/{two_stores.store_a.id}/members", headers=headers
    )
    assert settings_resp.status_code == 403
    assert members_resp.status_code == 403


def test_admin_allowed_to_list_team(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    admin = create_user(db)
    create_member(db, store=two_stores.store_a, user=admin, role_key="admin")
    headers = member_headers(client, db, admin)
    r = client.get(f"{API}/stores/{two_stores.store_a.id}/members", headers=headers)
    assert r.status_code == 200
