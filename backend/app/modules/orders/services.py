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
from app.modules.customers.schemas import AddressInput, CustomerOrderRow
from app.modules.orders.enums import OrderStatus
from app.modules.orders.models import (
    Order,
    OrderAddress,
    OrderItem,
    OrderNote,
    OrderStatusHistory,
)
from app.modules.orders.schemas import (
    OrderAddressPublic,
    OrderCustomerPublic,
    OrderDetail,
    OrderItemPublic,
    OrderNotePublic,
    OrderPublic,
    OrderStatusHistoryPublic,
    OrderSummary,
)
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod

# Statuses an order may be canceled from (shipped/delivered/canceled cannot).
_CANCELABLE = {
    OrderStatus.pending_payment,
    OrderStatus.paid,
    OrderStatus.processing,
}

# Allowed forward operational transitions (cancellation is handled separately).
_FORWARD: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.pending_payment: {OrderStatus.paid},
    OrderStatus.paid: {OrderStatus.processing},
    OrderStatus.processing: {OrderStatus.shipped},
    OrderStatus.shipped: {OrderStatus.delivered},
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


def get_order(*, session: Session, store_id: uuid.UUID, order_id: uuid.UUID) -> Order:
    """Return a store's order by id, or raise 404.

    Args:
        session: Active database session.
        store_id: The active store id.
        order_id: The order to fetch.

    Returns:
        The store-scoped :class:`Order`.

    Raises:
        AppError: 404 if the order is missing or belongs to another store.
    """
    order = session.exec(
        select(Order).where(
            Order.id == order_id,
            Order.store_id == store_id,
            col(Order.deleted_at).is_(None),
        )
    ).first()
    if order is None:
        raise AppError("order_not_found", "Order not found", status_code=404)
    return order


def list_orders(
    *,
    session: Session,
    store_id: uuid.UUID,
    status: OrderStatus | None,
    skip: int,
    limit: int,
) -> tuple[list[OrderSummary], int]:
    """Return a paginated list of the store's orders (newest first).

    Args:
        session: Active database session.
        store_id: The active store id.
        status: Optional status filter.
        skip: Offset.
        limit: Page size.

    Returns:
        A ``(summaries, total)`` tuple.
    """
    count_stmt = (
        select(func.count())
        .select_from(Order)
        .where(Order.store_id == store_id, col(Order.deleted_at).is_(None))
    )
    list_stmt = select(Order).where(
        Order.store_id == store_id, col(Order.deleted_at).is_(None)
    )
    if status is not None:
        count_stmt = count_stmt.where(Order.status == status)
        list_stmt = list_stmt.where(Order.status == status)
    total = session.exec(count_stmt).one()
    orders = list(
        session.exec(
            list_stmt.order_by(col(Order.created_at).desc()).offset(skip).limit(limit)
        ).all()
    )

    customer_ids = {o.customer_id for o in orders if o.customer_id is not None}
    names: dict[uuid.UUID, str] = {}
    if customer_ids:
        for c in session.exec(
            select(CustomerProfile).where(col(CustomerProfile.id).in_(customer_ids))
        ).all():
            names[c.id] = c.name

    counts: dict[uuid.UUID, int] = {}
    order_ids = [o.id for o in orders]
    if order_ids:
        for oid, qty in session.exec(
            select(OrderItem.order_id, func.sum(OrderItem.quantity))
            .where(
                col(OrderItem.order_id).in_(order_ids),
                col(OrderItem.deleted_at).is_(None),
            )
            .group_by(col(OrderItem.order_id))
        ).all():
            counts[oid] = int(qty or 0)

    summaries = [
        OrderSummary(
            id=o.id,
            order_number=o.order_number,
            status=o.status,
            currency=o.currency,
            total_amount_minor=o.total_amount_minor,
            item_count=counts.get(o.id, 0),
            customer_name=names.get(o.customer_id) if o.customer_id else None,
            created_at=o.created_at,
        )
        for o in orders
    ]
    return summaries, total


