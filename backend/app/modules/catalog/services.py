"""Catalog services: products, categories, variants, images and inventory.

Every operation is store-scoped: resources are fetched by ``(store_id, id)`` via
``get_store_scoped`` (INV-T2), so one store can never reach another's data.
"""

import uuid
from collections.abc import Sequence

from sqlmodel import Session

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.catalog import repositories as repo
from app.modules.catalog.enums import ProductStatus, ProductVariantStatus
from app.modules.catalog.models import (
    Category,
    InventoryItem,
    Product,
    ProductImage,
    ProductVariant,
)
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ImageAttach,
    ImagePublic,
    InventorySet,
    ProductCreate,
    ProductUpdate,
    VariantCreate,
    VariantUpdate,
)
from app.modules.media.models import MediaFile
from app.modules.stores.models import Store
from app.modules.stores.services import slugify
from app.modules.tenancy.services import get_store_scoped


def _resolve_slug(
    session: Session,
    model: type[Product] | type[Category],
    store_id: uuid.UUID,
    *,
    name: str,
    slug: str | None,
    exclude_id: uuid.UUID | None = None,
) -> str:
    """Derive/validate a unique active slug for ``model`` in the store.

    Args:
        session: Active database session.
        model: The slugged model (``Product`` or ``Category``).
        store_id: The active store id.
        name: The source name (used when ``slug`` is omitted).
        slug: An explicit slug, or ``None`` to derive from ``name``.
        exclude_id: Row id to ignore (for updates).

    Returns:
        The validated slug.

    Raises:
        AppError: 422 if no slug can be derived; 409 if it is already in use.
    """
    candidate = slug or slugify(name)
    if not candidate:
        raise AppError("invalid_slug", "Could not derive a slug; provide one", 422)
    if repo.active_slug_exists(
        session, model, store_id, candidate, exclude_id=exclude_id
    ):
        raise AppError("slug_taken", "This slug is already in use in the store", 409)
    return candidate


# --- Products ---


def get_product(
    *, session: Session, store_id: uuid.UUID, product_id: uuid.UUID
) -> Product:
    """Return a store's product by id, or raise 404.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product id.

    Returns:
        The product.

    Raises:
        AppError: 404 if not found in the store.
    """
    product = get_store_scoped(
        session=session, model=Product, store_id=store_id, resource_id=product_id
    )
    if product is None:
        raise AppError("product_not_found", "Product not found", 404)
    return product


def list_products(
    *, session: Session, store_id: uuid.UUID, skip: int, limit: int
) -> tuple[Sequence[Product], int]:
    """Return a paginated list of the store's products.

    Args:
        session: Active database session.
        store_id: The active store id.
        skip: Offset.
        limit: Page size.

    Returns:
        A ``(products, total)`` tuple.
    """
    return repo.list_scoped(session, Product, store_id, skip=skip, limit=limit)


