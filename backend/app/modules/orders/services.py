"""Order services: create an order from a cart, and cancel it (doc 11).

``create_order`` freezes the cart into an immutable order (price/variant/name per
item), **decrements stock**, generates the per-store ``order_number`` and records
the initial ``pending_payment`` status. The per-item freeze (``_freeze_item``) is
the seam Fase 7 uses to also copy the approved customization. ``cancel_order``
restocks. No gateway — the order stops at ``pending_payment``.
"""

import uuid

from sqlmodel import Session, col, func, select

from app.core.api import AppError
from app.modules.cart.enums import CartStatus
from app.modules.cart.models import CartCart, CartItem
from app.modules.catalog.models import InventoryItem, Product
from app.modules.customers.models import CustomerProfile
from app.modules.customers.schemas import AddressInput
from app.modules.orders.enums import OrderStatus
from app.modules.orders.models import (
    Order,
    OrderAddress,
    OrderItem,
    OrderStatusHistory,
)
from app.modules.orders.schemas import OrderItemPublic, OrderPublic
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod

# Statuses an order may be canceled from (shipped/delivered/canceled cannot).
_CANCELABLE = {
    OrderStatus.pending_payment,
    OrderStatus.paid,
    OrderStatus.processing,
}


def _cart_items(session: Session, cart: CartCart) -> list[CartItem]:
    """Return the cart's active items, oldest first."""
    return list(
        session.exec(
            select(CartItem)
            .where(
                CartItem.cart_id == cart.id,
                CartItem.store_id == cart.store_id,
                col(CartItem.deleted_at).is_(None),
            )
            .order_by(col(CartItem.created_at))
        ).all()
    )


def _order_items(session: Session, order: Order) -> list[OrderItem]:
    """Return an order's line items."""
    return list(
        session.exec(
            select(OrderItem).where(
                OrderItem.order_id == order.id,
                OrderItem.store_id == order.store_id,
                col(OrderItem.deleted_at).is_(None),
            )
        ).all()
    )


def _inventory_row(
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
) -> InventoryItem | None:
    """Return the inventory row for a product/variant, or ``None`` if untracked."""
    variant_cond = (
        InventoryItem.variant_id == variant_id
        if variant_id is not None
        else col(InventoryItem.variant_id).is_(None)
    )
    return session.exec(
        select(InventoryItem).where(
            InventoryItem.store_id == store_id,
            InventoryItem.product_id == product_id,
            variant_cond,
            col(InventoryItem.deleted_at).is_(None),
        )
    ).first()


def _decrement_stock(
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
    quantity: int,
) -> None:
    """Decrement tracked stock; untracked products are not limited.

    Raises:
        AppError: 409 if the tracked stock is below the requested quantity.
    """
    item = _inventory_row(session, store_id, product_id, variant_id)
    if item is None:
        return
    if item.quantity < quantity:
        raise AppError(
            "insufficient_stock",
            f"Only {item.quantity} left in stock",
            status_code=409,
        )
    item.quantity -= quantity
    session.add(item)


def _restock(
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
    quantity: int,
) -> None:
    """Give tracked stock back (on cancel)."""
    item = _inventory_row(session, store_id, product_id, variant_id)
    if item is not None:
        item.quantity += quantity
        session.add(item)


def _next_order_number(session: Session, store_id: uuid.UUID) -> int:
    """Return the next sequential ``order_number`` for the store."""
    current = session.exec(
        select(func.max(Order.order_number)).where(Order.store_id == store_id)
    ).one()
    return (current or 0) + 1


def _shipping_cost(method: ShippingMethod) -> int:
    """Return the shipping fee for a method (flat for fixed, else free)."""
    if method.type == ShippingMethodType.fixed_shipping:
        return method.price_amount_minor or 0
    return 0


def _freeze_item(session: Session, order: Order, item: CartItem) -> None:
    """Freeze a cart line into an order line (immutable snapshot).

    Fase 7 extends this to also copy the approved customization into
    ``customization_order_items`` for the same order item.
    """
    product = session.get(Product, item.product_id)
    session.add(
        OrderItem(
            store_id=order.store_id,
            order_id=order.id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            name=product.name if product else "",
            quantity=item.quantity,
            unit_price_amount_minor=item.unit_price_amount_minor,
            unit_price_currency=item.unit_price_currency,
            line_total_amount_minor=item.unit_price_amount_minor * item.quantity,
        )
    )


