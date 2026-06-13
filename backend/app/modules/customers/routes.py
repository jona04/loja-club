"""Customer panel routes, under ``/stores/{store_id}/customers`` (gated ``customers.*``).

Read-only in this phase: the merchant lists/searches customers and opens one to
see the profile, saved addresses and order history. Customers are created by the
public checkout (``P6-CUST-01``); editing/LGPD export are later phases.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.modules.customers import repositories as repo
from app.modules.customers import services
from app.modules.customers.schemas import (
    CustomerAddressPublic,
    CustomerDetail,
    CustomerSummary,
)
from app.modules.orders import services as order_services
from app.modules.tenancy.deps import require_permission

Params = Annotated[PageParams, Depends(pagination_params)]

router = APIRouter(prefix="/stores/{store_id}/customers", tags=["customers"])


@router.get(
    "",
    response_model=Page[CustomerSummary],
    dependencies=[Depends(require_permission("customers.view"))],
)
def list_customers(
    store_id: uuid.UUID,
    session: SessionDep,
    params: Params,
    search: Annotated[str | None, Query()] = None,
) -> Page[CustomerSummary]:
    """List the store's customers (newest first), optionally filtered by search."""
    summaries, count = services.list_customers(
        session=session,
        store_id=store_id,
        search=search,
        skip=params.skip,
        limit=params.limit,
    )
    return Page(data=summaries, count=count)


@router.get(
    "/{customer_id}",
    response_model=CustomerDetail,
    dependencies=[Depends(require_permission("customers.view"))],
)
def get_customer(
    store_id: uuid.UUID, customer_id: uuid.UUID, session: SessionDep
) -> CustomerDetail:
    """Get a customer's profile, saved addresses and order history."""
    customer = services.get_customer(
        session=session, store_id=store_id, customer_id=customer_id
    )
    addresses = repo.list_addresses(
        session=session, store_id=store_id, customer_id=customer_id
    )
    orders = order_services.list_orders_by_customer(
        session=session, store_id=store_id, customer_id=customer_id
    )
    return CustomerDetail(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone_e164=customer.phone_e164,
        created_at=customer.created_at,
        addresses=[CustomerAddressPublic.model_validate(a) for a in addresses],
        orders=orders,
    )
