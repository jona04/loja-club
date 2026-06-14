"""Freezing customizations into the cart and the order (INV-P5, doc 30 §7).

An ``image_3d_customizable`` product only enters the cart with an **approved**
session; at order time the customization is **copied** (state + pinned version +
snapshot) into ``customization_order_items`` and the snapshot is duplicated under
the order's private prefix — so a placed order never depends on the live session.
"""

import copy
import io
import uuid

from sqlmodel import Session

from app.core import storage
from app.core.api import AppError
from app.modules.customization import repositories
from app.modules.customization.enums import CustomizationSessionStatus
from app.modules.customization.models import (
    CustomizationCartItem,
    CustomizationOrderItem,
    CustomizationSession,
)
from app.modules.customization.sessions import SNAPSHOT_MIME
from app.modules.customization.storage import customization_order_key


def resolve_approved_session(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    guest_session_id: str,
    session_id: uuid.UUID | None,
) -> CustomizationSession:
    """Return the guest's **approved** session for a product, or raise 422.

    Enforces the add-to-cart gate for customizable products: the session must
    exist in the store, belong to this guest, target this product and be
    ``approved``.

    Args:
        session: Active database session.
        store_id: The store id.
        product_id: The product being added.
        guest_session_id: The guest browser's session id.
        session_id: The customization session id from the request (or ``None``).

    Returns:
        The approved customization session.

    Raises:
        AppError: 422 ``customization_required`` if there is no matching approved
            session.
    """
    obj = (
        repositories.get_session(
            session=session, store_id=store_id, session_id=session_id
        )
        if session_id is not None
        else None
    )
    if (
        obj is None
        or obj.guest_session_id != guest_session_id
        or obj.product_id != product_id
        or obj.status != CustomizationSessionStatus.approved
    ):
        raise AppError(
            "customization_required",
            "This product must be customized and approved before adding to the cart",
            status_code=422,
        )
    return obj


def link_session_to_cart_item(
    *, session: Session, cart_item_id: uuid.UUID, cust_session: CustomizationSession
) -> None:
    """Attach an approved session to a cart line and mark it added-to-cart.

    Args:
        session: Active database session.
        cart_item_id: The cart line id.
        cust_session: The approved customization session.
    """
    session.add(
        CustomizationCartItem(
            store_id=cust_session.store_id,
            cart_item_id=cart_item_id,
            customization_session_id=cust_session.id,
        )
    )
    cust_session.status = CustomizationSessionStatus.added_to_cart
    session.add(cust_session)


def cart_item_image_url(
    *, session: Session, store_id: uuid.UUID, cart_item_id: uuid.UUID
) -> str | None:
    """Return the customization snapshot URL for a cart line, if customized.

    Lets the cart show the customer's personalized mug photo instead of the
    generic product image, so distinct customizations are distinguishable.

    Args:
        session: Active database session.
        store_id: The owning store id.
        cart_item_id: The cart line id.

    Returns:
        A presigned snapshot URL, or ``None`` if the line isn't customized.
    """
    link = repositories.get_cart_item_link(
        session=session, store_id=store_id, cart_item_id=cart_item_id
    )
    if link is None:
        return None
    cust = repositories.get_session(
        session=session, store_id=store_id, session_id=link.customization_session_id
    )
    if cust is None or not cust.snapshot_key:
        return None
    return storage.generate_presigned_url(cust.snapshot_key)


def _copy_to_order(
    source_key: str | None,
    store_id: uuid.UUID,
    order_id: uuid.UUID,
    filename: str,
) -> str | None:
    """Copy a private asset to the order's prefix, or ``None`` if there is none.

    Raises on failure so the order is not committed without its frozen assets.
    """
    if not source_key:
        return None
    data = storage.download(source_key)
    dest = customization_order_key(store_id, order_id, filename)
    storage.upload_fileobj(dest, io.BytesIO(data), SNAPSHOT_MIME)
    return dest


def freeze_order_item(
    *,
    session: Session,
    store_id: uuid.UUID,
    order_id: uuid.UUID,
    order_item_id: uuid.UUID,
    cart_item_id: uuid.UUID,
) -> None:
    """Freeze a cart line's customization into the order line, if any.

    Copies the approved ``state_json`` + pinned version, duplicates the snapshot
    under the order's private prefix, and marks the session ``ordered``. A
    regular (non-customizable) line is a no-op. If the snapshot copy fails the
    exception propagates so the order is not committed.

    Args:
        session: Active database session.
        store_id: The order's store id.
        order_id: The order id.
        order_item_id: The order line id to attach the frozen copy to.
        cart_item_id: The originating cart line id.
    """
    link = repositories.get_cart_item_link(
        session=session, store_id=store_id, cart_item_id=cart_item_id
    )
    if link is None:
        return
    cust_session = repositories.get_session(
        session=session,
        store_id=store_id,
        session_id=link.customization_session_id,
    )
    if cust_session is None:  # pragma: no cover - FK guarantees it exists
        return

    frozen_snapshot_key = _copy_to_order(
        cust_session.snapshot_key, store_id, order_id, "snapshot.png"
    )
    frozen_composite_key = _copy_to_order(
        cust_session.composite_key, store_id, order_id, "composite.png"
    )

    session.add(
        CustomizationOrderItem(
            store_id=store_id,
            order_id=order_id,
            order_item_id=order_item_id,
            customization_session_id=cust_session.id,
            platform_3d_model_version_id=cust_session.platform_3d_model_version_id,
            # Deep copy: the frozen order must never share state with the session.
            state_json=copy.deepcopy(cust_session.state_json),
            snapshot_key=frozen_snapshot_key,
            composite_key=frozen_composite_key,
        )
    )
    cust_session.status = CustomizationSessionStatus.ordered
    session.add(cust_session)
