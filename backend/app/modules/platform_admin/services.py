"""Platform-admin services: cross-store operation.

Operates stores **across tenants** (no ``store_id`` scope), so it deliberately
bypasses the per-store guard — but still excludes soft-deleted stores from admin
reads. Sensitive actions (block/unblock) are recorded in ``audit_logs``.
"""

import uuid
from datetime import timedelta

from sqlalchemy import ColumnElement, func, or_
from sqlmodel import Session, col, select

from app.core.api import AppError
from app.core.config import settings
from app.core.security import create_access_token
from app.modules.accounts.models import User
from app.modules.accounts.repositories import get_active_user
from app.modules.audit.services import record_audit
from app.modules.platform_admin.schemas import StoreAdminDetail
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store, StoreMember, StoreRole, StoreSettings
from app.modules.stores.schemas import StoreMemberPublic, StoreSettingsPublic


def list_stores(
    *, session: Session, skip: int, limit: int, search: str | None = None
) -> tuple[list[Store], int]:
    """List all stores (cross-store), excluding soft-deleted ones.

    Args:
        session: Active database session.
        skip: Pagination offset.
        limit: Pagination page size.
        search: Optional case-insensitive filter on name/slug.

    Returns:
        A ``(stores, total_count)`` tuple for the current page.
    """
    conditions: list[ColumnElement[bool]] = [col(Store.deleted_at).is_(None)]
    if search:
        like = f"%{search}%"
        conditions.append(or_(col(Store.name).ilike(like), col(Store.slug).ilike(like)))
    count = session.exec(
        select(func.count()).select_from(Store).where(*conditions)
    ).one()
    stores = session.exec(
        select(Store)
        .where(*conditions)
        .order_by(col(Store.created_at).desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return list(stores), count


def _get_store(*, session: Session, store_id: uuid.UUID) -> Store:
    """Load a store for admin use, excluding soft-deleted ones.

    Args:
        session: Active database session.
        store_id: The store id.

    Returns:
        The store.

    Raises:
        AppError: 404 if the store does not exist or is soft-deleted.
    """
    store = session.get(Store, store_id)
    if store is None or store.deleted_at is not None:
        raise AppError("store_not_found", "Store not found", status_code=404)
    return store


def get_store_detail(*, session: Session, store_id: uuid.UUID) -> StoreAdminDetail:
    """Return a store's admin detail: identity + settings + members.

    Args:
        session: Active database session.
        store_id: The store id.

    Returns:
        The store's admin detail.

    Raises:
        AppError: 404 if the store does not exist or is soft-deleted.
    """
    store = _get_store(session=session, store_id=store_id)
    settings = session.exec(
        select(StoreSettings).where(StoreSettings.store_id == store_id)
    ).first()
    rows = session.exec(
        select(StoreMember, User.email, StoreRole.key)
        .join(User, col(User.id) == col(StoreMember.user_id))
        .join(StoreRole, col(StoreRole.id) == col(StoreMember.role_id))
        .where(
            StoreMember.store_id == store_id,
            col(StoreMember.deleted_at).is_(None),
        )
    ).all()
    members = [
        StoreMemberPublic(
            id=member.id,
            user_id=member.user_id,
            email=email,
            role=role_key,
            status=member.status,
        )
        for member, email, role_key in rows
    ]
    return StoreAdminDetail(
        id=store.id,
        name=store.name,
        slug=store.slug,
        status=store.status,
        created_at=store.created_at,
        settings=StoreSettingsPublic.model_validate(settings) if settings else None,
        members=members,
    )


def set_store_status(
    *,
    session: Session,
    actor: User,
    store_id: uuid.UUID,
    status: StoreStatus,
    action: str,
) -> Store:
    """Change a store's status (block/unblock) and record the action.

    Args:
        session: Active database session.
        actor: The platform user performing the action (for the audit trail).
        store_id: The store id.
        status: The new store status.
        action: The audit action key (e.g. ``platform.stores.block``).

    Returns:
        The updated store.

    Raises:
        AppError: 404 if the store does not exist or is soft-deleted.
    """
    store = _get_store(session=session, store_id=store_id)
    store.status = status
    record_audit(
        session=session,
        user_id=actor.id,
        action=action,
        store_id=store_id,
        target_type="store",
        target_id=str(store_id),
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def list_users(
    *, session: Session, skip: int, limit: int, search: str | None = None
) -> tuple[list[User], int]:
    """List all account users, excluding soft-deleted ones.

    Args:
        session: Active database session.
        skip: Pagination offset.
        limit: Pagination page size.
        search: Optional case-insensitive filter on email.

    Returns:
        A ``(users, total_count)`` tuple for the current page.
    """
    conditions: list[ColumnElement[bool]] = [col(User.deleted_at).is_(None)]
    if search:
        conditions.append(col(User.email).ilike(f"%{search}%"))
    count = session.exec(
        select(func.count()).select_from(User).where(*conditions)
    ).one()
    users = session.exec(
        select(User)
        .where(*conditions)
        .order_by(col(User.created_at).desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return list(users), count


def get_user(*, session: Session, user_id: uuid.UUID) -> User:
    """Return an account user by id, excluding soft-deleted ones.

    Args:
        session: Active database session.
        user_id: The user id.

    Returns:
        The user.

    Raises:
        AppError: 404 if the user does not exist or is soft-deleted.
    """
    user = get_active_user(session=session, user_id=user_id)
    if user is None:
        raise AppError("user_not_found", "User not found", status_code=404)
    return user


def impersonate(*, session: Session, actor: User, user_id: uuid.UUID) -> str:
    """Issue an access token to act on behalf of another user, recording it.

    Args:
        session: Active database session.
        actor: The platform user performing the impersonation.
        user_id: The user to impersonate.

    Returns:
        A signed access token whose subject is the impersonated user.

    Raises:
        AppError: 404 if the target user does not exist or is soft-deleted.
    """
    target = get_active_user(session=session, user_id=user_id)
    if target is None:
        raise AppError("user_not_found", "User not found", status_code=404)
    record_audit(
        session=session,
        user_id=actor.id,
        action="platform.support.impersonate",
        target_type="user",
        target_id=str(user_id),
    )
    session.commit()
    return create_access_token(
        target.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
