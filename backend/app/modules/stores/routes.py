"""HTTP routes for store lifecycle and team management (panel)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.models import Message
from app.modules.stores import repositories, services
from app.modules.stores.models import Store, StoreMember, StoreRole, StoreSettings
from app.modules.stores.schemas import (
    MyMembership,
    StoreCreate,
    StoreMemberInvite,
    StoreMemberPublic,
    StoreMemberRoleUpdate,
    StorePublic,
    StoreSettingsPublic,
    StoreSettingsUpdate,
)
from app.modules.tenancy.deps import (
    ActiveStore,
    get_active_membership,
    require_permission,
)

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("/", response_model=StorePublic, status_code=201)
def create_store(
    payload: StoreCreate, session: SessionDep, current_user: CurrentUser
) -> Store:
    """Create a store; the caller becomes its owner (+ subdomain)."""
    return services.create_store(session=session, owner=current_user, payload=payload)


@router.get("/", response_model=Page[StorePublic])
def list_my_stores(
    session: SessionDep,
    current_user: CurrentUser,
    params: Annotated[PageParams, Depends(pagination_params)],
) -> Page[StorePublic]:
    """List the stores the current user is an active member of."""
    stores, count = repositories.list_my_stores(
        session=session,
        user_id=current_user.id,
        skip=params.skip,
        limit=params.limit,
    )
    return Page(data=[StorePublic.model_validate(s) for s in stores], count=count)


@router.get("/{store_id}", response_model=StorePublic)
def get_store(store: ActiveStore) -> Store:
    """Get a store the current user can access."""
    return store


@router.get("/{store_id}/me", response_model=MyMembership)
def get_my_membership(
    membership: Annotated[StoreMember, Depends(get_active_membership)],
    session: SessionDep,
) -> MyMembership:
    """Return the current user's role and permissions in the active store."""
    role = session.get(StoreRole, membership.role_id)
    assert role is not None  # FK guarantees the role exists
    permissions = repositories.role_permission_keys(
        session=session, role_id=membership.role_id
    )
    return MyMembership(role=role.key, permissions=permissions)


@router.patch(
    "/{store_id}/settings",
    response_model=StoreSettingsPublic,
    dependencies=[Depends(require_permission("settings.update"))],
)
def update_store_settings(
    store_id: uuid.UUID, payload: StoreSettingsUpdate, session: SessionDep
) -> StoreSettings:
    """Update the store's settings (requires ``settings.update``)."""
    return services.update_settings(session=session, store_id=store_id, payload=payload)


@router.post(
    "/{store_id}/publish",
    response_model=StorePublic,
    dependencies=[Depends(require_permission("settings.update"))],
)
def publish_store(store_id: uuid.UUID, session: SessionDep) -> Store:
    """Publish the store (status active; requires ``settings.update``)."""
    return services.set_store_published(
        session=session, store_id=store_id, published=True
    )


@router.post(
    "/{store_id}/pause",
    response_model=StorePublic,
    dependencies=[Depends(require_permission("settings.update"))],
)
def pause_store(store_id: uuid.UUID, session: SessionDep) -> Store:
    """Pause the store (status paused; requires ``settings.update``)."""
    return services.set_store_published(
        session=session, store_id=store_id, published=False
    )


@router.get(
    "/{store_id}/members",
    response_model=Page[StoreMemberPublic],
    dependencies=[Depends(require_permission("team.view"))],
)
def list_store_members(
    store_id: uuid.UUID,
    session: SessionDep,
    params: Annotated[PageParams, Depends(pagination_params)],
) -> Page[StoreMemberPublic]:
    """List the store's members (requires ``team.view``)."""
    members, count = repositories.list_members(
        session=session, store_id=store_id, skip=params.skip, limit=params.limit
    )
    return Page(data=members, count=count)


@router.post(
    "/{store_id}/members",
    response_model=StoreMemberPublic,
    status_code=201,
    dependencies=[Depends(require_permission("team.invite"))],
)
def invite_store_member(
    store_id: uuid.UUID, payload: StoreMemberInvite, session: SessionDep
) -> StoreMemberPublic:
    """Invite an existing account user to the store (requires ``team.invite``)."""
    return services.invite_member(session=session, store_id=store_id, payload=payload)


@router.patch(
    "/{store_id}/members/{user_id}",
    response_model=StoreMemberPublic,
    dependencies=[Depends(require_permission("team.update_role"))],
)
def update_store_member_role(
    store_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: StoreMemberRoleUpdate,
    session: SessionDep,
) -> StoreMemberPublic:
    """Change a member's role (requires ``team.update_role``)."""
    return services.change_member_role(
        session=session, store_id=store_id, user_id=user_id, payload=payload
    )


@router.delete(
    "/{store_id}/members/{user_id}",
    response_model=Message,
    dependencies=[Depends(require_permission("team.remove"))],
)
def remove_store_member(
    store_id: uuid.UUID,
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """Remove (soft-delete) a member (requires ``team.remove``)."""
    services.remove_member(
        session=session,
        store_id=store_id,
        user_id=user_id,
        removed_by=current_user.id,
    )
    return Message(message="Member removed")
