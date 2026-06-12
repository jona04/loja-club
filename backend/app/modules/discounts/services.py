"""Discount services: coupon CRUD + validation/application (doc 09).

``validate_coupon`` (raising) is used when a customer applies a coupon or checks
out; ``quote_discount`` (non-raising) feeds the cart's render. A coupon is keyed
per store by its normalized (upper-cased) code; the usage limit is enforced by
counting ``discount_coupon_redemptions``.
"""

import uuid
from datetime import datetime

from sqlmodel import Session, col, func, select

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.discounts.enums import CouponType
from app.modules.discounts.models import DiscountCoupon, DiscountCouponRedemption
from app.modules.discounts.schemas import CouponCreate, CouponUpdate


def _normalize_code(code: str) -> str:
    """Normalize a coupon code for storage/lookup (trim + upper-case)."""
    return code.strip().upper()


def _validate_value(coupon_type: CouponType, value: int) -> None:
    """Enforce a sensible value for the coupon type.

    Raises:
        AppError: 422 if a percentage is not 1..100 or a fixed amount is < 1.
    """
    if coupon_type == CouponType.percentage and not 1 <= value <= 100:
        raise AppError(
            "invalid_coupon_value",
            "A percentage coupon must be between 1 and 100",
            status_code=422,
        )
    if coupon_type == CouponType.fixed and value < 1:
        raise AppError(
            "invalid_coupon_value",
            "A fixed coupon must be a positive amount",
            status_code=422,
        )


def _active_by_code(
    session: Session, store_id: uuid.UUID, code: str
) -> DiscountCoupon | None:
    """Return the store's active (non-deleted) coupon for a code, or ``None``."""
    return session.exec(
        select(DiscountCoupon).where(
            DiscountCoupon.store_id == store_id,
            DiscountCoupon.code == code,
            col(DiscountCoupon.is_active).is_(True),
            col(DiscountCoupon.deleted_at).is_(None),
        )
    ).first()


def get_coupon(
    *, session: Session, store_id: uuid.UUID, coupon_id: uuid.UUID
) -> DiscountCoupon:
    """Return a store's coupon by id, or raise 404."""
    coupon = session.exec(
        select(DiscountCoupon).where(
            DiscountCoupon.id == coupon_id,
            DiscountCoupon.store_id == store_id,
            col(DiscountCoupon.deleted_at).is_(None),
        )
    ).first()
    if coupon is None:
        raise AppError("coupon_not_found", "Coupon not found", status_code=404)
    return coupon


def list_coupons(*, session: Session, store_id: uuid.UUID) -> list[DiscountCoupon]:
    """Return the store's non-deleted coupons (newest first)."""
    return list(
        session.exec(
            select(DiscountCoupon)
            .where(
                DiscountCoupon.store_id == store_id,
                col(DiscountCoupon.deleted_at).is_(None),
            )
            .order_by(col(DiscountCoupon.created_at).desc())
        ).all()
    )


def create_coupon(
    *, session: Session, store_id: uuid.UUID, data: CouponCreate
) -> DiscountCoupon:
    """Create a coupon for the store.

    Raises:
        AppError: 422 if the value is invalid for the type; 409 if an active
            coupon already uses the same code.
    """
    _validate_value(data.type, data.value)
    code = _normalize_code(data.code)
    if data.is_active and _active_by_code(session, store_id, code) is not None:
        raise AppError(
            "coupon_code_exists",
            "An active coupon already uses this code",
            status_code=409,
        )
    coupon = DiscountCoupon(
        store_id=store_id,
        code=code,
        type=data.type,
        value=data.value,
        min_subtotal_amount_minor=data.min_subtotal_amount_minor,
        max_redemptions=data.max_redemptions,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        is_active=data.is_active,
    )
    session.add(coupon)
    session.commit()
    session.refresh(coupon)
    return coupon


def update_coupon(
    *,
    session: Session,
    store_id: uuid.UUID,
    coupon_id: uuid.UUID,
    data: CouponUpdate,
) -> DiscountCoupon:
    """Apply a partial update to a coupon.

    Raises:
        AppError: 404 if missing; 422 if the resulting value is invalid; 409 if
            the code collides with another active coupon.
    """
    coupon = get_coupon(session=session, store_id=store_id, coupon_id=coupon_id)
    fields = data.model_dump(exclude_unset=True)
    if "code" in fields:
        fields["code"] = _normalize_code(fields["code"])
    new_type = fields.get("type", coupon.type)
    new_value = fields.get("value", coupon.value)
    _validate_value(new_type, new_value)
    new_code = fields.get("code", coupon.code)
    new_active = fields.get("is_active", coupon.is_active)
    if new_active:
        clash = _active_by_code(session, store_id, new_code)
        if clash is not None and clash.id != coupon.id:
            raise AppError(
                "coupon_code_exists",
                "An active coupon already uses this code",
                status_code=409,
            )
    for key, value in fields.items():
        setattr(coupon, key, value)
    session.add(coupon)
    session.commit()
    session.refresh(coupon)
    return coupon


