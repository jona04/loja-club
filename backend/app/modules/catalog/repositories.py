"""Data access for the catalog module (store-scoped, soft-delete aware)."""

import uuid
from collections.abc import Sequence
from typing import Any, TypeVar, cast

from sqlmodel import Session, col, func, select

from app.modules.catalog.models import InventoryItem, ProductImage

T = TypeVar("T")


def list_scoped(
    session: Session,
    model: type[T],
    store_id: uuid.UUID,
    *,
    skip: int,
    limit: int,
    extra: Sequence[Any] = (),
) -> tuple[Sequence[T], int]:
    """Return a paginated, store-scoped, non-deleted list of ``model`` + the total.

    Args:
        session: Active database session.
        model: A store-scoped, soft-deletable, timestamped table model.
        store_id: The active store id.
        skip: Items to skip (offset).
        limit: Maximum items to return.
        extra: Additional SQLAlchemy filter expressions.

    Returns:
        A ``(rows, total_count)`` tuple.
    """
    scoped = cast(Any, model)
    base = select(model).where(
        scoped.store_id == store_id,
        col(scoped.deleted_at).is_(None),
        *extra,
    )
    count = session.exec(select(func.count()).select_from(base.subquery())).one()
    rows = session.exec(
        base.order_by(col(scoped.created_at).desc()).offset(skip).limit(limit)
    ).all()
    return rows, count


def active_slug_exists(
    session: Session,
    model: type[T],
    store_id: uuid.UUID,
    slug: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    """Return whether a non-deleted ``model`` row with ``slug`` exists in the store.

    Args:
        session: Active database session.
        model: A store-scoped model carrying ``slug``.
        store_id: The active store id.
        slug: The slug to check.
        exclude_id: A row id to ignore (for updates).

    Returns:
        True if a conflicting active row exists.
    """
    scoped = cast(Any, model)
    stmt = select(scoped.id).where(
        scoped.store_id == store_id,
        scoped.slug == slug,
        col(scoped.deleted_at).is_(None),
    )
    if exclude_id is not None:
        stmt = stmt.where(scoped.id != exclude_id)
    return session.exec(stmt).first() is not None


def list_product_images(
    session: Session, *, store_id: uuid.UUID, product_id: uuid.UUID
) -> Sequence[ProductImage]:
    """Return a product's non-deleted images ordered by position.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product whose images to list.

    Returns:
        The image rows, ordered by ``position`` then ``created_at``.
    """
    return session.exec(
        select(ProductImage)
        .where(
            ProductImage.store_id == store_id,
            ProductImage.product_id == product_id,
            col(ProductImage.deleted_at).is_(None),
        )
        .order_by(col(ProductImage.position), col(ProductImage.created_at))
    ).all()


def get_inventory_item(
    session: Session,
    *,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
) -> InventoryItem | None:
    """Return the non-deleted stock row for ``(product, variant)``, or None.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product id.
        variant_id: The variant id, or ``None`` for product-level stock.

    Returns:
        The matching inventory row, or ``None``.
    """
    variant_clause = (
        col(InventoryItem.variant_id).is_(None)
        if variant_id is None
        else InventoryItem.variant_id == variant_id
    )
    return session.exec(
        select(InventoryItem).where(
            InventoryItem.store_id == store_id,
            InventoryItem.product_id == product_id,
            variant_clause,
            col(InventoryItem.deleted_at).is_(None),
        )
    ).first()
