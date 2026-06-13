"""Routes for the platform 3D catalog and product 3D-model links.

The catalog (``/3d-catalog``) is global (platform-owned), so it is not
store-scoped: any authenticated user can browse the active models to pick one.
Linking a model to a product is store-scoped (``/stores/{store_id}/...``) and
gated by ``customization.models.assign``.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, SessionDep
from app.modules.customization import services
from app.modules.customization.schemas import (
    Platform3DModelPublic,
    ProductModelLink,
    ProductModelSettingsPublic,
)
from app.modules.stores.models import StoreMember
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/3d-catalog", tags=["3d-catalog"])

panel_router = APIRouter(prefix="/stores/{store_id}", tags=["customization"])


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
