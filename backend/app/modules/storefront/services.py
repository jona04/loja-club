"""Storefront services: public read endpoints, host-resolved, cached (doc 10/13).

Public (no-auth) reads for the customer vitrine. Queries are kept **separate**
from the admin/catalog ones and filter to *published* products / non-deleted
rows of the active store. Hot reads are cache-aside (doc 13) under
``store:{id}:home|categories|product:{slug}``; the panel (``P3-CONTENT-02``)
invalidates the layout caches.
"""

import uuid
from typing import Any

from pydantic import TypeAdapter
from sqlmodel import Session, col, func, select
from sqlmodel.sql.expression import SelectOfScalar

from app.core.api import AppError, PageParams
from app.core.cache import cache_get, cache_set
from app.modules.catalog import services as catalog_services
from app.modules.catalog.enums import ProductStatus
from app.modules.catalog.models import Category, Product, ProductCategory
from app.modules.catalog.schemas import CategoryPublic
from app.modules.content.models import ContentPage
from app.modules.content.repositories import get_store_theme_settings
from app.modules.content.services import resolve_active_settings
from app.modules.storefront.schemas import (
    StorefrontCategorySection,
    StorefrontHome,
    StorefrontProduct,
    StorefrontStore,
    StorefrontTheme,
)
from app.modules.stores.models import Store, StoreSettings

# Storefront read caches live ~5 min (doc 13); panel writes invalidate eagerly.
_TTL = 300
DEFAULT_TEMPLATE_ID = "aurora"
_FEATURED_LIMIT = 12
_HOME_CATEGORIES = 6
_SECTION_PRODUCTS = 8
_CATEGORIES_ADAPTER = TypeAdapter(list[CategoryPublic])


def _published_products(store_id: uuid.UUID) -> SelectOfScalar[Product]:
    """Build the base query for a store's published, non-deleted products."""
    return select(Product).where(
        Product.store_id == store_id,
        Product.status == ProductStatus.published,
        col(Product.deleted_at).is_(None),
    )


def _to_storefront_product(*, session: Session, product: Product) -> StorefrontProduct:
    """Enrich a product with its images for the storefront."""
    sp = StorefrontProduct.model_validate(product)
    sp.images = catalog_services.list_images(
        session=session, store_id=product.store_id, product_id=product.id
    )
    return sp


def _store_public(store: Store, settings: StoreSettings | None) -> StorefrontStore:
    """Build the public store identity from the store and its settings."""
    return StorefrontStore(
        name=store.name,
        slug=store.slug,
        currency=store.currency,
        locale=store.locale,
        public_name=settings.public_name if settings else None,
        description=settings.description if settings else None,
        logo_url=settings.logo_url if settings else None,
        whatsapp_number=settings.whatsapp_number if settings else None,
    )


def _theme(*, session: Session, store_id: uuid.UUID) -> StorefrontTheme:
    """Return the store's public theme (active template + appearance + chrome settings).

    Falls back to ``DEFAULT_TEMPLATE_ID`` if the store has no settings yet (no row
    created). ``settings`` are the active template's schema defaults merged with
    the store's overrides.
    """
    row = get_store_theme_settings(session=session, store_id=store_id)
    template_id = row.active_template_id if row is not None else DEFAULT_TEMPLATE_ID
    settings = resolve_active_settings(
        session=session, store_id=store_id, active_template_id=template_id
    )
    if row is None:
        return StorefrontTheme(active_template_id=template_id, settings=settings)
    theme = StorefrontTheme.model_validate(row)
    theme.settings = settings
    return theme


def _category_sections(
    *, session: Session, store_id: uuid.UUID
) -> list[StorefrontCategorySection]:
    """Build the home's category sections (for templates like Bazar).

    The first categories (by name), each with its first published products;
    empty categories are skipped.

    Args:
        session: Active database session.
        store_id: The active store id.

    Returns:
        Up to ``_HOME_CATEGORIES`` non-empty sections.
    """
    categories = session.exec(
        select(Category)
        .where(Category.store_id == store_id, col(Category.deleted_at).is_(None))
        .order_by(col(Category.name))
        .limit(_HOME_CATEGORIES)
    ).all()
    sections: list[StorefrontCategorySection] = []
    for cat in categories:
        in_cat = select(ProductCategory.product_id).where(
            ProductCategory.category_id == cat.id,
            ProductCategory.store_id == store_id,
        )
        products = session.exec(
            _published_products(store_id)
            .where(col(Product.id).in_(in_cat))
            .order_by(col(Product.created_at).desc())
            .limit(_SECTION_PRODUCTS)
        ).all()
        if products:
            sections.append(
                StorefrontCategorySection(
                    category=CategoryPublic.model_validate(cat),
                    products=[
                        _to_storefront_product(session=session, product=p)
                        for p in products
                    ],
                )
            )
    return sections