def get_order_detail(
    *, session: Session, store_id: uuid.UUID, order_id: uuid.UUID
) -> OrderDetail:
    """Build an order's full panel payload (customer, address, history, notes).

    Args:
        session: Active database session.
        store_id: The active store id.
        order_id: The order to represent.

    Returns:
        The :class:`OrderDetail` for the panel.

    Raises:
        AppError: 404 if the order is missing or belongs to another store.
    """
    order = get_order(session=session, store_id=store_id, order_id=order_id)
    items = _order_items(session, order)
    address = session.exec(
        select(OrderAddress).where(
            OrderAddress.order_id == order.id, OrderAddress.store_id == store_id
        )
    ).first()
    customer = (
        session.get(CustomerProfile, order.customer_id)
        if order.customer_id is not None
        else None
    )
    history = session.exec(
        select(OrderStatusHistory)
        .where(
            OrderStatusHistory.order_id == order.id,
            OrderStatusHistory.store_id == store_id,
        )
        .order_by(col(OrderStatusHistory.created_at))
    ).all()
    notes = session.exec(
        select(OrderNote)
        .where(
            OrderNote.order_id == order.id,
            OrderNote.store_id == store_id,
            col(OrderNote.deleted_at).is_(None),
        )
        .order_by(col(OrderNote.created_at))
    ).all()
    return OrderDetail(
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
        created_at=order.created_at,
        customer=(
            OrderCustomerPublic.model_validate(customer)
            if customer is not None
            else None
        ),
        address=(
            OrderAddressPublic.model_validate(address) if address is not None else None
        ),
        items=[OrderItemPublic.model_validate(item) for item in items],
        status_history=[OrderStatusHistoryPublic.model_validate(h) for h in history],
        notes=[OrderNotePublic.model_validate(n) for n in notes],
    )


def set_status(*, session: Session, order: Order, new_status: OrderStatus) -> Order:
    """Move an order one step forward in the operational chain.

    Args:
        session: Active database session.
        order: The order to transition.
        new_status: The target status (must be the next allowed step).

    Returns:
        The updated order.

    Raises:
        AppError: 409 if the transition is not allowed (use ``cancel_order`` to
            cancel).
    """
    if new_status not in _FORWARD.get(order.status, set()):
        raise AppError(
            "invalid_transition",
            f"Cannot move an order from '{order.status.value}' to '{new_status.value}'",
            status_code=409,
        )
    order.status = new_status
    session.add(order)
    session.add(
        OrderStatusHistory(
            store_id=order.store_id, order_id=order.id, status=new_status
        )
    )
    session.commit()
    session.refresh(order)
    return order


def list_orders_by_customer(
    *, session: Session, store_id: uuid.UUID, customer_id: uuid.UUID
) -> list[CustomerOrderRow]:
    """Return a customer's orders, newest first (for the customers panel).

    Args:
        session: Active database session.
        store_id: The active store id.
        customer_id: The customer whose orders are listed.

    Returns:
        The customer's order history as lean rows.
    """
    orders = session.exec(
        select(Order)
        .where(
            Order.store_id == store_id,
            Order.customer_id == customer_id,
            col(Order.deleted_at).is_(None),
        )
        .order_by(col(Order.created_at).desc())
    ).all()
    return [
        CustomerOrderRow(
            id=o.id,
            order_number=o.order_number,
            status=o.status,
            currency=o.currency,
            total_amount_minor=o.total_amount_minor,
            created_at=o.created_at,
        )
        for o in orders
    ]


def add_note(
    *,
    session: Session,
    order: Order,
    body: str,
    author_user_id: uuid.UUID | None,
) -> OrderNote:
    """Append an internal note to an order.

    Args:
        session: Active database session.
        order: The order to annotate.
        body: The note text.
        author_user_id: The member writing the note, if known.

    Returns:
        The created :class:`OrderNote`.
    """
    note = OrderNote(
        store_id=order.store_id,
        order_id=order.id,
        body=body,
        author_user_id=author_user_id,
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return note
