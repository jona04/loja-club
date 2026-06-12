"""Shipping services: panel CRUD + the active-methods read for checkout.

Store-scoped: every method is fetched by ``(store_id, id)`` so one store never
reaches another's. ``list_active_methods`` feeds the public checkout.
"""

import uuid

from sqlmodel import Session, col, select

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.shipping.schemas import ShippingMethodCreate, ShippingMethodUpdate


def _get_method(
    session: Session, store_id: uuid.UUID, method_id: uuid.UUID
) -> ShippingMethod:
    """Return a store's active method by id, or raise 404."""
    method = session.exec(
        select(ShippingMethod).where(
            ShippingMethod.id == method_id,
            ShippingMethod.store_id == store_id,
            col(ShippingMethod.deleted_at).is_(None),
        )
    ).first()
    if method is None:
        raise AppError(
            "shipping_method_not_found", "Shipping method not found", status_code=404
        )
    return method


def _validate_amounts(
    method_type: ShippingMethodType, price_amount_minor: int | None
) -> None:
    """Enforce that a ``fixed_shipping`` method carries a price.

    Raises:
        AppError: 422 if a fixed method has no ``price_amount_minor``.
    """
    if method_type == ShippingMethodType.fixed_shipping and price_amount_minor is None:
        raise AppError(
            "invalid_shipping_method",
            "A fixed shipping method requires a price",
            status_code=422,
        )


def list_methods(*, session: Session, store_id: uuid.UUID) -> list[ShippingMethod]:
    """Return all of the store's active methods (panel).

    Args:
        session: Active database session.
        store_id: The owning store.

    Returns:
        The store's non-deleted :class:`ShippingMethod` rows.
    """
    return list(
        session.exec(
            select(ShippingMethod).where(
                ShippingMethod.store_id == store_id,
                col(ShippingMethod.deleted_at).is_(None),
            )
        ).all()
    )


def list_active_methods(
    *, session: Session, store_id: uuid.UUID
) -> list[ShippingMethod]:
    """Return the store's **active** methods (public checkout).

    Args:
        session: Active database session.
        store_id: The owning store.

    Returns:
        The store's active, non-deleted :class:`ShippingMethod` rows.
    """
    return list(
        session.exec(
            select(ShippingMethod).where(
                ShippingMethod.store_id == store_id,
                col(ShippingMethod.is_active).is_(True),
                col(ShippingMethod.deleted_at).is_(None),
            )
        ).all()
    )


def create_method(
    *, session: Session, store_id: uuid.UUID, data: ShippingMethodCreate
) -> ShippingMethod:
    """Create a shipping method.

    Args:
        session: Active database session.
        store_id: The owning store.
        data: The method payload.

    Returns:
        The created method.

    Raises:
        AppError: 422 if a fixed method has no price.
    """
    _validate_amounts(data.type, data.price_amount_minor)
    method = ShippingMethod(store_id=store_id, **data.model_dump())
    session.add(method)
    session.commit()
    session.refresh(method)
    return method


def update_method(
    *,
    session: Session,
    store_id: uuid.UUID,
    method_id: uuid.UUID,
    data: ShippingMethodUpdate,
) -> ShippingMethod:
    """Update a shipping method (``type`` is immutable).

    Args:
        session: Active database session.
        store_id: The owning store.
        method_id: The method to update.
        data: Partial update (only set fields apply).

    Returns:
        The updated method.

    Raises:
        AppError: 404 if the method is missing; 422 if a fixed method ends
            without a price.
    """
    method = _get_method(session, store_id, method_id)
    fields = data.model_dump(exclude_unset=True)
    price = fields.get("price_amount_minor", method.price_amount_minor)
    _validate_amounts(method.type, price)
    for key, value in fields.items():
        setattr(method, key, value)
    session.add(method)
    session.commit()
    session.refresh(method)
    return method


def delete_method(
    *, session: Session, store_id: uuid.UUID, method_id: uuid.UUID
) -> None:
    """Soft-delete a shipping method.

    Args:
        session: Active database session.
        store_id: The owning store.
        method_id: The method to delete.

    Raises:
        AppError: 404 if the method is missing.
    """
    method = _get_method(session, store_id, method_id)
    method.deleted_at = get_datetime_utc()
    session.add(method)
    session.commit()
