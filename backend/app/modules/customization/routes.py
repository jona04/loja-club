"""Routes for the platform 3D catalog, product links and customization sessions.

Three surfaces: the global catalog browse (``/3d-catalog``, authenticated); the
store panel (``/stores/{store_id}/...``, permission-gated) for linking models and
assembling assisted sessions; and the public storefront (``/storefront/...``,
guest cookie or a session ``public_token``) that drives the customer editor.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.modules.customers.deps import guest_session
from app.modules.customers.models import CustomerGuestSession
from app.modules.customization import services, sessions
from app.modules.customization.schemas import (
    AssistedSessionCreate,
    AssistedSessionPublic,
    ContactConfirm,
    Platform3DModelPublic,
    ProductModelLink,
    ProductModelSettingsPublic,
    SessionPublic,
    SessionStart,
    StateJson,
    UploadPublic,
)
from app.modules.stores.models import StoreMember
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/3d-catalog", tags=["3d-catalog"])

panel_router = APIRouter(prefix="/stores/{store_id}", tags=["customization"])

storefront_router = APIRouter(prefix="/storefront", tags=["customization"])

GuestSession = Annotated[CustomerGuestSession, Depends(guest_session)]


@router.get("/models", response_model=list[Platform3DModelPublic])
def list_models(
    session: SessionDep, _current_user: CurrentUser
) -> list[Platform3DModelPublic]:
    """List the active catalog models with their active version.

    Args:
        session: Active database session.
        _current_user: The authenticated user (browse requires login).

    Returns:
        The active catalog models.
    """
    return services.list_catalog(session=session)


@panel_router.get(
    "/products/{product_id}/3d-model",
    response_model=ProductModelSettingsPublic | None,
    dependencies=[Depends(require_permission("customization.view"))],
)
def get_product_model(
    store_id: uuid.UUID, product_id: uuid.UUID, session: SessionDep
) -> ProductModelSettingsPublic | None:
    """Return the product's current 3D-model link (``None`` if unlinked)."""
    return services.get_product_model(
        session=session, store_id=store_id, product_id=product_id
    )


@panel_router.put(
    "/products/{product_id}/3d-model",
    response_model=ProductModelSettingsPublic,
    dependencies=[Depends(require_permission("customization.models.assign"))],
)
def link_product_model(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: ProductModelLink,
    session: SessionDep,
) -> ProductModelSettingsPublic:
    """Link a product to a catalog 3D model and set its 3D ``type``."""
    return services.link_product_model(
        session=session, store_id=store_id, product_id=product_id, payload=payload
    )


@panel_router.delete("/products/{product_id}/3d-model", status_code=204)
def unlink_product_model(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    session: SessionDep,
    member: Annotated[
        StoreMember, Depends(require_permission("customization.models.assign"))
    ],
) -> None:
    """Unlink the product's 3D model (reverts ``type`` to ``image``)."""
    services.unlink_product_model(
        session=session,
        store_id=store_id,
        product_id=product_id,
        unlinked_by=member.user_id,
    )


@panel_router.post(
    "/customizations/assisted",
    response_model=AssistedSessionPublic,
    status_code=201,
)
def create_assisted_session(
    store_id: uuid.UUID,
    payload: AssistedSessionCreate,
    session: SessionDep,
    member: Annotated[
        StoreMember, Depends(require_permission("customization.sessions.view"))
    ],
) -> AssistedSessionPublic:
    """Assemble a session for a customer and return its public link token."""
    return sessions.create_assisted_session(
        session=session,
        store_id=store_id,
        created_by=member.user_id,
        payload=payload,
    )


# --- Public storefront: the customer editor (guest cookie) ---


@storefront_router.post(
    "/customizations", response_model=SessionPublic, status_code=201
)
def start_session(
    payload: SessionStart, guest: GuestSession, session: SessionDep
) -> SessionPublic:
    """Start (or resume) the guest's customization session for a product."""
    return sessions.start_session(
        session=session,
        store_id=guest.store_id,
        product_id=payload.product_id,
        guest_session_id=guest.guest_session_id,
    )


@storefront_router.get("/customizations/{session_id}", response_model=SessionPublic)
def get_session(
    session_id: uuid.UUID, guest: GuestSession, session: SessionDep
) -> SessionPublic:
    """Return the guest's customization session."""
    obj = sessions.get_guest_session(
        session=session,
        store_id=guest.store_id,
        session_id=session_id,
        guest_session_id=guest.guest_session_id,
    )
    return sessions.view_session(session=session, obj=obj)


@storefront_router.put(
    "/customizations/{session_id}/state", response_model=SessionPublic
)
def autosave_session(
    session_id: uuid.UUID,
    payload: StateJson,
    guest: GuestSession,
    session: SessionDep,
) -> SessionPublic:
    """Autosave the editor state (validated against the pinned version)."""
    obj = sessions.get_guest_session(
        session=session,
        store_id=guest.store_id,
        session_id=session_id,
        guest_session_id=guest.guest_session_id,
    )
    return sessions.autosave(session=session, obj=obj, state=payload)


@storefront_router.post(
    "/customizations/{session_id}/uploads",
    response_model=UploadPublic,
    status_code=201,
)
async def upload_art(
    session_id: uuid.UUID,
    guest: GuestSession,
    session: SessionDep,
    file: UploadFile,
) -> UploadPublic:
    """Upload raster art to the session (stored privately, presigned back)."""
    obj = sessions.get_guest_session(
        session=session,
        store_id=guest.store_id,
        session_id=session_id,
        guest_session_id=guest.guest_session_id,
    )
    data = await file.read()
    return sessions.add_upload(
        session=session,
        obj=obj,
        data=data,
        content_type=file.content_type or "application/octet-stream",
    )


@storefront_router.post(
    "/customizations/{session_id}/approve", response_model=SessionPublic
)
async def approve_session(
    session_id: uuid.UUID,
    guest: GuestSession,
    session: SessionDep,
    snapshot: UploadFile,
) -> SessionPublic:
    """Approve the session with the client-side snapshot (freezes it)."""
    obj = sessions.get_guest_session(
        session=session,
        store_id=guest.store_id,
        session_id=session_id,
        guest_session_id=guest.guest_session_id,
    )
    data = await snapshot.read()
    return sessions.approve_session(
        session=session,
        obj=obj,
        snapshot_data=data,
        snapshot_content_type=snapshot.content_type or "application/octet-stream",
    )


# --- Public link: read-only view + approve by confirming contact (§9) ---


@storefront_router.get("/p/{token}", response_model=SessionPublic)
def view_public_session(token: str, session: SessionDep) -> SessionPublic:
    """Open a shared session read-only via its public token."""
    return sessions.view_public_session(session=session, token=token)


@storefront_router.post("/p/{token}/approve", response_model=SessionPublic)
async def approve_public_session(
    token: str,
    session: SessionDep,
    snapshot: UploadFile,
    email: Annotated[str | None, Form()] = None,
    phone: Annotated[str | None, Form()] = None,
    region: Annotated[str | None, Form()] = None,
) -> SessionPublic:
    """Approve a shared session after confirming the pre-registered contact."""
    data = await snapshot.read()
    return sessions.approve_via_token(
        session=session,
        token=token,
        contact=ContactConfirm(email=email, phone=phone, region=region),
        snapshot_data=data,
        snapshot_content_type=snapshot.content_type or "application/octet-stream",
    )
