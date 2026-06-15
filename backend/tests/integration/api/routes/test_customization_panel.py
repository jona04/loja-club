"""Integration tests for the merchant customization panel (P7-OPS-01)."""

import io
import uuid
from collections.abc import Generator
from typing import Any

import boto3  # type: ignore[import-untyped]  # boto3 ships no type stubs
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlmodel import Session, col, select

from app.core import storage
from app.core.config import settings
from app.modules.cart.enums import CartStatus
from app.modules.cart.models import CartCart
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import Product
from app.modules.customers.schemas import AddressInput
from app.modules.customers.services import create_or_update_customer
from app.modules.customization import repositories
from app.modules.customization.models import (
    CustomizationProductSettings,
    Platform3DModel,
)
from app.modules.customization.repositories import MUG_SLUG
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.orders.services import create_order
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store
from tests.utils.store import create_member, create_user, member_headers

SF = "/api/v1/storefront"
CART = "/api/v1/storefront/cart"
PANEL = "/api/v1/stores"


def _png(size: tuple[int, int] = (700, 700)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, "red").save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> Generator[Any, None, None]:
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
    return next(
        m for m in repositories.list_active_models(session=db) if m.slug == MUG_SLUG
    )


def _customizable_product(db: Session, store: Store) -> Product:
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


def _text_layer() -> dict[str, object]:
    return {
        "id": "l1",
        "kind": "text",
        "area_id": "front",
        "z": 0,
        "transform": {"x": 0.5, "y": 0.5, "scale": 1.0, "rotation_deg": 0},
        "text": "Oi",
        "font": "inter",
        "font_size": 48,
        "color": "#222222",
    }


def _owner_headers(
    client: TestClient, db: Session, store: Store, role_key: str = "owner"
) -> dict[str, str]:
    """Create a member of the store with a role and return its JWT headers."""
    user = create_user(db)
    create_member(db, store=store, user=user, role_key=role_key)
    return member_headers(client, db, user)


def _start(client: TestClient, headers: dict[str, str], product: Product) -> str:
    body = client.post(
        f"{SF}/customizations", headers=headers, json={"product_id": str(product.id)}
    ).json()
    return str(body["id"])


def _approve(client: TestClient, headers: dict[str, str], product: Product) -> str:
    """Start → autosave a layer → approve; return the approved session id."""
    body = client.post(
        f"{SF}/customizations", headers=headers, json={"product_id": str(product.id)}
    ).json()
    sid = str(body["id"])
    client.put(
        f"{SF}/customizations/{sid}/state",
        headers=headers,
        json={
            "schema_version": 1,
            "model": body["state_json"]["model"],
            "layers": [_text_layer()],
        },
    )
    approve = client.post(
        f"{SF}/customizations/{sid}/approve",
        headers=headers,
        files={
            "snapshot": ("s.png", _png(), "image/png"),
            "composite": ("c.png", _png((1200, 480)), "image/png"),
        },
    )
    assert approve.status_code == 200, approve.text
    return sid


def _active_cart(db: Session, store: Store) -> CartCart:
    cart = db.exec(
        select(CartCart).where(
            CartCart.store_id == store.id,
            CartCart.status == CartStatus.active,
            col(CartCart.deleted_at).is_(None),
        )
    ).first()
    assert cart is not None
    return cart


def _order_customization(
    client: TestClient, db: Session, store: Store, headers: dict[str, str], sid: str
) -> None:
    """Add the approved session to the cart and place an order (freezes it)."""
    client.post(
        f"{CART}/items",
        headers=headers,
        json={
            "product_id": str(
                db.exec(select(Product).where(Product.store_id == store.id)).first().id  # type: ignore[union-attr]
            ),
            "quantity": 1,
            "customization_session_id": sid,
        },
    )
    method = ShippingMethod(
        store_id=store.id,
        type=ShippingMethodType.fixed_shipping,
        name="Frete",
        price_amount_minor=900,
    )
    db.add(method)
    db.flush()
    customer = create_or_update_customer(
        session=db,
        store_id=store.id,
        name="Ana",
        email=f"ana-{uuid.uuid4().hex[:6]}@x.com",
    )
    create_order(
        session=db,
        cart=_active_cart(db, store),
        customer=customer,
        address=AddressInput(line1="Rua A", city="SP", country="BR"),
        shipping_method=method,
    )


@pytest.mark.usefixtures("s3")
def test_list_shows_store_sessions(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "ops-list")
    product = _customizable_product(db, store)
    sid = _start(client, h, product)
    mh = _owner_headers(client, db, store)

    resp = client.get(f"{PANEL}/{store.id}/customizations", headers=mh)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["count"] >= 1
    row = next(r for r in body["data"] if r["id"] == sid)
    assert row["product_name"] == "Caneca"
    assert row["status"] == "draft"
    assert row["production_status"] is None
    assert row["is_assisted"] is False


@pytest.mark.usefixtures("s3")
def test_detail_returns_presigned_downloads(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "ops-detail")
    product = _customizable_product(db, store)
    sid = _approve(client, h, product)
    mh = _owner_headers(client, db, store)

    resp = client.get(f"{PANEL}/{store.id}/customizations/{sid}", headers=mh)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["product_name"] == "Caneca"
    assert body["snapshot_url"] is not None
    assert body["composite_url"] is not None
    assert body["production_status"] is None


@pytest.mark.usefixtures("s3")
def test_production_status_lifecycle(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "ops-prod")
    product = _customizable_product(db, store)
    sid = _approve(client, h, product)
    _order_customization(client, db, store, h, sid)
    mh = _owner_headers(client, db, store)

    # Frozen order starts at 'received'.
    detail = client.get(f"{PANEL}/{store.id}/customizations/{sid}", headers=mh).json()
    assert detail["production_status"] == "received"
    assert detail["order_id"] is not None

    upd = client.put(
        f"{PANEL}/{store.id}/customizations/{sid}/production-status",
        headers=mh,
        json={"production_status": "in_production"},
    )
    assert upd.status_code == 200, upd.text
    assert upd.json()["production_status"] == "in_production"

    # The list surfaces the new production status too.
    row = next(
        r
        for r in client.get(f"{PANEL}/{store.id}/customizations", headers=mh).json()[
            "data"
        ]
        if r["id"] == sid
    )
    assert row["production_status"] == "in_production"


@pytest.mark.usefixtures("s3")
def test_production_status_requires_order(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "ops-noorder")
    product = _customizable_product(db, store)
    sid = _approve(client, h, product)
    mh = _owner_headers(client, db, store)

    resp = client.put(
        f"{PANEL}/{store.id}/customizations/{sid}/production-status",
        headers=mh,
        json={"production_status": "in_production"},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "not_ordered"


@pytest.mark.usefixtures("s3")
def test_detail_other_store_is_404(client: TestClient, db: Session) -> None:
    store_a, ha = _published_store(db, "ops-a")
    product = _customizable_product(db, store_a)
    sid = _start(client, ha, product)
    store_b, _ = _published_store(db, "ops-b")
    mhb = _owner_headers(client, db, store_b)

    resp = client.get(f"{PANEL}/{store_b.id}/customizations/{sid}", headers=mhb)
    assert resp.status_code == 404


def test_list_requires_permission(client: TestClient, db: Session) -> None:
    store, _ = _published_store(db, "ops-perm")
    # 'marketing' holds customization.view but not customization.sessions.view.
    mh = _owner_headers(client, db, store, role_key="marketing")
    resp = client.get(f"{PANEL}/{store.id}/customizations", headers=mh)
    assert resp.status_code == 403
