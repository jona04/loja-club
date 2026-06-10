"""HTTP routes for platform-admin operation (admin.${DOMAIN})."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.modules.accounts.models import User
from app.modules.platform_admin import services
from app.modules.platform_admin.deps import require_platform_permission
from app.modules.platform_admin.schemas import StoreAdminDetail, StoreAdminListItem
from app.modules.stores.enums import StoreStatus

router = APIRouter(prefix="/platform", tags=["platform-admin"])


@router.get(
    "/stores",
    response_model=Page[StoreAdminListItem],
    dependencies=[Depends(require_platform_permission("platform.stores.view"))],
)
def list_stores(
    session: SessionDep,
    params: Annotated[PageParams, Depends(pagination_params)],
    search: str | None = None,
) -> Page[StoreAdminListItem]:
    """List all stores (cross-store), excluding soft-deleted ones."""
    stores, count = services.list_stores(
        session=session, skip=params.skip, limit=params.limit, search=search
    )
    return Page(
        data=[StoreAdminListItem.model_validate(s) for s in stores], count=count
    )


@router.get(
    "/stores/{store_id}",
    response_model=StoreAdminDetail,
    dependencies=[Depends(require_platform_permission("platform.stores.view"))],
)
def get_store(store_id: uuid.UUID, session: SessionDep) -> StoreAdminDetail:
    """Get a store's admin detail (identity + settings + members)."""
    return services.get_store_detail(session=session, store_id=store_id)


@router.post("/stores/{store_id}/block", response_model=StoreAdminListItem)
def block_store(
    store_id: uuid.UUID,
    session: SessionDep,
    actor: Annotated[
        User, Depends(require_platform_permission("platform.stores.block"))
    ],
) -> StoreAdminListItem:
    """Block a store (status -> ``blocked``); the dashboard guard then bars it."""
    store = services.set_store_status(
        session=session,
        actor=actor,
        store_id=store_id,
        status=StoreStatus.blocked,
        action="platform.stores.block",
    )
    return StoreAdminListItem.model_validate(store)


@router.post("/stores/{store_id}/unblock", response_model=StoreAdminListItem)
def unblock_store(
    store_id: uuid.UUID,
    session: SessionDep,
    actor: Annotated[
        User, Depends(require_platform_permission("platform.stores.unblock"))
    ],
) -> StoreAdminListItem:
    """Unblock a store (status -> ``active``)."""
    store = services.set_store_status(
        session=session,
        actor=actor,
        store_id=store_id,
        status=StoreStatus.active,
        action="platform.stores.unblock",
    )
    return StoreAdminListItem.model_validate(store)
