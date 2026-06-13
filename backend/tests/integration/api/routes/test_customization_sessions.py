"""Integration tests for customization sessions (editor backend, doc 30)."""

import io
import uuid
from collections.abc import Generator
from datetime import timedelta
from typing import Any

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlmodel import Session

from app.core import storage
from app.core.config import settings
from app.db.base import get_datetime_utc
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import Product
from app.modules.customization import repositories, sessions
from app.modules.customization.enums import CustomizationSessionStatus
from app.modules.customization.models import (
    CustomizationProductSettings,
    CustomizationSession,
    Platform3DModel,
)
from app.modules.customization.repositories import MUG_SLUG
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store
from tests.utils.store import TenantContext, create_member, create_user, member_headers

SF = "/api/v1/storefront"
PANEL = "/api/v1/stores"


def _png(size: tuple[int, int] = (1200, 900), color: str = "red") -> bytes:
    """Return freshly encoded PNG bytes of the given size."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> Generator[Any, None, None]:
    """Provide a mocked S3 bucket for upload/snapshot tests."""
    from moto import mock_aws

    with mock_aws():
        storage.reset_client()
        monkeypatch.setattr(settings, "S3_BUCKET", "loja-club-test")
        monkeypatch.setattr(settings, "CDN_BASE_URL", "https://cdn.test")
        client = boto3.client("s3", region_name=settings.S3_REGION)
        client.create_bucket(
            Bucket="loja-club-test",
            CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION},
        )
        yield client


def _published_store(db: Session, slug: str) -> tuple[Store, dict[str, str]]:
    """Create an active store with a resolvable host; return (store, headers)."""
    store = Store(
        name="L", slug=slug, currency="BRL", locale="pt-BR", status=StoreStatus.active
    )
    db.add(store)
    db.flush()
    host = f"{uuid.uuid4().hex[:10]}.localhost"
    db.add(DomainHost(host=host, store_id=store.id, status=DomainStatus.active))
    db.flush()
    return store, {"host": host}


def _mug(db: Session) -> Platform3DModel:
    """Return the seeded ceramic-mug catalog model."""
    return next(
        m for m in repositories.list_active_models(session=db) if m.slug == MUG_SLUG
    )


def _customizable_product(db: Session, store: Store) -> Product:
    """Create a published customizable product linked to the mug model."""
    product = Product(
        store_id=store.id,
        name="Caneca",
        slug=f"caneca-{uuid.uuid4().hex[:6]}",
        type=ProductType.image_3d_customizable,
        status=ProductStatus.published,
        price_amount_minor=2500,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    db.add(
        CustomizationProductSettings(
            store_id=store.id,
            product_id=product.id,
            platform_3d_model_id=_mug(db).id,
        )
    )
    db.flush()
    return product


def _text_layer(area_id: str = "front") -> dict[str, object]:
    """Return a valid text layer for the seeded mug version."""
    return {
        "id": "l1",
        "kind": "text",
        "area_id": area_id,
        "z": 0,
        "transform": {"x": 0.5, "y": 0.5, "scale": 1.0, "rotation_deg": 0},
        "text": "João & Maria",
        "font": "inter",
        "font_size": 48,
        "color": "#222222",
    }


def _start(
    client: TestClient, headers: dict[str, str], product: Product
) -> dict[str, Any]:
    """Start a session and return the parsed body."""
    resp = client.post(
        f"{SF}/customizations",
        headers=headers,
        json={"product_id": str(product.id)},
    )
    assert resp.status_code == 201, resp.text
    body: dict[str, Any] = resp.json()
    return body


def test_start_and_autosave(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-start")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    assert body["status"] == "draft"
    assert body["version"]["glb_url"].endswith(f"/{MUG_SLUG}/v1/model.glb")

    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [_text_layer()],
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["state_json"]["layers"]) == 1


def test_start_resumes_existing_draft(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-resume")
    product = _customizable_product(db, store)
    first = _start(client, h, product)
    second = _start(client, h, product)
    assert first["id"] == second["id"]


def test_start_rejects_non_customizable(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-plain")
    product = Product(
        store_id=store.id,
        name="Plain",
        slug="plain",
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=1000,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    resp = client.post(
        f"{SF}/customizations", headers=h, json={"product_id": str(product.id)}
    )
    assert resp.status_code == 422


def test_autosave_rejects_bad_font(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-font")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    layer = _text_layer()
    layer["font"] = "comic-sans"
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [layer],
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "font_not_allowed"


def test_autosave_rejects_unknown_area(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-area")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [_text_layer(area_id="back")],
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "unknown_area"


def test_autosave_rejects_transform_out_of_range(
    client: TestClient, db: Session
) -> None:
    store, h = _published_store(db, "cust-transform")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    layer = _text_layer()
    layer["transform"] = {"x": 1.5, "y": 0.5, "scale": 1.0, "rotation_deg": 0}
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [layer],
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "transform_out_of_range"


def test_autosave_rejects_image_layer_without_upload(
    client: TestClient, db: Session
) -> None:
    store, h = _published_store(db, "cust-img")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    layer = {
        "id": "l1",
        "kind": "image",
        "area_id": "front",
        "z": 0,
        "transform": {"x": 0.5, "y": 0.5, "scale": 1.0, "rotation_deg": 0},
        "upload_id": str(uuid.uuid4()),
    }
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [layer],
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "unknown_upload"


@pytest.mark.usefixtures("s3")
def test_upload_and_reference_in_layer(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-upload")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    up = client.post(
        f"{SF}/customizations/{body['id']}/uploads",
        headers=h,
        files={"file": ("art.png", _png(), "image/png")},
    )
    assert up.status_code == 201, up.text
    upload = up.json()
    assert upload["url"]
    assert upload["low_resolution"] is False

    layer = {
        "id": "l1",
        "kind": "image",
        "area_id": "front",
        "z": 0,
        "transform": {"x": 0.5, "y": 0.5, "scale": 0.8, "rotation_deg": 0},
        "upload_id": upload["id"],
    }
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [layer],
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 200, resp.text


@pytest.mark.usefixtures("s3")
def test_upload_low_resolution_warns(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-lowres")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    up = client.post(
        f"{SF}/customizations/{body['id']}/uploads",
        headers=h,
        files={"file": ("tiny.png", _png(size=(100, 100)), "image/png")},
    )
    assert up.status_code == 201
    assert up.json()["low_resolution"] is True


@pytest.mark.usefixtures("s3")
def test_upload_rejects_non_image(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-bad")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    up = client.post(
        f"{SF}/customizations/{body['id']}/uploads",
        headers=h,
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert up.status_code == 422


@pytest.mark.usefixtures("s3")
def test_approve_freezes_and_blocks_edits(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-approve")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": [_text_layer()],
    }
    client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)

    approve = client.post(
        f"{SF}/customizations/{body['id']}/approve",
        headers=h,
        files={"snapshot": ("snap.png", _png(size=(800, 800)), "image/png")},
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None
    assert approved["snapshot_url"]

    # No more edits once approved.
    again = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert again.status_code == 409


@pytest.mark.usefixtures("s3")
def test_approve_requires_png_snapshot(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-snap")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    resp = client.post(
        f"{SF}/customizations/{body['id']}/approve",
        headers=h,
        files={"snapshot": ("snap.jpg", _png(), "image/jpeg")},
    )
    assert resp.status_code == 422


def test_other_store_cannot_read_session(client: TestClient, db: Session) -> None:
    store_a, ha = _published_store(db, "cust-iso-a")
    _store_b, hb = _published_store(db, "cust-iso-b")
    product = _customizable_product(db, store_a)
    body = _start(client, ha, product)
    # Same session id, but addressed through store B's host -> not found.
    resp = client.get(f"{SF}/customizations/{body['id']}", headers=hb)
    assert resp.status_code == 404


@pytest.mark.usefixtures("s3")
def test_assisted_create_and_public_approve(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    product = _customizable_product(db, a)
    created = client.post(
        f"{PANEL}/{a.id}/customizations/assisted",
        headers=h,
        json={"product_id": str(product.id), "name": "João", "email": "joao@x.com"},
    )
    assert created.status_code == 201, created.text
    body = created.json()
    token = body["public_token"]
    assert body["status"] == "draft"

    # Public link opens read-only.
    view = client.get(f"{SF}/p/{token}")
    assert view.status_code == 200
    assert view.json()["id"] == body["id"]

    # Approving needs the matching contact.
    snap = {"snapshot": ("snap.png", _png(size=(700, 700)), "image/png")}
    wrong = client.post(
        f"{SF}/p/{token}/approve", data={"email": "no@x.com"}, files=snap
    )
    assert wrong.status_code == 403

    ok = client.post(
        f"{SF}/p/{token}/approve", data={"email": "joao@x.com"}, files=snap
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["status"] == "approved"


def test_assisted_requires_permission(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a = two_stores.store_a
    product = _customizable_product(db, a)
    # 'marketing' holds customization.view but not customization.sessions.view.
    user = create_user(db)
    create_member(db, store=a, user=user, role_key="marketing")
    headers = member_headers(client, db, user)
    resp = client.post(
        f"{PANEL}/{a.id}/customizations/assisted",
        headers=headers,
        json={"product_id": str(product.id), "name": "X", "email": "x@x.com"},
    )
    assert resp.status_code == 403


def test_public_token_unknown_is_404(client: TestClient) -> None:
    resp = client.get(f"{SF}/p/does-not-exist")
    assert resp.status_code == 404


def test_autosave_rejects_too_many_layers(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-cap")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    layers = []
    for i in range(6):  # the seeded front area allows max 5
        layer = _text_layer()
        layer["id"] = f"l{i}"
        layers.append(layer)
    state = {
        "schema_version": 1,
        "model": body["state_json"]["model"],
        "layers": layers,
    }
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "too_many_layers"


def test_autosave_rejects_version_mismatch(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-vmismatch")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    model_ref = dict(body["state_json"]["model"])
    model_ref["version_id"] = str(uuid.uuid4())
    state = {"schema_version": 1, "model": model_ref, "layers": []}
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "version_mismatch"


def test_autosave_on_expired_session_is_410(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-exp-auto")
    product = _customizable_product(db, store)
    body = _start(client, h, product)
    obj = db.get(CustomizationSession, uuid.UUID(body["id"]))
    assert obj is not None
    obj.expires_at = get_datetime_utc() - timedelta(days=1)
    db.add(obj)
    db.commit()
    state = {"schema_version": 1, "model": body["state_json"]["model"], "layers": []}
    resp = client.put(f"{SF}/customizations/{body['id']}/state", headers=h, json=state)
    assert resp.status_code == 410


@pytest.mark.usefixtures("s3")
def test_upload_too_large_is_413(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "cust-big")
    product = _customizable_product(db, store)
    version = repositories.get_active_version(session=db, model_id=_mug(db).id)
    assert version is not None
    version.art_limits = {**version.art_limits, "max_bytes": 10}
    db.add(version)
    db.commit()
    body = _start(client, h, product)
    up = client.post(
        f"{SF}/customizations/{body['id']}/uploads",
        headers=h,
        files={"file": ("art.png", _png(size=(100, 100)), "image/png")},
    )
    assert up.status_code == 413


def test_public_token_expired_is_410(
    client: TestClient, db: Session, two_stores: TenantContext
) -> None:
    a, h = two_stores.store_a, two_stores.owner_a_headers
    product = _customizable_product(db, a)
    created = client.post(
        f"{PANEL}/{a.id}/customizations/assisted",
        headers=h,
        json={"product_id": str(product.id), "name": "João", "email": "joao@x.com"},
    )
    token = created.json()["public_token"]
    obj = db.get(CustomizationSession, uuid.UUID(created.json()["id"]))
    assert obj is not None
    obj.expires_at = get_datetime_utc() - timedelta(days=1)
    db.add(obj)
    db.commit()
    resp = client.get(f"{SF}/p/{token}")
    assert resp.status_code == 410


def test_expire_sweeps_old_drafts(db: Session) -> None:
    store, _h = _published_store(db, "cust-expire")
    product = _customizable_product(db, store)
    version = repositories.get_active_version(session=db, model_id=_mug(db).id)
    assert version is not None
    stale = CustomizationSession(
        store_id=store.id,
        product_id=product.id,
        platform_3d_model_version_id=version.id,
        status=CustomizationSessionStatus.draft,
        guest_session_id="g",
        expires_at=get_datetime_utc() - timedelta(days=1),
    )
    db.add(stale)
    db.commit()

    swept = sessions.expire_sessions(session=db, now=get_datetime_utc())
    assert swept >= 1
    db.refresh(stale)
    assert stale.status == CustomizationSessionStatus.expired
    assert stale.deleted_at is not None
