"""HTTP routes for the catalog (panel), under ``/stores/{store_id}/...``.

All endpoints are gated by ``catalog.*`` permissions and operate only on the
active store's data (INV-T2). Lists use the shared ``Page`` envelope.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep
from app.core.api import Page, PageParams, pagination_params
from app.modules.catalog import services
from app.modules.catalog.models import (
    Category,
    InventoryItem,
    Product,
    ProductVariant,
)
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryPublic,
    CategoryUpdate,
    ImageAttach,
    ImagePublic,
    InventoryPublic,
    InventorySet,
    ProductCreate,
    ProductPublic,
    ProductUpdate,
    VariantCreate,
    VariantPublic,
    VariantUpdate,
)
from app.modules.stores.models import StoreMember
from app.modules.tenancy.deps import require_permission

router = APIRouter(prefix="/stores/{store_id}", tags=["catalog"])

Params = Annotated[PageParams, Depends(pagination_params)]

# --- Products ---


@router.get(
    "/products",
    response_model=Page[ProductPublic],
    dependencies=[Depends(require_permission("catalog.product.view"))],
)
def list_products(
    store_id: uuid.UUID, session: SessionDep, params: Params
) -> Page[ProductPublic]:
    """List the store's products (paginated)."""
    products, count = services.list_products(
        session=session, store_id=store_id, skip=params.skip, limit=params.limit
    )
    return Page(data=[ProductPublic.model_validate(p) for p in products], count=count)


@router.post(
    "/products",
    response_model=ProductPublic,
    status_code=201,
    dependencies=[Depends(require_permission("catalog.product.create"))],
)
def create_product(
    store_id: uuid.UUID, payload: ProductCreate, session: SessionDep
) -> Product:
    """Create a draft product."""
    return services.create_product(session=session, store_id=store_id, payload=payload)


@router.get(
    "/products/{product_id}",
    response_model=ProductPublic,
    dependencies=[Depends(require_permission("catalog.product.view"))],
)
def get_product(
    store_id: uuid.UUID, product_id: uuid.UUID, session: SessionDep
) -> Product:
    """Get a product by id."""
    return services.get_product(
        session=session, store_id=store_id, product_id=product_id
    )


@router.patch(
    "/products/{product_id}",
    response_model=ProductPublic,
    dependencies=[Depends(require_permission("catalog.product.update"))],
)
def update_product(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: ProductUpdate,
    session: SessionDep,
) -> Product:
    """Apply a partial update to a product."""
    return services.update_product(
        session=session, store_id=store_id, product_id=product_id, payload=payload
    )


@router.post(
    "/products/{product_id}/publish",
    response_model=ProductPublic,
    dependencies=[Depends(require_permission("catalog.product.update"))],
)
def publish_product(
    store_id: uuid.UUID, product_id: uuid.UUID, session: SessionDep
) -> Product:
    """Publish a product."""
    return services.set_product_published(
        session=session, store_id=store_id, product_id=product_id, published=True
    )


@router.post(
    "/products/{product_id}/unpublish",
    response_model=ProductPublic,
    dependencies=[Depends(require_permission("catalog.product.update"))],
)
def unpublish_product(
    store_id: uuid.UUID, product_id: uuid.UUID, session: SessionDep
) -> Product:
    """Unpublish a product (back to draft)."""
    return services.set_product_published(
        session=session, store_id=store_id, product_id=product_id, published=False
    )


@router.post(
    "/products/{product_id}/archive",
    response_model=ProductPublic,
)
def archive_product(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    session: SessionDep,
    member: Annotated[
        StoreMember, Depends(require_permission("catalog.product.archive"))
    ],
) -> Product:
    """Archive a product (soft delete)."""
    return services.archive_product(
        session=session,
        store_id=store_id,
        product_id=product_id,
        archived_by=member.user_id,
    )


# --- Categories ---


@router.get(
    "/categories",
    response_model=Page[CategoryPublic],
    dependencies=[Depends(require_permission("catalog.view"))],
)
def list_categories(
    store_id: uuid.UUID, session: SessionDep, params: Params
) -> Page[CategoryPublic]:
    """List the store's categories (paginated)."""
    categories, count = services.list_categories(
        session=session, store_id=store_id, skip=params.skip, limit=params.limit
    )
    return Page(
        data=[CategoryPublic.model_validate(c) for c in categories], count=count
    )


