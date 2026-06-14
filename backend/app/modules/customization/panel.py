"""Merchant panel operations over a store's customizations (P7-OPS-01, doc 22).

The store-facing side: list the store's sessions (near-real-time via polling),
open the full art + downloads, and advance the **production status** of an
ordered customization. Strictly store-scoped — a member only ever sees their own
store's sessions.
"""

import uuid

from sqlmodel import Session, col, select

from app.core import storage
from app.core.api import AppError
from app.modules.catalog.models import Product
from app.modules.customization import repositories, sessions
from app.modules.customization.enums import CustomizationSessionStatus
from app.modules.customization.models import (
    CustomizationOrderItem,
    CustomizationSession,
)
from app.modules.customization.schemas import (
    MerchantSessionDetail,
    MerchantSessionListItem,
    ProductionStatusUpdate,
)


def _product_names(
    *, session: Session, product_ids: set[uuid.UUID]
) -> dict[uuid.UUID, str]:
    """Return a ``{product_id: name}`` map for the given products."""
    if not product_ids:
        return {}
    rows = session.exec(
        select(Product.id, Product.name).where(col(Product.id).in_(product_ids))
    ).all()
    return {row[0]: row[1] for row in rows}


def list_sessions(
    *,
    session: Session,
    store_id: uuid.UUID,
    status: CustomizationSessionStatus | None,
    skip: int,
    limit: int,
) -> tuple[list[MerchantSessionListItem], int]:
    """List the store's customization sessions for the panel (newest first).

    Args:
        session: Active database session.
        store_id: The active store id.
        status: Optional session-status filter.
        skip: Offset.
        limit: Page size.

    Returns:
        A ``(items, total)`` tuple; ``production_status`` is set only for the
        sessions that were frozen into an order.
    """
    rows, total = repositories.list_store_sessions(
        session=session, store_id=store_id, status=status, skip=skip, limit=limit
    )
    names = _product_names(session=session, product_ids={r.product_id for r in rows})
    order_items = {
        oi.customization_session_id: oi
        for oi in repositories.list_order_items_by_sessions(
            session=session, store_id=store_id, session_ids=[r.id for r in rows]
        )
    }
    items = [
        MerchantSessionListItem(
            id=r.id,
            product_id=r.product_id,
            product_name=names.get(r.product_id, "—"),
            status=r.status,
            is_assisted=r.created_by_user_id is not None,
            snapshot_url=(
                storage.generate_presigned_url(r.snapshot_key)
                if r.snapshot_key
                else None
            ),
            created_at=r.created_at,
            updated_at=r.updated_at,
            approved_at=r.approved_at,
            order_id=order_items[r.id].order_id if r.id in order_items else None,
            order_item_id=(
                order_items[r.id].order_item_id if r.id in order_items else None
            ),
            production_status=(
                order_items[r.id].production_status if r.id in order_items else None
            ),
        )
        for r in rows
    ]
    return items, total


def _detail(
    *,
    session: Session,
    obj: CustomizationSession,
    order_item: CustomizationOrderItem | None,
) -> MerchantSessionDetail:
    """Build the merchant detail DTO from a session + its order item (if any)."""
    public = sessions.view_session(session=session, obj=obj)
    names = _product_names(session=session, product_ids={public.product_id})
    return MerchantSessionDetail(
        **public.model_dump(),
        product_name=names.get(public.product_id, "—"),
        is_assisted=obj.created_by_user_id is not None,
        order_id=order_item.order_id if order_item else None,
        order_item_id=order_item.order_item_id if order_item else None,
        production_status=order_item.production_status if order_item else None,
    )


def get_session_detail(
    *, session: Session, store_id: uuid.UUID, session_id: uuid.UUID
) -> MerchantSessionDetail:
    """Return a store session's full art + downloads + order link.

    Args:
        session: Active database session.
        store_id: The active store id.
        session_id: The customization session id.

    Returns:
        The detail DTO (with presigned snapshot/composite/upload URLs).

    Raises:
        AppError: 404 if the session is missing or belongs to another store.
    """
    obj = repositories.get_session(
        session=session, store_id=store_id, session_id=session_id
    )
    if obj is None:
        raise AppError("not_found", "Customization session not found", status_code=404)
    order_item = repositories.get_order_item_by_session(
        session=session, store_id=store_id, session_id=session_id
    )
    return _detail(session=session, obj=obj, order_item=order_item)


def update_production_status(
    *,
    session: Session,
    store_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: ProductionStatusUpdate,
) -> MerchantSessionDetail:
    """Advance the production status of an ordered customization.

    Args:
        session: Active database session.
        store_id: The active store id.
        session_id: The customization session id (its frozen order item is set).
        payload: The new production status.

    Returns:
        The updated detail DTO.

    Raises:
        AppError: 404 if the session is missing; 422 ``not_ordered`` if it has
            not been frozen into a placed order yet.
    """
    obj = repositories.get_session(
        session=session, store_id=store_id, session_id=session_id
    )
    if obj is None:
        raise AppError("not_found", "Customization session not found", status_code=404)
    order_item = repositories.get_order_item_by_session(
        session=session, store_id=store_id, session_id=session_id
    )
    if order_item is None:
        raise AppError(
            "not_ordered",
            "This customization is not in a placed order yet",
            status_code=422,
        )
    order_item.production_status = payload.production_status
    session.add(order_item)
    session.commit()
    session.refresh(order_item)
    return _detail(session=session, obj=obj, order_item=order_item)