def get_home(*, session: Session, store: Store) -> StorefrontHome:
    """Return the storefront home (store + theme + highlights), cache-aside.

    Args:
        session: Active database session.
        store: The resolved, published store.

    Returns:
        The home payload.
    """
    cached = cache_get(f"{store.id}:home", prefix="store")
    if cached is not None:
        return StorefrontHome.model_validate_json(cached)
    settings = session.exec(
        select(StoreSettings).where(StoreSettings.store_id == store.id)
    ).first()
    featured = session.exec(
        _published_products(store.id)
        .where(col(Product.is_featured).is_(True))
        .order_by(col(Product.created_at).desc())
        .limit(_FEATURED_LIMIT)
    ).all()
    home = StorefrontHome(
        store=_store_public(store, settings),
        theme=_theme(session=session, store_id=store.id),
        featured_products=[
            _to_storefront_product(session=session, product=p) for p in featured
        ],
        category_sections=_category_sections(session=session, store_id=store.id),
    )
    cache_set(f"{store.id}:home", home.model_dump_json(), ttl=_TTL, prefix="store")
    return home


def get_categories(*, session: Session, store: Store) -> list[CategoryPublic]:
    """Return the store's categories, cache-aside.

    Args:
        session: Active database session.
        store: The resolved, published store.

    Returns:
        The store's categories.
    """
    cached = cache_get(f"{store.id}:categories", prefix="store")
    if cached is not None:
        return _CATEGORIES_ADAPTER.validate_json(cached)
    rows = session.exec(
        select(Category)
        .where(Category.store_id == store.id, col(Category.deleted_at).is_(None))
        .order_by(col(Category.name))
    ).all()
    categories = [CategoryPublic.model_validate(c) for c in rows]
    cache_set(
        f"{store.id}:categories",
        _CATEGORIES_ADAPTER.dump_json(categories).decode(),
        ttl=_TTL,
        prefix="store",
    )
    return categories


def list_products(
    *,
    session: Session,
    store: Store,
    params: PageParams,
    category: str | None = None,
) -> tuple[list[StorefrontProduct], int]:
    """List the store's published products (paginated; not cached).

    Args:
        session: Active database session.
        store: The resolved, published store.
        params: Offset pagination parameters.
        category: Optional category slug to filter by.

    Returns:
        A ``(products, total_count)`` tuple.
    """
    filters: list[Any] = [
        Product.store_id == store.id,
        Product.status == ProductStatus.published,
        col(Product.deleted_at).is_(None),
    ]
    if category is not None:
        in_category = (
            select(ProductCategory.product_id)
            .join(Category, col(Category.id) == col(ProductCategory.category_id))
            .where(
                Category.store_id == store.id,
                Category.slug == category,
                col(Category.deleted_at).is_(None),
            )
        )
        filters.append(col(Product.id).in_(in_category))
    count = session.exec(
        select(func.count()).select_from(Product).where(*filters)
    ).one()
    rows = session.exec(
        select(Product)
        .where(*filters)
        .order_by(col(Product.created_at).desc())
        .offset(params.skip)
        .limit(params.limit)
    ).all()
    return [_to_storefront_product(session=session, product=p) for p in rows], count


def get_product(*, session: Session, store: Store, slug: str) -> StorefrontProduct:
    """Return a published product by ``slug``, cache-aside.

    Args:
        session: Active database session.
        store: The resolved, published store.
        slug: The product slug.

    Returns:
        The product with its images.

    Raises:
        AppError: 404 if no published product has that slug.
    """
    cached = cache_get(f"{store.id}:product:{slug}", prefix="store")
    if cached is not None:
        return StorefrontProduct.model_validate_json(cached)
    product = session.exec(
        _published_products(store.id).where(Product.slug == slug)
    ).first()
    if product is None:
        raise AppError("product_not_found", "Product not found", status_code=404)
    sp = _to_storefront_product(session=session, product=product)
    cache_set(
        f"{store.id}:product:{slug}", sp.model_dump_json(), ttl=_TTL, prefix="store"
    )
    return sp


def get_page(*, session: Session, store: Store, slug: str) -> ContentPage:
    """Return a published editorial page by ``slug``.

    Args:
        session: Active database session.
        store: The resolved, published store.
        slug: The page slug.

    Returns:
        The published page.

    Raises:
        AppError: 404 if no published page has that slug.
    """
    page = session.exec(
        select(ContentPage).where(
            ContentPage.store_id == store.id,
            ContentPage.slug == slug,
            col(ContentPage.is_published).is_(True),
            col(ContentPage.deleted_at).is_(None),
        )
    ).first()
    if page is None:
        raise AppError("page_not_found", "Page not found", status_code=404)
    return page
