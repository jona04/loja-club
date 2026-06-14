"""Integration tests for freezing customizations in cart/order (P7-ORD-01)."""

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
from app.modules.cart.models import CartCart, CartItem
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import Product
from app.modules.customers.schemas import AddressInput
from app.modules.customers.services import create_or_update_customer
from app.modules.customization import repositories
from app.modules.customization.enums import CustomizationSessionStatus
from app.modules.customization.models import (
    CustomizationOrderItem,
    CustomizationProductSettings,
    CustomizationSession,
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

SF = "/api/v1/storefront"
CART = "/api/v1/storefront/cart"


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


def _approve_session(
    client: TestClient, headers: dict[str, str], product: Product
) -> str:
    """Run start → autosave a layer → approve; return the approved session id."""
    body = client.post(
        f"{SF}/customizations", headers=headers, json={"product_id": str(product.id)}
    ).json()
    sid: str = body["id"]
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
        files={"snapshot": ("s.png", _png(), "image/png")},
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


def test_add_requires_approved_session(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "frz-gate")
    product = _customizable_product(db, store)
    resp = client.post(
        f"{CART}/items", headers=h, json={"product_id": str(product.id), "quantity": 1}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "customization_required"


@pytest.mark.usefixtures("s3")
def test_add_with_approved_session_links(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "frz-add")
    product = _customizable_product(db, store)
    sid = _approve_session(client, h, product)

    resp = client.post(
        f"{CART}/items",
        headers=h,
        json={
            "product_id": str(product.id),
            "quantity": 1,
            "customization_session_id": sid,
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["item_count"] == 1

    obj = db.get(CustomizationSession, uuid.UUID(sid))
    assert obj is not None
    assert obj.status == CustomizationSessionStatus.added_to_cart

    cart = _active_cart(db, store)
    item = db.exec(select(CartItem).where(CartItem.cart_id == cart.id)).first()
    assert item is not None
    link = repositories.get_cart_item_link(
        session=db, store_id=store.id, cart_item_id=item.id
    )
    assert link is not None
    assert link.customization_session_id == uuid.UUID(sid)


def _checkout(db: Session, store: Store, cart: CartCart) -> Any:
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
    return create_order(
        session=db,
        cart=cart,
        customer=customer,
        address=AddressInput(line1="Rua A", city="SP", country="BR"),
        shipping_method=method,
    )


def test_order_freezes_customization(client: TestClient, db: Session, s3: Any) -> None:
    store, h = _published_store(db, "frz-order")
    product = _customizable_product(db, store)
    sid = _approve_session(client, h, product)
    client.post(
        f"{CART}/items",
        headers=h,
        json={
            "product_id": str(product.id),
            "quantity": 1,
            "customization_session_id": sid,
        },
    )
    cart = _active_cart(db, store)
    order = _checkout(db, store, cart)

    frozen = db.exec(
        select(CustomizationOrderItem).where(
            CustomizationOrderItem.order_id == order.id
        )
    ).first()
    assert frozen is not None
    sess = db.get(CustomizationSession, uuid.UUID(sid))
    assert sess is not None
    assert frozen.platform_3d_model_version_id == sess.platform_3d_model_version_id
    layers = frozen.state_json["layers"]
    assert isinstance(layers, list) and len(layers) == 1
    assert frozen.snapshot_key is not None
    assert frozen.snapshot_key.startswith(f"private/{store.id}/orders/{order.id}/")
    # The snapshot was copied to the order prefix (exists on S3).
    s3.get_object(Bucket="loja-club-test", Key=frozen.snapshot_key)
    # The session is now marked ordered.
    assert sess.status == CustomizationSessionStatus.ordered


@pytest.mark.usefixtures("s3")
def test_frozen_order_is_immutable(client: TestClient, db: Session) -> None:
    store, h = _published_store(db, "frz-immut")
    product = _customizable_product(db, store)
    sid = _approve_session(client, h, product)
    client.post(
        f"{CART}/items",
        headers=h,
        json={
            "product_id": str(product.id),
            "quantity": 1,
            "customization_session_id": sid,
        },
    )
    order = _checkout(db, store, _active_cart(db, store))
    frozen = db.exec(
        select(CustomizationOrderItem).where(
            CustomizationOrderItem.order_id == order.id
        )
    ).first()
    assert frozen is not None
    frozen_id = frozen.id

    # Mutating the session afterwards must not change the frozen order copy.
    sess = db.get(CustomizationSession, uuid.UUID(sid))
    assert sess is not None
    sess.state_json = {**sess.state_json, "layers": []}
    db.add(sess)
    db.commit()

    again = db.get(CustomizationOrderItem, frozen_id)
    assert again is not None
    again_layers = again.state_json["layers"]
    assert isinstance(again_layers, list) and len(again_layers) == 1
