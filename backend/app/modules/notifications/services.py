"""Order notification emails (doc 15/16).

Renders the "order placed" (customer) and "new order" (merchant) emails and
**enqueues** them to the worker — never sends inline (INV-F5). Dispatch is
best-effort: a queue hiccup is logged and swallowed so it never fails checkout
(the order is the source of truth); the worker retries the actual send.
"""

import logging
import uuid
from collections.abc import Sequence

from sqlmodel import Session, col, select

from app.core.queue import enqueue
from app.modules.accounts.models import User
from app.modules.customers.models import CustomerProfile
from app.modules.orders.models import Order, OrderItem
from app.modules.stores.models import Store, StoreMember, StoreRole, StoreSettings
from app.utils import EmailData, render_email_template

logger = logging.getLogger(__name__)


def _money(amount_minor: int, currency: str) -> str:
    """Format a minor-unit amount with its currency for display in an email."""
    return f"{currency} {amount_minor / 100:.2f}"


def _items_context(items: Sequence[OrderItem]) -> list[dict[str, object]]:
    """Build the template rows for an order's line items."""
    return [
        {
            "name": item.name,
            "quantity": item.quantity,
            "line_total": _money(
                item.line_total_amount_minor, item.unit_price_currency
            ),
        }
        for item in items
    ]


def generate_order_placed_email(
    store_name: str, order: Order, items: Sequence[OrderItem]
) -> EmailData:
    """Build the customer's "order placed" email.

    Args:
        store_name: The store's display name.
        order: The placed order.
        items: The order's line items.

    Returns:
        The rendered customer email.
    """
    subject = f"{store_name} - Pedido #{order.order_number} recebido"
    html_content = render_email_template(
        template_name="order_placed.html",
        context={
            "store_name": store_name,
            "order_number": order.order_number,
            "items": _items_context(items),
            "total": _money(order.total_amount_minor, order.currency),
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_order_received_email(
    store_name: str,
    order: Order,
    items: Sequence[OrderItem],
    customer_name: str | None,
) -> EmailData:
    """Build the merchant's "new order" email.

    Args:
        store_name: The store's display name.
        order: The placed order.
        items: The order's line items.
        customer_name: The buyer's name, if known.

    Returns:
        The rendered merchant email.
    """
    subject = f"Novo pedido #{order.order_number}"
    html_content = render_email_template(
        template_name="order_received.html",
        context={
            "store_name": store_name,
            "order_number": order.order_number,
            "customer_name": customer_name or "Cliente",
            "items": _items_context(items),
            "total": _money(order.total_amount_minor, order.currency),
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def _merchant_email(
    session: Session, store_id: uuid.UUID, store_settings: StoreSettings | None
) -> str | None:
    """Resolve where the merchant order notification goes.

    Prefers the store's ``contact_email``; falls back to the owner's account
    email.

    Args:
        session: Active database session.
        store_id: The owning store.
        store_settings: The store's settings row, if any.

    Returns:
        The merchant recipient address, or ``None`` if it cannot be resolved.
    """
    if store_settings is not None and store_settings.contact_email:
        return store_settings.contact_email
    owner = session.exec(
        select(StoreMember)
        .join(StoreRole, col(StoreMember.role_id) == col(StoreRole.id))
        .where(
            StoreMember.store_id == store_id,
            StoreRole.key == "owner",
            col(StoreMember.deleted_at).is_(None),
        )
    ).first()
    if owner is None:
        return None
    user = session.get(User, owner.user_id)
    return user.email if user is not None else None


async def dispatch_order_emails(*, session: Session, order: Order) -> None:
    """Enqueue the customer + merchant emails for a freshly created order.

    Best-effort: any failure to render/enqueue is logged and swallowed so the
    checkout never fails because of email (INV-F5; the worker retries the send).

    Args:
        session: Active database session.
        order: The created order.
    """
    try:
        store = session.get(Store, order.store_id)
        if store is None:
            return
        store_settings = session.exec(
            select(StoreSettings).where(StoreSettings.store_id == order.store_id)
        ).first()
        store_name = (
            store_settings.public_name if store_settings else None
        ) or store.name
        items = list(
            session.exec(
                select(OrderItem).where(
                    OrderItem.order_id == order.id,
                    OrderItem.store_id == order.store_id,
                    col(OrderItem.deleted_at).is_(None),
                )
            ).all()
        )
        customer = (
            session.get(CustomerProfile, order.customer_id)
            if order.customer_id is not None
            else None
        )

        if customer is not None and customer.email:
            data = generate_order_placed_email(store_name, order, items)
            await enqueue(
                "send_order_email",
                email_to=customer.email,
                subject=data.subject,
                html_content=data.html_content,
            )

        merchant = _merchant_email(session, order.store_id, store_settings)
        if merchant:
            data = generate_order_received_email(
                store_name, order, items, customer.name if customer else None
            )
            await enqueue(
                "send_order_email",
                email_to=merchant,
                subject=data.subject,
                html_content=data.html_content,
            )
    except Exception:
        logger.exception("failed to enqueue order emails for order %s", order.id)
