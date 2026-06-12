"""Checkout routes: the public storefront submit + the panel policies.

The submit (``/storefront/checkout``) is public (host + guest cookie); the
policies (``/stores/{store_id}/checkout/policies``) are panel, gated ``checkout.*``.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.modules.checkout import services
from app.modules.checkout.schemas import (
    CheckoutInput,
    PoliciesPublic,
    PoliciesUpdate,
)
from app.modules.customers.deps import guest_session
from app.modules.customers.models import CustomerGuestSession
from app.modules.orders import services as order_services
from app.modules.orders.schemas import OrderPublic
from app.modules.stores.models import StoreSettings
from app.modules.tenancy.deps import require_permission

GuestSession = Annotated[CustomerGuestSession, Depends(guest_session)]

# --- Public: place the order ---
public_router = APIRouter(prefix="/storefront/checkout", tags=["checkout"])


@public_router.post("", response_model=OrderPublic)
def submit_checkout(
    guest: GuestSession, data: CheckoutInput, session: SessionDep
) -> OrderPublic:
    """Place the order from the cart (no login, no gateway) and return it."""
    order = services.submit_checkout(session=session, guest=guest, data=data)
    return order_services.order_to_public(session=session, order=order)


# --- Panel: store checkout policies ---
router = APIRouter(prefix="/stores/{store_id}/checkout", tags=["checkout"])


@router.get(
    "/policies",
    response_model=PoliciesPublic,
    dependencies=[Depends(require_permission("checkout.view"))],
)
def get_policies(store_id: uuid.UUID, session: SessionDep) -> StoreSettings:
    """Return the store's checkout policies."""
    return services.get_policies(session=session, store_id=store_id)


@router.patch(
    "/policies",
    response_model=PoliciesPublic,
    dependencies=[Depends(require_permission("checkout.policies.update"))],
)
def update_policies(
    store_id: uuid.UUID, data: PoliciesUpdate, session: SessionDep
) -> StoreSettings:
    """Update the store's checkout policies (return/exchange/privacy)."""
    return services.update_policies(session=session, store_id=store_id, data=data)
