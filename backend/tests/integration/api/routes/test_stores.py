"""Integration tests for the store and team endpoints (panel)."""

import uuid
from typing import Any

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.accounts import repositories as accounts_repo
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.stores.enums import MembershipStatus
from app.modules.stores.models import StoreMember, StoreRole
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email

API = settings.API_V1_STR


def _headers(client: TestClient, db: Session, email: str) -> dict[str, str]:
    return authentication_token_from_email(client=client, email=email, db=db)


def _create_store(
    client: TestClient, headers: dict[str, str], name: str
) -> dict[str, Any]:
    r = client.post(f"{API}/stores/", headers=headers, json={"name": name})
    assert r.status_code == 201, r.text
    data: dict[str, Any] = r.json()
    return data


def _add_active_member(
    db: Session, store_id: uuid.UUID, user_id: uuid.UUID, role_key: str
) -> None:
    role = db.exec(select(StoreRole).where(StoreRole.key == role_key)).one()
    db.add(
        StoreMember(
            store_id=store_id,
            user_id=user_id,
            role_id=role.id,
            status=MembershipStatus.active,
        )
    )
    db.commit()


def test_create_store_is_atomic(client: TestClient, db: Session) -> None:
    headers = _headers(client, db, random_email())
    body = _create_store(client, headers, "Brindes Fortaleza")
    store_id = uuid.UUID(body["id"])
    assert body["slug"] == "brindes-fortaleza"
    assert body["status"] == "draft"

    members = db.exec(select(StoreMember).where(StoreMember.store_id == store_id)).all()
    assert len(members) == 1
    assert members[0].status == MembershipStatus.active

    domain = db.exec(select(DomainHost).where(DomainHost.store_id == store_id)).first()
    assert domain is not None
    assert domain.host == f"brindes-fortaleza.{settings.DOMAIN}"
    assert domain.status == DomainStatus.active


def test_list_my_stores_isolation(client: TestClient, db: Session) -> None:
    headers_a = _headers(client, db, random_email())
    _create_store(client, headers_a, "Store Alpha")
    headers_b = _headers(client, db, random_email())
    _create_store(client, headers_b, "Store Beta")

    r = client.get(f"{API}/stores/", headers=headers_a)
    assert r.status_code == 200
    slugs = {s["slug"] for s in r.json()["data"]}
    assert "store-alpha" in slugs
    assert "store-beta" not in slugs


def test_get_store_non_member_forbidden(client: TestClient, db: Session) -> None:
    owner = _headers(client, db, random_email())
    store_id = _create_store(client, owner, "Owned")["id"]
    outsider = _headers(client, db, random_email())
    r = client.get(f"{API}/stores/{store_id}", headers=outsider)
    assert r.status_code == 403


def test_duplicate_slug_rejected(client: TestClient, db: Session) -> None:
    headers = _headers(client, db, random_email())
    r1 = client.post(
        f"{API}/stores/", headers=headers, json={"name": "Dup", "slug": "dup-slug"}
    )
    assert r1.status_code == 201
    r2 = client.post(
        f"{API}/stores/", headers=headers, json={"name": "Other", "slug": "dup-slug"}
    )
    assert r2.status_code == 409


def test_owner_updates_settings(client: TestClient, db: Session) -> None:
    headers = _headers(client, db, random_email())
    store_id = _create_store(client, headers, "Shop")["id"]
    r = client.patch(
        f"{API}/stores/{store_id}/settings",
        headers=headers,
        json={"public_name": "My Shop", "whatsapp_number": "+15551234567"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["public_name"] == "My Shop"
    assert body["whatsapp_number"] == "+15551234567"


def test_get_settings_round_trip(client: TestClient, db: Session) -> None:
    headers = _headers(client, db, random_email())
    store_id = _create_store(client, headers, "Settable")["id"]
    client.patch(
        f"{API}/stores/{store_id}/settings",
        headers=headers,
        json={"public_name": "Loaded Shop"},
    )
    r = client.get(f"{API}/stores/{store_id}/settings", headers=headers)
    assert r.status_code == 200
    assert r.json()["public_name"] == "Loaded Shop"


def test_support_denied_settings(client: TestClient, db: Session) -> None:
    owner = _headers(client, db, random_email())
    store_id = _create_store(client, owner, "Gated")["id"]
    support_email = random_email()
    support = _headers(client, db, support_email)
    support_user = accounts_repo.get_user_by_email(session=db, email=support_email)
    assert support_user is not None
    _add_active_member(db, uuid.UUID(store_id), support_user.id, "support")

    r = client.patch(
        f"{API}/stores/{store_id}/settings",
        headers=support,
        json={"public_name": "Nope"},
    )
    assert r.status_code == 403


def test_publish_and_pause(client: TestClient, db: Session) -> None:
    headers = _headers(client, db, random_email())
    store_id = _create_store(client, headers, "Pubbable")["id"]
    r = client.post(f"{API}/stores/{store_id}/publish", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "active"
    r = client.post(f"{API}/stores/{store_id}/pause", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "paused"


def test_my_membership(client: TestClient, db: Session) -> None:
    headers = _headers(client, db, random_email())
    store_id = _create_store(client, headers, "MineShop")["id"]
    r = client.get(f"{API}/stores/{store_id}/me", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "owner"
    assert "settings.update" in body["permissions"]


def test_invite_existing_user(client: TestClient, db: Session) -> None:
    owner = _headers(client, db, random_email())
    store_id = _create_store(client, owner, "Teamed")["id"]
    invitee_email = random_email()
    _headers(client, db, invitee_email)  # create the invitee's account
    r = client.post(
        f"{API}/stores/{store_id}/members",
        headers=owner,
        json={"email": invitee_email, "role": "support"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "invited"
    assert body["role"] == "support"
    assert body["email"] == invitee_email


def test_invite_unknown_email_not_found(client: TestClient, db: Session) -> None:
    owner = _headers(client, db, random_email())
    store_id = _create_store(client, owner, "NoGhost")["id"]
    r = client.post(
        f"{API}/stores/{store_id}/members",
        headers=owner,
        json={"email": random_email(), "role": "support"},
    )
    assert r.status_code == 404