def create_product(
    *, session: Session, store_id: uuid.UUID, payload: ProductCreate
) -> Product:
    """Create a draft product (slug derived; currency inherited from the store).

    Args:
        session: Active database session.
        store_id: The active store id.
        payload: Product creation data.

    Returns:
        The created product.

    Raises:
        AppError: 422 invalid slug; 409 slug already in use.
    """
    store = session.get(Store, store_id)
    assert store is not None  # validated by the route dependency
    slug = _resolve_slug(
        session, Product, store_id, name=payload.name, slug=payload.slug
    )
    product = Product(
        store_id=store_id,
        name=payload.name,
        slug=slug,
        description=payload.description,
        status=ProductStatus.draft,
        price_amount_minor=payload.price_amount_minor,
        price_currency=payload.price_currency or store.currency,
        is_featured=payload.is_featured,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def update_product(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: ProductUpdate,
) -> Product:
    """Apply a partial update to a product.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product id.
        payload: Fields to change.

    Returns:
        The updated product.

    Raises:
        AppError: 404 not found; 409 if the new slug is taken.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("slug") is not None:
        data["slug"] = _resolve_slug(
            session,
            Product,
            store_id,
            name=product.name,
            slug=data["slug"],
            exclude_id=product.id,
        )
    product.sqlmodel_update(data)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def set_product_published(
    *, session: Session, store_id: uuid.UUID, product_id: uuid.UUID, published: bool
) -> Product:
    """Publish or unpublish (back to draft) a product.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product id.
        published: True to publish, False to revert to draft.

    Returns:
        The updated product.

    Raises:
        AppError: 404 if not found.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    product.status = ProductStatus.published if published else ProductStatus.draft
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def archive_product(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    archived_by: uuid.UUID,
) -> Product:
    """Archive a product (status ``archived`` + soft delete).

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product id.
        archived_by: The acting user's id.

    Returns:
        The archived product.

    Raises:
        AppError: 404 if not found.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    product.status = ProductStatus.archived
    product.deleted_at = get_datetime_utc()
    product.deleted_by_user_id = archived_by
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# --- Categories ---


def list_categories(
    *, session: Session, store_id: uuid.UUID, skip: int, limit: int
) -> tuple[Sequence[Category], int]:
    """Return a paginated list of the store's categories.

    Args:
        session: Active database session.
        store_id: The active store id.
        skip: Offset.
        limit: Page size.

    Returns:
        A ``(categories, total)`` tuple.
    """
    return repo.list_scoped(session, Category, store_id, skip=skip, limit=limit)


def create_category(
    *, session: Session, store_id: uuid.UUID, payload: CategoryCreate
) -> Category:
    """Create a category (slug derived, unique per active store).

    Args:
        session: Active database session.
        store_id: The active store id.
        payload: Category creation data.

    Returns:
        The created category.

    Raises:
        AppError: 422 invalid slug; 409 slug already in use.
    """
    slug = _resolve_slug(
        session, Category, store_id, name=payload.name, slug=payload.slug
    )
    category = Category(
        store_id=store_id,
        name=payload.name,
        slug=slug,
        description=payload.description,
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def _get_category(
    *, session: Session, store_id: uuid.UUID, category_id: uuid.UUID
) -> Category:
    """Return a store's category by id, or raise 404."""
    category = get_store_scoped(
        session=session, model=Category, store_id=store_id, resource_id=category_id
    )
    if category is None:
        raise AppError("category_not_found", "Category not found", 404)
    return category


def update_category(
    *,
    session: Session,
    store_id: uuid.UUID,
    category_id: uuid.UUID,
    payload: CategoryUpdate,
) -> Category:
    """Apply a partial update to a category.

    Args:
        session: Active database session.
        store_id: The active store id.
        category_id: The category id.
        payload: Fields to change.

    Returns:
        The updated category.

    Raises:
        AppError: 404 not found; 409 if the new slug is taken.
    """
    category = _get_category(
        session=session, store_id=store_id, category_id=category_id
    )
    data = payload.model_dump(exclude_unset=True)
    if data.get("slug") is not None:
        data["slug"] = _resolve_slug(
            session,
            Category,
            store_id,
            name=category.name,
            slug=data["slug"],
            exclude_id=category.id,
        )
    category.sqlmodel_update(data)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def archive_category(
    *,
    session: Session,
    store_id: uuid.UUID,
    category_id: uuid.UUID,
    archived_by: uuid.UUID,
) -> None:
    """Soft-delete a category.

    Args:
        session: Active database session.
        store_id: The active store id.
        category_id: The category id.
        archived_by: The acting user's id.

    Raises:
        AppError: 404 if not found.
    """
    category = _get_category(
        session=session, store_id=store_id, category_id=category_id
    )
    category.deleted_at = get_datetime_utc()
    category.deleted_by_user_id = archived_by
    session.add(category)
    session.commit()


# --- Variants ---


def list_variants(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    skip: int,
    limit: int,
) -> tuple[Sequence[ProductVariant], int]:
    """Return a product's variants (paginated). Validates the product first.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.
        skip: Offset.
        limit: Page size.

    Returns:
        A ``(variants, total)`` tuple.

    Raises:
        AppError: 404 if the product is not found.
    """
    get_product(session=session, store_id=store_id, product_id=product_id)
    return repo.list_scoped(
        session,
        ProductVariant,
        store_id,
        skip=skip,
        limit=limit,
        extra=(ProductVariant.product_id == product_id,),
    )


def create_variant(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: VariantCreate,
) -> ProductVariant:
    """Create a variant under a product.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.
        payload: Variant creation data.

    Returns:
        The created variant.

    Raises:
        AppError: 404 if the product is not found.
    """
    get_product(session=session, store_id=store_id, product_id=product_id)
    variant = ProductVariant(
        store_id=store_id,
        product_id=product_id,
        name=payload.name,
        sku=payload.sku,
        attributes=payload.attributes,
        price_override_amount_minor=payload.price_override_amount_minor,
        price_override_currency=payload.price_override_currency,
    )
    session.add(variant)
    session.commit()
    session.refresh(variant)
    return variant


def _get_variant(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID,
) -> ProductVariant:
    """Return a variant by ``(store, id)`` validating it belongs to the product."""
    variant = get_store_scoped(
        session=session,
        model=ProductVariant,
        store_id=store_id,
        resource_id=variant_id,
    )
    if variant is None or variant.product_id != product_id:
        raise AppError("variant_not_found", "Variant not found", 404)
    return variant


def update_variant(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID,
    payload: VariantUpdate,
) -> ProductVariant:
    """Apply a partial update to a variant.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.
        variant_id: The variant id.
        payload: Fields to change.

    Returns:
        The updated variant.

    Raises:
        AppError: 404 if not found.
    """
    variant = _get_variant(
        session=session, store_id=store_id, product_id=product_id, variant_id=variant_id
    )
    variant.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(variant)
    session.commit()
    session.refresh(variant)
    return variant


def archive_variant(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID,
    archived_by: uuid.UUID,
) -> None:
    """Archive a variant (status ``archived`` + soft delete).

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.
        variant_id: The variant id.
        archived_by: The acting user's id.

    Raises:
        AppError: 404 if not found.
    """
    variant = _get_variant(
        session=session, store_id=store_id, product_id=product_id, variant_id=variant_id
    )
    variant.status = ProductVariantStatus.archived
    variant.deleted_at = get_datetime_utc()
    variant.deleted_by_user_id = archived_by
    session.add(variant)
    session.commit()


# --- Images ---


def list_images(
    *, session: Session, store_id: uuid.UUID, product_id: uuid.UUID
) -> list[ImagePublic]:
    """Return a product's images (with each media's URL/status), by position.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.

    Returns:
        The images, each carrying its media file's URL, variants and status.

    Raises:
        AppError: 404 if the product is not found.
    """
    get_product(session=session, store_id=store_id, product_id=product_id)
    result: list[ImagePublic] = []
    for image in repo.list_product_images(
        session, store_id=store_id, product_id=product_id
    ):
        media = session.get(MediaFile, image.media_file_id)
        if media is None:  # pragma: no cover - the FK guarantees the media exists
            continue
        result.append(
            ImagePublic(
                id=image.id,
                store_id=image.store_id,
                product_id=image.product_id,
                media_file_id=image.media_file_id,
                position=image.position,
                url=media.url,
                variants=media.variants,
                status=media.status,
            )
        )
    return result


def attach_image(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: ImageAttach,
) -> ImagePublic:
    """Link a store's media file to a product at a position.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.
        payload: The media file id + position.

    Returns:
        The created image link (with the media's URL, variants and status).

    Raises:
        AppError: 404 if the product or the media file is not in the store.
    """
    get_product(session=session, store_id=store_id, product_id=product_id)
    media = get_store_scoped(
        session=session,
        model=MediaFile,
        store_id=store_id,
        resource_id=payload.media_file_id,
    )
    if media is None:
        raise AppError("media_not_found", "Media file not found in this store", 404)
    image = ProductImage(
        store_id=store_id,
        product_id=product_id,
        media_file_id=payload.media_file_id,
        position=payload.position,
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    return ImagePublic(
        id=image.id,
        store_id=image.store_id,
        product_id=image.product_id,
        media_file_id=image.media_file_id,
        position=image.position,
        url=media.url,
        variants=media.variants,
        status=media.status,
    )


def remove_image(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    image_id: uuid.UUID,
    removed_by: uuid.UUID,
) -> None:
    """Soft-delete a product image link.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The owning product id.
        image_id: The image link id.
        removed_by: The acting user's id.

    Raises:
        AppError: 404 if not found.
    """
    image = get_store_scoped(
        session=session, model=ProductImage, store_id=store_id, resource_id=image_id
    )
    if image is None or image.product_id != product_id:
        raise AppError("image_not_found", "Image not found", 404)
    image.deleted_at = get_datetime_utc()
    image.deleted_by_user_id = removed_by
    session.add(image)
    session.commit()


# --- Inventory ---


def set_inventory(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: InventorySet,
) -> InventoryItem:
    """Set the stock quantity for a product (optionally a specific variant).

    Upserts the single inventory row for ``(product, variant)``.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product id.
        payload: The variant (optional) and the new quantity.

    Returns:
        The created/updated inventory row.

    Raises:
        AppError: 404 if the product or the variant is not found.
    """
    get_product(session=session, store_id=store_id, product_id=product_id)
    if payload.variant_id is not None:
        _get_variant(
            session=session,
            store_id=store_id,
            product_id=product_id,
            variant_id=payload.variant_id,
        )
    item = repo.get_inventory_item(
        session, store_id=store_id, product_id=product_id, variant_id=payload.variant_id
    )
    if item is None:
        item = InventoryItem(
            store_id=store_id,
            product_id=product_id,
            variant_id=payload.variant_id,
            quantity=payload.quantity,
        )
    else:
        item.quantity = payload.quantity
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
