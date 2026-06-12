"""Checkout services: orchestrate the no-gateway checkout + store policies.

``submit_checkout`` ties together the cart (``P6-CART-01``), customer dedup
(``P6-CUST-01``), shipping (``P6-SHIP-01``) and order creation (``P6-ORD-01``):
it runs the composable checks, dedups the customer, resolves the chosen method,
records a checkout session and creates the ``pending_payment`` order. There is no
gateway — ``payments.get_gateway`` is the no-op seam reserved for Fase 8.
"""

import uuid
from collections.abc import Callable
from datetime import timedelta

from sqlmodel import Session, col, select

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.cart import services as cart_services
from app.modules.cart.models import CartCart, CartItem
from app.modules.checkout.enums import CheckoutStatus
from app.modules.checkout.models import CheckoutSession
from app.modules.checkout.schemas import CheckoutInput, PoliciesUpdate
from app.modules.customers import services as customer_services
from app.modules.customers.models import CustomerGuestSession
from app.modules.orders import services as order_services
from app.modules.orders.models import Order
from app.modules.payments.gateway import get_gateway
from app.modules.shipping.models import ShippingMethod
from app.modules.stores import services as store_services
from app.modules.stores.models import StoreSettings

_CHECKOUT_TTL = timedelta(hours=24)


def _check_cart_not_empty(session: Session, cart: CartCart) -> None:
    """Refuse an empty cart at checkout."""
    has_item = session.exec(
        select(CartItem.id).where(
            CartItem.cart_id == cart.id,
            CartItem.store_id == cart.store_id,
            col(CartItem.deleted_at).is_(None),
        )
    ).first()
    if has_item is None:
        raise AppError("empty_cart", "The cart is empty", status_code=422)


# Composable checkout checks. Fase 7 appends "every image_3d_customizable item
# has an approved customization session".
_CHECKOUT_CHECKS: list[Callable[[Session, CartCart], None]] = [_check_cart_not_empty]


def _validate_checkout(session: Session, cart: CartCart) -> None:
    """Run the composable checkout checks (stock is enforced in ``create_order``)."""
    for check in _CHECKOUT_CHECKS:
        check(session, cart)


def _get_active_method(
    session: Session, store_id: uuid.UUID, method_id: uuid.UUID
) -> ShippingMethod:
    """Return the chosen active shipping method of the store, or raise 404."""
    method = session.exec(
        select(ShippingMethod).where(
            ShippingMethod.id == method_id,
            ShippingMethod.store_id == store_id,
            col(ShippingMethod.is_active).is_(True),
            col(ShippingMethod.deleted_at).is_(None),
        )
    ).first()
    if method is None:
        raise AppError(
            "shipping_method_unavailable",
            "The chosen shipping method is unavailable",
            status_code=404,
        )
    return method


def submit_checkout(
    *, session: Session, guest: CustomerGuestSession, data: CheckoutInput
) -> Order:
    """Place the order from the guest's cart (no login, no gateway).

    Validates, dedups the customer, resolves the shipping method, records a
    checkout session and creates the ``pending_payment`` order. The payment is
    arranged off-platform (``payments.get_gateway`` is a no-op in Fase 6).

    Args:
        session: Active database session.
        guest: The resolved guest session (store + cart owner).
        data: The checkout submission.

    Returns:
        The created :class:`Order`.

    Raises:
        AppError: 422 if the cart is empty / phone invalid; 404 if the shipping
            method is unavailable; 409 if stock ran out.
    """
    store_id = guest.store_id
    cart = cart_services.get_or_create_cart(
        session=session, store_id=store_id, guest_session_id=guest.guest_session_id
    )
    _validate_checkout(session, cart)
    customer = customer_services.create_or_update_customer(
        session=session,
        store_id=store_id,
        name=data.contact.name,
        email=data.contact.email,
        phone=data.contact.phone,
        region=data.contact.region,
        address=data.address,
    )
    method = _get_active_method(session, store_id, data.shipping_method_id)
    checkout = CheckoutSession(
        store_id=store_id,
        cart_id=cart.id,
        status=CheckoutStatus.active,
        expires_at=get_datetime_utc() + _CHECKOUT_TTL,
    )
    session.add(checkout)
    session.flush()
    order = order_services.create_order(
        session=session,
        cart=cart,
        customer=customer,
        address=data.address,
        shipping_method=method,
    )
    checkout.status = CheckoutStatus.completed
    checkout.order_id = order.id
    session.add(checkout)
    session.commit()
    # No gateway in Fase 6 — Fase 8 swaps this for a real charge/split/webhook.
    get_gateway().initiate(order)
    return order


def get_policies(*, session: Session, store_id: uuid.UUID) -> StoreSettings:
    """Return the store's settings (carrying the checkout policies)."""
    return store_services.get_settings(session=session, store_id=store_id)


def update_policies(
    *, session: Session, store_id: uuid.UUID, data: PoliciesUpdate
) -> StoreSettings:
    """Update the store's checkout policies (return/exchange/privacy).

    Args:
        session: Active database session.
        store_id: The store whose policies are updated.
        data: Partial policy update (only set fields apply).

    Returns:
        The store's updated settings.
    """
    settings = store_services.get_settings(session=session, store_id=store_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings
