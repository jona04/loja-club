"""Tenancy dependencies: active-store resolution and permission enforcement."""

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, col, select

from app.api.deps import CurrentUser, SessionDep
from app.core.api import AppError
from app.modules.stores.enums import MembershipStatus
from app.modules.stores.models import (
    Store,
    StoreMember,
    StorePermission,
    StoreRolePermission,
)


def get_active_membership(
    store_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> StoreMember:
    """Validate the active store and the user's active membership; return it.

    Args:
        store_id: Store id from the ``/stores/{store_id}`` path.
        session: Active database session.
        current_user: The authenticated user.

    Returns:
        The user's active membership in the store.

    Raises:
        AppError: 404 if the store does not exist/is archived; 403 if the user
            is not an active member (no internal data leaked).
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
    return membership


def get_active_store(
    store_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Store:
    """Resolve the active store, requiring the user to be an active member.

    The single entry point for panel routes under ``/stores/{store_id}/...``
    (INV-T2/T3).

    Args:
        store_id: Store id from the path.
        session: Active database session.
        current_user: The authenticated user.

    Returns:
        The active store the user may operate.
    """
    get_active_membership(store_id=store_id, session=session, current_user=current_user)
    store = session.get(Store, store_id)
    if store is None:  # pragma: no cover - guaranteed by get_active_membership
        raise AppError("store_not_found", "Store not found", status_code=404)
    return store


ActiveStore = Annotated[Store, Depends(get_active_store)]


def _role_grants(*, session: Session, role_id: uuid.UUID, permission: str) -> bool:
    """Return whether ``role_id`` is granted ``permission`` (store_role_permissions).

    Args:
        session: Active database session.
        role_id: The member's role id.
        permission: The permission key to check.

    Returns:
        True if the role grants the permission.
    """
    grant = session.exec(
        select(StoreRolePermission)
        .join(
            StorePermission,
            col(StorePermission.id) == col(StoreRolePermission.permission_id),
        )
        .where(
            StoreRolePermission.role_id == role_id,
            StorePermission.key == permission,
        )
    ).first()
    return grant is not None


def _plan_allows() -> bool:
    """Plan-gating hook (Phase 5). No-op in the MVP: every plan allows everything.

    Returns:
        Always True in the MVP. Phase 5 expands this to consult the store's plan
        for the requested feature.
    """
    return True


def require_permission(permission: str) -> Callable[..., StoreMember]:
    """Build a dependency that authorizes ``permission`` on the active store.

    Validates (doc 08): authenticated -> active member -> role grants the
    permission -> plan allows it (Phase 5 hook). Authorization is enforced in
    the backend regardless of what the frontend shows (INV-A4/S1).

    Args:
        permission: Required permission key (e.g. ``catalog.product.update``).

    Returns:
        A FastAPI dependency that returns the authorized membership.
    """

    def _require(
        membership: Annotated[StoreMember, Depends(get_active_membership)],
        session: SessionDep,
    ) -> StoreMember:
        if not _role_grants(
            session=session, role_id=membership.role_id, permission=permission
        ):
            raise AppError("forbidden", "Missing permission", status_code=403)
        if not _plan_allows():  # pragma: no cover - Phase 5 hook
            raise AppError("plan_required", "Plan does not allow this", status_code=403)
        return membership

    return _require