@router.post(
    "/categories",
    response_model=CategoryPublic,
    status_code=201,
    dependencies=[Depends(require_permission("catalog.category.manage"))],
)
def create_category(
    store_id: uuid.UUID, payload: CategoryCreate, session: SessionDep
) -> Category:
    """Create a category."""
    return services.create_category(session=session, store_id=store_id, payload=payload)


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryPublic,
    dependencies=[Depends(require_permission("catalog.category.manage"))],
)
def update_category(
    store_id: uuid.UUID,
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    session: SessionDep,
) -> Category:
    """Apply a partial update to a category."""
    return services.update_category(
        session=session, store_id=store_id, category_id=category_id, payload=payload
    )


@router.post("/categories/{category_id}/archive", status_code=204)
def archive_category(
    store_id: uuid.UUID,
    category_id: uuid.UUID,
    session: SessionDep,
    member: Annotated[
        StoreMember, Depends(require_permission("catalog.category.manage"))
    ],
) -> None:
    """Archive (soft-delete) a category."""
    services.archive_category(
        session=session,
        store_id=store_id,
        category_id=category_id,
        archived_by=member.user_id,
    )


# --- Variants ---


@router.get(
    "/products/{product_id}/variants",
    response_model=Page[VariantPublic],
    dependencies=[Depends(require_permission("catalog.product.view"))],
)
def list_variants(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    session: SessionDep,
    params: Params,
) -> Page[VariantPublic]:
    """List a product's variants (paginated)."""
    variants, count = services.list_variants(
        session=session,
        store_id=store_id,
        product_id=product_id,
        skip=params.skip,
        limit=params.limit,
    )
    return Page(data=[VariantPublic.model_validate(v) for v in variants], count=count)


@router.post(
    "/products/{product_id}/variants",
    response_model=VariantPublic,
    status_code=201,
    dependencies=[Depends(require_permission("catalog.product.update"))],
)
def create_variant(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: VariantCreate,
    session: SessionDep,
) -> ProductVariant:
    """Create a variant under a product."""
    return services.create_variant(
        session=session, store_id=store_id, product_id=product_id, payload=payload
    )


@router.patch(
    "/products/{product_id}/variants/{variant_id}",
    response_model=VariantPublic,
    dependencies=[Depends(require_permission("catalog.product.update"))],
)
def update_variant(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID,
    payload: VariantUpdate,
    session: SessionDep,
) -> ProductVariant:
    """Apply a partial update to a variant."""
    return services.update_variant(
        session=session,
        store_id=store_id,
        product_id=product_id,
        variant_id=variant_id,
        payload=payload,
    )


@router.post("/products/{product_id}/variants/{variant_id}/archive", status_code=204)
def archive_variant(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID,
    session: SessionDep,
    member: Annotated[
        StoreMember, Depends(require_permission("catalog.product.update"))
    ],
) -> None:
    """Archive (soft-delete) a variant."""
    services.archive_variant(
        session=session,
        store_id=store_id,
        product_id=product_id,
        variant_id=variant_id,
        archived_by=member.user_id,
    )


# --- Images ---


@router.get(
    "/products/{product_id}/images",
    response_model=list[ImagePublic],
    dependencies=[Depends(require_permission("catalog.product.view"))],
)
def list_images(
    store_id: uuid.UUID, product_id: uuid.UUID, session: SessionDep
) -> list[ImagePublic]:
    """List a product's images (ordered by position)."""
    return services.list_images(
        session=session, store_id=store_id, product_id=product_id
    )


@router.post(
    "/products/{product_id}/images",
    response_model=ImagePublic,
    status_code=201,
    dependencies=[Depends(require_permission("catalog.product.update"))],
)
def attach_image(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: ImageAttach,
    session: SessionDep,
) -> ImagePublic:
    """Link a media file to a product."""
    return services.attach_image(
        session=session, store_id=store_id, product_id=product_id, payload=payload
    )


@router.delete("/products/{product_id}/images/{image_id}", status_code=204)
def remove_image(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    image_id: uuid.UUID,
    session: SessionDep,
    member: Annotated[
        StoreMember, Depends(require_permission("catalog.product.update"))
    ],
) -> None:
    """Remove (soft-delete) a product image link."""
    services.remove_image(
        session=session,
        store_id=store_id,
        product_id=product_id,
        image_id=image_id,
        removed_by=member.user_id,
    )


# --- Inventory ---


@router.put(
    "/products/{product_id}/inventory",
    response_model=InventoryPublic,
    dependencies=[Depends(require_permission("catalog.inventory.update"))],
)
def set_inventory(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: InventorySet,
    session: SessionDep,
) -> InventoryItem:
    """Set the stock quantity for a product (optionally a variant)."""
    return services.set_inventory(
        session=session, store_id=store_id, product_id=product_id, payload=payload
    )
