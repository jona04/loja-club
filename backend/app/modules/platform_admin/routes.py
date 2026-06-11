"""HTTP routes for platform-admin operation (admin.${DOMAIN})."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.models import Message, Token
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserPublic
from app.modules.billing import services as billing_services
from app.modules.billing.models import BillingPlan
from app.modules.billing.schemas import (
    BillingPlanCreate,
    BillingPlanPublic,
    BillingPlanUpdate,
)
from app.modules.content.models import ContentThemeTemplate
from app.modules.platform_admin import services
from app.modules.platform_admin.deps import require_platform_permission
from app.modules.platform_admin.repositories import user_platform_roles
from app.modules.platform_admin.schemas import (
    PlatformMe,
    StoreAdminDetail,
    StoreAdminListItem,
    ThemeTemplateAdminPublic,
    ThemeTemplateCreate,
    ThemeTemplateUpdate,
)
from app.modules.stores.enums import StoreStatus

router = APIRouter(prefix="/platform", tags=["platform-admin"])


@router.get("/me", response_model=PlatformMe)
def get_platform_me(current_user: CurrentUser, session: SessionDep) -> PlatformMe:
    """Return the signed-in user and their platform roles (empty if not an admin)."""
    roles = user_platform_roles(session=session, user_id=current_user.id)
    return PlatformMe(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_platform_admin=bool(roles),
        platform_roles=roles,
    )


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


@router.get(
    "/users",
    response_model=Page[UserPublic],
    dependencies=[Depends(require_platform_permission("platform.users.view"))],
)
def list_users(
    session: SessionDep,
    params: Annotated[PageParams, Depends(pagination_params)],
    search: str | None = None,
) -> Page[UserPublic]:
    """List all account users, excluding soft-deleted ones."""
    users, count = services.list_users(
        session=session, skip=params.skip, limit=params.limit, search=search
    )
    return Page(data=[UserPublic.model_validate(u) for u in users], count=count)


@router.get(
    "/users/{user_id}",
    response_model=UserPublic,
    dependencies=[Depends(require_platform_permission("platform.users.view"))],
)
def get_user(user_id: uuid.UUID, session: SessionDep) -> User:
    """Get an account user by id."""
    return services.get_user(session=session, user_id=user_id)


@router.post("/users/{user_id}/impersonate", response_model=Token)
def impersonate_user(
    user_id: uuid.UUID,
    session: SessionDep,
    actor: Annotated[
        User, Depends(require_platform_permission("platform.support.impersonate"))
    ],
) -> Token:
    """Issue an access token to act on behalf of a user (recorded)."""
    token = services.impersonate(session=session, actor=actor, user_id=user_id)
    return Token(access_token=token)


@router.get(
    "/plans",
    response_model=Page[BillingPlanPublic],
    dependencies=[Depends(require_platform_permission("platform.plans.view"))],
)
def list_plans(
    session: SessionDep,
    params: Annotated[PageParams, Depends(pagination_params)],
) -> Page[BillingPlanPublic]:
    """List the subscription plan definitions."""
    plans, count = billing_services.list_plans(
        session=session, skip=params.skip, limit=params.limit
    )
    return Page(data=[BillingPlanPublic.model_validate(p) for p in plans], count=count)


@router.get(
    "/plans/{plan_id}",
    response_model=BillingPlanPublic,
    dependencies=[Depends(require_platform_permission("platform.plans.view"))],
)
def get_plan(plan_id: uuid.UUID, session: SessionDep) -> BillingPlan:
    """Get a subscription plan definition by id."""
    return billing_services.get_plan(session=session, plan_id=plan_id)


@router.post(
    "/plans",
    response_model=BillingPlanPublic,
    status_code=201,
    dependencies=[Depends(require_platform_permission("platform.plans.update"))],
)
def create_plan(payload: BillingPlanCreate, session: SessionDep) -> BillingPlan:
    """Create a subscription plan definition."""
    return billing_services.create_plan(session=session, payload=payload)


@router.patch(
    "/plans/{plan_id}",
    response_model=BillingPlanPublic,
    dependencies=[Depends(require_platform_permission("platform.plans.update"))],
)
def update_plan(
    plan_id: uuid.UUID, payload: BillingPlanUpdate, session: SessionDep
) -> BillingPlan:
    """Update a subscription plan definition."""
    return billing_services.update_plan(
        session=session, plan_id=plan_id, payload=payload
    )


@router.delete(
    "/plans/{plan_id}",
    response_model=Message,
    dependencies=[Depends(require_platform_permission("platform.plans.update"))],
)
def delete_plan(plan_id: uuid.UUID, session: SessionDep) -> Message:
    """Soft-delete a subscription plan definition."""
    billing_services.delete_plan(session=session, plan_id=plan_id)
    return Message(message="Plan deleted")


@router.get(
    "/templates",
    response_model=list[ThemeTemplateAdminPublic],
    dependencies=[Depends(require_platform_permission("platform.templates.view"))],
)
def list_templates(session: SessionDep) -> list[ContentThemeTemplate]:
    """List the registered theme templates."""
    return services.list_templates(session=session)


@router.get(
    "/templates/{template_id}",
    response_model=ThemeTemplateAdminPublic,
    dependencies=[Depends(require_platform_permission("platform.templates.view"))],
)
def get_template(template_id: str, session: SessionDep) -> ContentThemeTemplate:
    """Get a registered theme template by id."""
    return services.get_template(session=session, template_id=template_id)


@router.post(
    "/templates",
    response_model=ThemeTemplateAdminPublic,
    status_code=201,
    dependencies=[Depends(require_platform_permission("platform.templates.manage"))],
)
def create_template(
    payload: ThemeTemplateCreate, session: SessionDep
) -> ContentThemeTemplate:
    """Register a theme template (its code must already exist in the storefront)."""
    return services.create_template(session=session, payload=payload)


@router.patch(
    "/templates/{template_id}",
    response_model=ThemeTemplateAdminPublic,
    dependencies=[Depends(require_platform_permission("platform.templates.manage"))],
)
def update_template(
    template_id: str, payload: ThemeTemplateUpdate, session: SessionDep
) -> ContentThemeTemplate:
    """Update a theme template's metadata/status."""
    return services.update_template(
        session=session, template_id=template_id, payload=payload
    )


@router.post(
    "/templates/{template_id}/thumbnail",
    response_model=ThemeTemplateAdminPublic,
    dependencies=[Depends(require_platform_permission("platform.templates.manage"))],
)
async def upload_template_thumbnail(
    template_id: str, session: SessionDep, file: UploadFile
) -> ContentThemeTemplate:
    """Upload a template's thumbnail to the CDN and link it."""
    data = await file.read()
    return services.set_template_thumbnail(
        session=session,
        template_id=template_id,
        data=data,
        content_type=file.content_type or "application/octet-stream",
    )