def create_order(
    *,
    session: Session,
    cart: CartCart,
    customer: CustomerProfile,
    address: AddressInput,
    shipping_method: ShippingMethod,
    discount_amount_minor: int = 0,
) -> Order:
    """Turn a cart into a ``pending_payment`` order (no gateway).

    Re-validates and **decrements** stock, freezes each line (price + variant +
    name), generates the per-store ``order_number``, snapshots the address, writes
    the initial status, and marks the cart ``converted``.

    Args:
        session: Active database session.
        cart: The active cart being checked out.
        customer: The deduplicated customer (``P6-CUST-01``).
        address: The delivery address to snapshot.
        shipping_method: The chosen shipping method.
        discount_amount_minor: A coupon discount (``P6-DISC-01``); 0 for now.

    Returns:
        The created :class:`Order`.

    Raises:
        AppError: 422 if the cart is empty; 409 if stock ran out since add.
    """
    items = _cart_items(session, cart)
    if not items:
        raise AppError("empty_cart", "The cart is empty", status_code=422)
    for item in items:
        _decrement_stock(
            session, cart.store_id, item.product_id, item.variant_id, item.quantity
        )
    subtotal = sum(item.unit_price_amount_minor * item.quantity for item in items)
    shipping = _shipping_cost(shipping_method)
    total = max(0, subtotal + shipping - discount_amount_minor)
    order = Order(
        store_id=cart.store_id,
        order_number=_next_order_number(session, cart.store_id),
        status=OrderStatus.pending_payment,
        customer_id=customer.id,
        guest_session_id=cart.guest_session_id,
        shipping_method_type=shipping_method.type,
        shipping_method_name=shipping_method.name,
        subtotal_amount_minor=subtotal,
        shipping_amount_minor=shipping,
        discount_amount_minor=discount_amount_minor,
        total_amount_minor=total,
        currency=items[0].unit_price_currency,
    )
    session.add(order)
    session.flush()
    for item in items:
        _freeze_item(session, order, item)
    session.add(
        OrderAddress(store_id=cart.store_id, order_id=order.id, **address.model_dump())
    )
    session.add(
        OrderStatusHistory(
            store_id=cart.store_id,
            order_id=order.id,
            status=OrderStatus.pending_payment,
        )
    )
    cart.status = CartStatus.converted
    session.add(cart)
    session.commit()
    session.refresh(order)
    return order


def cancel_order(*, session: Session, order: Order) -> Order:
    """Cancel an order and give its stock back.

    Args:
        session: Active database session.
        order: The order to cancel.

    Returns:
        The canceled order.

    Raises:
        AppError: 409 if the order's status does not allow cancellation.
    """
    if order.status not in _CANCELABLE:
        raise AppError(
            "cannot_cancel",
            f"An order in '{order.status.value}' cannot be canceled",
            status_code=409,
        )
    for item in _order_items(session, order):
        _restock(
            session, order.store_id, item.product_id, item.variant_id, item.quantity
        )
    order.status = OrderStatus.canceled
    session.add(order)
    session.add(
        OrderStatusHistory(
            store_id=order.store_id, order_id=order.id, status=OrderStatus.canceled
        )
    )
    session.commit()
    session.refresh(order)
    return order


def order_to_public(*, session: Session, order: Order) -> OrderPublic:
    """Build an order's public payload (with its items).

    Args:
        session: Active database session.
        order: The order to represent.

    Returns:
        The :class:`OrderPublic` (order + items), for the confirmation/panel.
    """
    items = _order_items(session, order)
    return OrderPublic(
        id=order.id,
        order_number=order.order_number,
        status=order.status,
        currency=order.currency,
        subtotal_amount_minor=order.subtotal_amount_minor,
        shipping_amount_minor=order.shipping_amount_minor,
        discount_amount_minor=order.discount_amount_minor,
        total_amount_minor=order.total_amount_minor,
        shipping_method_type=order.shipping_method_type,
        shipping_method_name=order.shipping_method_name,
        items=[OrderItemPublic.model_validate(item) for item in items],
    )
