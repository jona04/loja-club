"""Shipping panel routes, under ``/stores/{store_id}/shipping`` (gated ``shipping.*``).

The public read consumed by the checkout (active methods, host-resolved) lives in
the storefront module.
"""

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.modules.shipping import services
from app.modules.shipping.models import ShippingMethod
from app.modules.shipping.schemas import (
    ShippingMethodCreate,
    ShippingMethodPublic,
    ShippingMethodUpdate,
)
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/stores/{store_id}/shipping", tags=["shipping"])


@router.get(
    "/methods",
    response_model=list[ShippingMethodPublic],
    dependencies=[Depends(require_permission("shipping.view"))],
)
def list_methods(store_id: uuid.UUID, session: SessionDep) -> list[ShippingMethod]:
    """List the store's shipping methods."""
    return services.list_methods(session=session, store_id=store_id)


@router.post(
    "/methods",
    response_model=ShippingMethodPublic,
    dependencies=[Depends(require_permission("shipping.create"))],
)
def create_method(
    store_id: uuid.UUID, data: ShippingMethodCreate, session: SessionDep
) -> ShippingMethod:
    """Create a shipping method."""
    return services.create_method(session=session, store_id=store_id, data=data)


@router.patch(
    "/methods/{method_id}",
    response_model=ShippingMethodPublic,
    dependencies=[Depends(require_permission("shipping.update"))],
)
def update_method(
    store_id: uuid.UUID,
    method_id: uuid.UUID,
    data: ShippingMethodUpdate,
    session: SessionDep,
) -> ShippingMethod:
    """Update a shipping method."""
    return services.update_method(
        session=session, store_id=store_id, method_id=method_id, data=data
    )


@router.delete(
    "/methods/{method_id}",
    status_code=204,
    dependencies=[Depends(require_permission("shipping.delete"))],
)
def delete_method(
    store_id: uuid.UUID, method_id: uuid.UUID, session: SessionDep
) -> None:
    """Soft-delete a shipping method."""
    services.delete_method(session=session, store_id=store_id, method_id=method_id)
