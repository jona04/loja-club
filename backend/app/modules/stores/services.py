"""Store services: creation (atomic), slug, status and membership management."""

import re
import uuid

from sqlmodel import Session, select

from app.core.api import AppError
from app.core.config import settings
from app.db.base import get_datetime_utc
from app.modules.accounts.models import User
from app.modules.accounts.repositories import get_user_by_email
from app.modules.domains.services import (
    create_platform_subdomain,
    is_subdomain_available,
)
from app.modules.stores.enums import MembershipStatus, StoreStatus
from app.modules.stores.models import Store, StoreMember, StoreSettings
from app.modules.stores.repositories import get_membership, get_role_by_key
from app.modules.stores.schemas import (
    StoreCreate,
    StoreMemberInvite,
    StoreMemberPublic,
    StoreMemberRoleUpdate,
    StoreSettingsUpdate,
)


def slugify(value: str) -> str:
    """Turn a name into a DNS-safe slug (lowercase ``a-z0-9`` joined by hyphens).

    Args:
        value: The source text (e.g. the store name).

    Returns:
        The slug, possibly empty if ``value`` has no ASCII alphanumerics.
    """
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def create_store(*, session: Session, owner: User, payload: StoreCreate) -> Store:
    """Create a store with its settings, owner membership and subdomain (atomic).

    Args:
        session: Active database session.
        owner: The account user creating the store (becomes ``owner``).
        payload: Store creation data.

    Returns:
        The created store.

    Raises:
        AppError: 422 if no slug can be derived; 409 if the subdomain is taken.
    """
    slug = payload.slug or slugify(payload.name)
    if not slug:
        raise AppError("invalid_slug", "Could not derive a slug; provide one", 422)
    if not is_subdomain_available(session=session, slug=slug):
        raise AppError("slug_taken", "This subdomain is already taken", 409)
    owner_role = get_role_by_key(session=session, key="owner")
    if owner_role is None:  # pragma: no cover - roles are seeded by init_db
        raise AppError("role_missing", "owner role is not seeded", 500)

    store = Store(
        name=payload.name,
        slug=slug,
        status=StoreStatus.draft,
        currency=payload.currency or settings.PLATFORM_DEFAULT_CURRENCY,
        locale=payload.locale or settings.PLATFORM_DEFAULT_LOCALE,
    )
    session.add(store)
    session.flush()
    session.add(StoreSettings(store_id=store.id))
    session.add(
        StoreMember(
            store_id=store.id,
            user_id=owner.id,
            role_id=owner_role.id,
            status=MembershipStatus.active,
        )
    )
    create_platform_subdomain(session=session, store_id=store.id, slug=slug)
    session.commit()
    session.refresh(store)
    return store


def get_settings(*, session: Session, store_id: uuid.UUID) -> StoreSettings:
    """Return a store's settings.

    Args:
        session: Active database session.
        store_id: The store whose settings to fetch.

    Returns:
        The store's settings.

    Raises:
        AppError: 404 if the settings row is missing.
    """
    settings_row = session.exec(
        select(StoreSettings).where(StoreSettings.store_id == store_id)
    ).first()
    if settings_row is None:  # pragma: no cover - created with the store
        raise AppError("settings_missing", "Store settings not found", 404)
    return settings_row


def update_settings(
    *, session: Session, store_id: uuid.UUID, payload: StoreSettingsUpdate
) -> StoreSettings:
    """Apply a partial update to a store's settings.

    Args:
        session: Active database session.
        store_id: The store whose settings are updated.
        payload: Fields to change (unset fields are ignored).

    Returns:
        The updated settings.
    """
    settings_row = session.exec(
        select(StoreSettings).where(StoreSettings.store_id == store_id)
    ).first()
    if settings_row is None:  # pragma: no cover - created with the store
        raise AppError("settings_missing", "Store settings not found", 404)
    settings_row.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(settings_row)
    session.commit()
    session.refresh(settings_row)
    return settings_row


def set_store_published(
    *, session: Session, store_id: uuid.UUID, published: bool
) -> Store:
    """Publish (active) or pause a store, keeping ``is_published`` consistent.

    Args:
        session: Active database session.
        store_id: The store to update.
        published: True to publish (active), False to pause.

    Returns:
        The updated store.
    """
    store = session.get(Store, store_id)
    if store is None:  # pragma: no cover - validated by the route dependency
        raise AppError("store_not_found", "Store not found", 404)
    store.status = StoreStatus.active if published else StoreStatus.paused
    settings_row = session.exec(
        select(StoreSettings).where(StoreSettings.store_id == store_id)
    ).first()
    if settings_row is not None:
        settings_row.is_published = published
        session.add(settings_row)
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def invite_member(
    *, session: Session, store_id: uuid.UUID, payload: StoreMemberInvite
) -> StoreMemberPublic:
    """Invite an existing account user to the store with a role (status invited).

    Args:
        session: Active database session.
        store_id: The store to add the member to.
        payload: Invite email + role key.

    Returns:
        The created membership (public view).

    Raises:
        AppError: 422 for an unknown role; 404 if no account has that email
            (full email onboarding is deferred); 409 if already a member.
    """
    role = get_role_by_key(session=session, key=payload.role)
    if role is None:
        raise AppError("invalid_role", f"Unknown role: {payload.role}", 422)
    user = get_user_by_email(session=session, email=payload.email)
    if user is None:
        raise AppError("user_not_found", "No account with that email", 404)
    if get_membership(session=session, store_id=store_id, user_id=user.id) is not None:
        raise AppError("already_member", "User is already a member", 409)
    member = StoreMember(
        store_id=store_id,
        user_id=user.id,
        role_id=role.id,
        status=MembershipStatus.invited,
        invited_at=get_datetime_utc(),
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return StoreMemberPublic(
        id=member.id,
        user_id=user.id,
        email=user.email,
        role=role.key,
        status=member.status,
    )


def change_member_role(
    *,
    session: Session,
    store_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: StoreMemberRoleUpdate,
) -> StoreMemberPublic:
    """Change a member's role.

    Args:
        session: Active database session.
        store_id: The store.
        user_id: The member's user id.
        payload: New role key.

    Returns:
        The updated membership (public view).

    Raises:
        AppError: 422 unknown role; 404 if the user is not a member.
    """
    role = get_role_by_key(session=session, key=payload.role)
    if role is None:
        raise AppError("invalid_role", f"Unknown role: {payload.role}", 422)
    member = get_membership(session=session, store_id=store_id, user_id=user_id)
    if member is None:
        raise AppError("member_not_found", "Member not found", 404)
    member.role_id = role.id
    session.add(member)
    session.commit()
    session.refresh(member)
    user = session.get(User, user_id)
    assert user is not None  # FK guarantees the user exists
    return StoreMemberPublic(
        id=member.id,
        user_id=user_id,
        email=user.email,
        role=role.key,
        status=member.status,
    )


def remove_member(
    *,
    session: Session,
    store_id: uuid.UUID,
    user_id: uuid.UUID,
    removed_by: uuid.UUID,
) -> None:
    """Soft-delete a membership (status removed).

    Args:
        session: Active database session.
        store_id: The store.
        user_id: The member's user id.
        removed_by: The acting user's id.

    Raises:
        AppError: 404 if the user is not a member.
    """
    member = get_membership(session=session, store_id=store_id, user_id=user_id)
    if member is None:
        raise AppError("member_not_found", "Member not found", 404)
    now = get_datetime_utc()
    member.status = MembershipStatus.removed
    member.removed_at = now
    member.deleted_at = now
    member.deleted_by_user_id = removed_by
    session.add(member)
    session.commit()
