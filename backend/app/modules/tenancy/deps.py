"""Tenancy dependency: resolve and authorize the active store for panel routes."""

import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep
from app.core.api import AppError
from app.modules.stores.enums import MembershipStatus
from app.modules.stores.models import Store, StoreMember


def get_active_store(
    store_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Store:
    """Resolve the store from the path and require an active membership.

    The single entry point for panel routes under ``/stores/{store_id}/...``
    (INV-T2/T3): instead of scattered ``store_id`` filters, every panel route
    depends on this to get the active store and validate access.

    Args:
        store_id: Store id from the ``/stores/{store_id}`` path.
        session: Active database session.
        current_user: The authenticated user.

    Returns:
        The active store the user may operate.

    Raises:
        AppError: 404 if the store does not exist (or is archived); 403 if the
            user is not an active member (no internal data leaked).
    """
    store = session.get(Store, store_id)
    if store is None or store.deleted_at is not None:
        raise AppError("store_not_found", "Store not found", status_code=404)
    membership = session.exec(
        select(StoreMember).where(
            StoreMember.store_id == store_id,
            StoreMember.user_id == current_user.id,
            StoreMember.status == MembershipStatus.active,
            col(StoreMember.deleted_at).is_(None),
        )
    ).first()
    if membership is None:
        raise AppError(
            "forbidden", "You do not have access to this store", status_code=403
        )
    return store


ActiveStore = Annotated[Store, Depends(get_active_store)]
