"""Order panel routes, under ``/stores/{store_id}/orders`` (gated ``orders.*``).

The merchant lists and opens orders, marks payment received manually (no
gateway), advances the operational status, cancels (restocking) and writes
internal notes. Orders are created by the public checkout (``P6-CHK-01``).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.modules.orders import services
from app.modules.orders.enums import OrderStatus
from app.modules.orders.schemas import (
    OrderDetail,
    OrderNoteCreate,
    OrderNotePublic,
    OrderStatusUpdate,
    OrderSummary,
)
from app.modules.tenancy.deps import require_permission

Params = Annotated[PageParams, Depends(pagination_params)]

router = APIRouter(prefix="/stores/{store_id}/orders", tags=["orders"])


@router.get(
    "",
    response_model=Page[OrderSummary],
    dependencies=[Depends(require_permission("orders.view"))],
)
def list_orders(
    store_id: uuid.UUID,
    session: SessionDep,
    params: Params,
    status: Annotated[OrderStatus | None, Query()] = None,
) -> Page[OrderSummary]:
    """List the store's orders (newest first), optionally filtered by status."""
    summaries, count = services.list_orders(
        session=session,
        store_id=store_id,
        status=status,
        skip=params.skip,
        limit=params.limit,
    )
    return Page(data=summaries, count=count)


@router.get(
    "/{order_id}",
    response_model=OrderDetail,
    dependencies=[Depends(require_permission("orders.view"))],
)
def get_order(
    store_id: uuid.UUID, order_id: uuid.UUID, session: SessionDep
) -> OrderDetail:
    """Get an order's full detail (customer, address, items, history, notes)."""
    return services.get_order_detail(
        session=session, store_id=store_id, order_id=order_id
    )


@router.patch(
    "/{order_id}/status",
    response_model=OrderDetail,
    dependencies=[Depends(require_permission("orders.update_status"))],
)
def update_status(
    store_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    session: SessionDep,
) -> OrderDetail:
    """Advance the order one step (e.g. mark payment received: → ``paid``)."""
    order = services.get_order(session=session, store_id=store_id, order_id=order_id)
    services.set_status(session=session, order=order, new_status=data.status)
    return services.get_order_detail(
        session=session, store_id=store_id, order_id=order_id
    )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderDetail,
    dependencies=[Depends(require_permission("orders.cancel"))],
)
def cancel_order(
    store_id: uuid.UUID, order_id: uuid.UUID, session: SessionDep
) -> OrderDetail:
    """Cancel an order (when allowed), giving its stock back."""
    order = services.get_order(session=session, store_id=store_id, order_id=order_id)
    services.cancel_order(session=session, order=order)
    return services.get_order_detail(
        session=session, store_id=store_id, order_id=order_id
    )


@router.post(
    "/{order_id}/notes",
    response_model=OrderNotePublic,
    status_code=201,
    dependencies=[Depends(require_permission("orders.add_note"))],
)
def add_note(
    store_id: uuid.UUID,
    order_id: uuid.UUID,
    data: OrderNoteCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> OrderNotePublic:
    """Write an internal note on the order."""
    order = services.get_order(session=session, store_id=store_id, order_id=order_id)
    note = services.add_note(
        session=session,
        order=order,
        body=data.body,
        author_user_id=current_user.id,
    )
    return OrderNotePublic.model_validate(note)
