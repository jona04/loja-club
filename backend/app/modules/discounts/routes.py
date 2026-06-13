"""Discount panel routes, under ``/stores/{store_id}/discounts`` (gated ``discounts.*``).

The customer-facing application of a coupon lives in the cart module (public,
host + guest cookie). Here the merchant manages the coupon catalog.
"""

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.modules.discounts import services
from app.modules.discounts.models import DiscountCoupon
from app.modules.discounts.schemas import (
    CouponCreate,
    CouponPublic,
    CouponUpdate,
)
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/stores/{store_id}/discounts", tags=["discounts"])


@router.get(
    "/coupons",
    response_model=list[CouponPublic],
    dependencies=[Depends(require_permission("discounts.view"))],
)
def list_coupons(store_id: uuid.UUID, session: SessionDep) -> list[DiscountCoupon]:
    """List the store's coupons (newest first)."""
    return services.list_coupons(session=session, store_id=store_id)


@router.post(
    "/coupons",
    response_model=CouponPublic,
    status_code=201,
    dependencies=[Depends(require_permission("discounts.create"))],
)
def create_coupon(
    store_id: uuid.UUID, data: CouponCreate, session: SessionDep
) -> DiscountCoupon:
    """Create a coupon."""
    return services.create_coupon(session=session, store_id=store_id, data=data)


@router.patch(
    "/coupons/{coupon_id}",
    response_model=CouponPublic,
    dependencies=[Depends(require_permission("discounts.update"))],
)
def update_coupon(
    store_id: uuid.UUID,
    coupon_id: uuid.UUID,
    data: CouponUpdate,
    session: SessionDep,
) -> DiscountCoupon:
    """Apply a partial update to a coupon."""
    return services.update_coupon(
        session=session, store_id=store_id, coupon_id=coupon_id, data=data
    )


@router.delete(
    "/coupons/{coupon_id}",
    status_code=204,
    dependencies=[Depends(require_permission("discounts.delete"))],
)
def delete_coupon(
    store_id: uuid.UUID, coupon_id: uuid.UUID, session: SessionDep
) -> None:
    """Soft-delete a coupon."""
    services.delete_coupon(session=session, store_id=store_id, coupon_id=coupon_id)
