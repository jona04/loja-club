"""Public cart routes under ``/storefront/cart`` (guest cookie, host-resolved).

No panel auth — the store comes from the request ``Host`` and the cart from the
``guest_session_id`` cookie (both via the ``guest_session`` dependency).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import SessionDep
from app.modules.cart import services
from app.modules.cart.models import CartCart
from app.modules.cart.schemas import (
    AddItemInput,
    ApplyCouponInput,
    CartPublic,
    UpdateItemInput,
)
from app.modules.customers.deps import guest_session
from app.modules.customers.models import CustomerGuestSession

router = APIRouter(prefix="/storefront/cart", tags=["cart"])

GuestSession = Annotated[CustomerGuestSession, Depends(guest_session)]


def _resolve_cart(session: Session, guest: CustomerGuestSession) -> CartCart:
    """Return the guest's active cart for the resolved store."""
    return services.get_or_create_cart(
        session=session,
        store_id=guest.store_id,
        guest_session_id=guest.guest_session_id,
    )


@router.get("", response_model=CartPublic)
def get_cart(guest: GuestSession, session: SessionDep) -> CartPublic:
    """Return (or start) the guest's active cart for the store."""
    return services.to_public(session=session, cart=_resolve_cart(session, guest))


@router.post("/items", response_model=CartPublic)
def add_item(
    guest: GuestSession, data: AddItemInput, session: SessionDep
) -> CartPublic:
    """Add a product/variant to the cart."""
    cart = _resolve_cart(session, guest)
    services.add_item(session=session, cart=cart, data=data)
    return services.to_public(session=session, cart=cart)


@router.patch("/items/{item_id}", response_model=CartPublic)
def update_item(
    guest: GuestSession,
    item_id: uuid.UUID,
    data: UpdateItemInput,
    session: SessionDep,
) -> CartPublic:
    """Set a cart line's quantity."""
    cart = _resolve_cart(session, guest)
    services.update_item(
        session=session, cart=cart, item_id=item_id, quantity=data.quantity
    )
    return services.to_public(session=session, cart=cart)


@router.delete("/items/{item_id}", response_model=CartPublic)
def remove_item(
    guest: GuestSession, item_id: uuid.UUID, session: SessionDep
) -> CartPublic:
    """Remove a cart line."""
    cart = _resolve_cart(session, guest)
    services.remove_item(session=session, cart=cart, item_id=item_id)
    return services.to_public(session=session, cart=cart)


@router.post("/coupon", response_model=CartPublic)
def apply_coupon(
    guest: GuestSession, data: ApplyCouponInput, session: SessionDep
) -> CartPublic:
    """Apply a coupon code to the cart (422 if it does not apply)."""
    cart = _resolve_cart(session, guest)
    services.apply_coupon(session=session, cart=cart, code=data.code)
    return services.to_public(session=session, cart=cart)


@router.delete("/coupon", response_model=CartPublic)
def remove_coupon(guest: GuestSession, session: SessionDep) -> CartPublic:
    """Remove the coupon applied to the cart."""
    cart = _resolve_cart(session, guest)
    services.remove_coupon(session=session, cart=cart)
    return services.to_public(session=session, cart=cart)