def delete_coupon(
    *, session: Session, store_id: uuid.UUID, coupon_id: uuid.UUID
) -> None:
    """Soft-delete a coupon."""
    coupon = get_coupon(session=session, store_id=store_id, coupon_id=coupon_id)
    coupon.deleted_at = get_datetime_utc()
    session.add(coupon)
    session.commit()


def redemptions_count(
    *, session: Session, store_id: uuid.UUID, coupon_id: uuid.UUID
) -> int:
    """Return how many times a coupon has been redeemed."""
    return session.exec(
        select(func.count())
        .select_from(DiscountCouponRedemption)
        .where(
            DiscountCouponRedemption.store_id == store_id,
            DiscountCouponRedemption.coupon_id == coupon_id,
        )
    ).one()


def _aware(value: datetime) -> datetime:
    """Return a timezone-aware copy of a datetime (assume UTC if naive)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=get_datetime_utc().tzinfo)
    return value


def validate_coupon(
    *,
    session: Session,
    store_id: uuid.UUID,
    code: str,
    subtotal_amount_minor: int,
) -> DiscountCoupon:
    """Return the active coupon for a code, refusing it when it does not apply.

    Args:
        session: Active database session.
        store_id: The store the coupon belongs to.
        code: The (raw) coupon code the customer typed.
        subtotal_amount_minor: The cart subtotal to test the minimum against.

    Returns:
        The valid :class:`DiscountCoupon`.

    Raises:
        AppError: 422 ``invalid_coupon`` (unknown/inactive), ``coupon_not_active``
            (before ``valid_from``), ``coupon_expired`` (after ``valid_until``),
            ``coupon_below_minimum`` (subtotal below the minimum) or
            ``coupon_usage_exceeded`` (redemption limit reached).
    """
    coupon = _active_by_code(session, store_id, _normalize_code(code))
    if coupon is None:
        raise AppError("invalid_coupon", "Invalid coupon code", status_code=422)
    now = get_datetime_utc()
    if coupon.valid_from is not None and now < _aware(coupon.valid_from):
        raise AppError(
            "coupon_not_active", "This coupon is not active yet", status_code=422
        )
    if coupon.valid_until is not None and now > _aware(coupon.valid_until):
        raise AppError("coupon_expired", "This coupon has expired", status_code=422)
    if subtotal_amount_minor < coupon.min_subtotal_amount_minor:
        raise AppError(
            "coupon_below_minimum",
            "The cart does not reach this coupon's minimum",
            status_code=422,
        )
    if coupon.max_redemptions is not None:
        used = redemptions_count(
            session=session, store_id=store_id, coupon_id=coupon.id
        )
        if used >= coupon.max_redemptions:
            raise AppError(
                "coupon_usage_exceeded",
                "This coupon has reached its usage limit",
                status_code=422,
            )
    return coupon


def compute_discount(coupon: DiscountCoupon, subtotal_amount_minor: int) -> int:
    """Return the discount (minor units) a coupon yields on a subtotal.

    Args:
        coupon: The coupon to apply.
        subtotal_amount_minor: The cart subtotal.

    Returns:
        The discount, never exceeding the subtotal.
    """
    if coupon.type == CouponType.percentage:
        discount = subtotal_amount_minor * coupon.value // 100
    else:
        discount = coupon.value
    return min(discount, subtotal_amount_minor)


def quote_discount(
    *,
    session: Session,
    store_id: uuid.UUID,
    code: str | None,
    subtotal_amount_minor: int,
) -> tuple[DiscountCoupon | None, int]:
    """Return ``(coupon, discount)`` for a code, or ``(None, 0)`` — non-raising.

    Used to render the cart: a missing/expired/invalid code simply yields no
    discount instead of raising.

    Args:
        session: Active database session.
        store_id: The store the coupon belongs to.
        code: The applied coupon code, if any.
        subtotal_amount_minor: The cart subtotal.

    Returns:
        The coupon and its discount, or ``(None, 0)`` when there is no valid
        coupon for the code.
    """
    if not code:
        return None, 0
    try:
        coupon = validate_coupon(
            session=session,
            store_id=store_id,
            code=code,
            subtotal_amount_minor=subtotal_amount_minor,
        )
    except AppError:
        return None, 0
    return coupon, compute_discount(coupon, subtotal_amount_minor)


def record_redemption(
    *,
    session: Session,
    store_id: uuid.UUID,
    coupon_id: uuid.UUID,
    order_id: uuid.UUID,
    customer_id: uuid.UUID | None,
) -> None:
    """Write a redemption row for a coupon used on an order (usage limit)."""
    session.add(
        DiscountCouponRedemption(
            store_id=store_id,
            coupon_id=coupon_id,
            order_id=order_id,
            customer_id=customer_id,
        )
    )
