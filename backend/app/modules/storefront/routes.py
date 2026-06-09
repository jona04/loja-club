"""Public storefront routes, under ``/storefront`` and resolved by ``Host``.

No panel auth: the active store comes from the request host (``get_published_store``);
an unknown/unpublished host returns "loja não encontrada" (404). Reads only.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.modules.catalog.schemas import CategoryPublic
from app.modules.content.models import ContentPage
from app.modules.content.schemas import ContentPagePublic
from app.modules.storefront import services
from app.modules.storefront.deps import get_published_store
from app.modules.storefront.schemas import StorefrontHome, StorefrontProduct
from app.modules.stores.models import Store

router = APIRouter(prefix="/storefront", tags=["storefront"])

PublishedStore = Annotated[Store, Depends(get_published_store)]
Params = Annotated[PageParams, Depends(pagination_params)]


@router.get("/home", response_model=StorefrontHome)
def get_home(store: PublishedStore, session: SessionDep) -> StorefrontHome:
    """Return the storefront home for the host's store."""
    return services.get_home(session=session, store=store)


@router.get("/categories", response_model=list[CategoryPublic])
def list_categories(store: PublishedStore, session: SessionDep) -> list[CategoryPublic]:
    """List the store's categories."""
    return services.get_categories(session=session, store=store)


@router.get("/products", response_model=Page[StorefrontProduct])
def list_products(
    store: PublishedStore, session: SessionDep, params: Params
) -> Page[StorefrontProduct]:
    """List the store's published products (paginated)."""
    items, count = services.list_products(session=session, store=store, params=params)
    return Page[StorefrontProduct](data=items, count=count)


@router.get("/products/{slug}", response_model=StorefrontProduct)
def get_product(
    store: PublishedStore, slug: str, session: SessionDep
) -> StorefrontProduct:
    """Return a published product by slug."""
    return services.get_product(session=session, store=store, slug=slug)


@router.get("/pages/{slug}", response_model=ContentPagePublic)
def get_page(store: PublishedStore, slug: str, session: SessionDep) -> ContentPage:
    """Return a published editorial page by slug."""
    return services.get_page(session=session, store=store, slug=slug)
