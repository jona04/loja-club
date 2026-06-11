"""Seed a template's demo store from its ``demo.json``.

Each template gets a real, published store (``<id>-demo``) with the template
active and the demo's categories/products/images (already on the CDN via
``import_assets``). It is served like any storefront — the navigable preview and
the model a merchant copies. Idempotent: re-running updates in place and never
duplicates (every record is matched by its natural key before insert).
"""

from typing import Any
from urllib.parse import urlparse

from sqlmodel import Session, col, select

from app.modules.catalog.enums import ProductStatus
from app.modules.catalog.models import (
    Category,
    Product,
    ProductCategory,
    ProductImage,
)
from app.modules.content import import_assets
from app.modules.content.models import (
    ContentStoreThemeSettings,
    ContentThemeTemplate,
)
from app.modules.domains.enums import DomainStatus
from app.modules.domains.models import DomainHost
from app.modules.media.enums import MediaStatus
from app.modules.media.models import MediaFile
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store

_DEMO_COUNTRY = "BR"
_DEMO_CURRENCY = "BRL"
_DEMO_LOCALE = "pt-BR"


def _get_or_create_store(session: Session, template_id: str, slug: str) -> Store:
    """Return the demo store for ``slug``, creating an active one if absent."""
    store = session.exec(
        select(Store).where(Store.slug == slug, col(Store.deleted_at).is_(None))
    ).first()
    if store is None:
        store = Store(
            name=f"{template_id.title()} Demo",
            slug=slug,
            country=_DEMO_COUNTRY,
            currency=_DEMO_CURRENCY,
            locale=_DEMO_LOCALE,
            status=StoreStatus.active,
        )
        session.add(store)
        session.flush()
    return store


def _ensure_host(session: Session, store: Store, slug: str) -> None:
    """Ensure the demo store resolves at ``{slug}.localhost``."""
    host = f"{slug}.localhost"
    if session.exec(select(DomainHost).where(DomainHost.host == host)).first() is None:
        session.add(
            DomainHost(host=host, store_id=store.id, status=DomainStatus.active)
        )


def _ensure_theme(
    session: Session, store: Store, template_id: str, banner: str | None
) -> None:
    """Ensure the demo store has the template active and the hero banner set.

    Args:
        session: Active database session.
        store: The demo store.
        template_id: The template to activate.
        banner: The demo's hero image URL (CDN), or ``None`` to leave it unset.
    """
    theme = session.exec(
        select(ContentStoreThemeSettings).where(
            ContentStoreThemeSettings.store_id == store.id
        )
    ).first()
    if theme is None:
        session.add(
            ContentStoreThemeSettings(
                store_id=store.id,
                active_template_id=template_id,
                banner_image_url=banner,
            )
        )
        return
    changed = False
    if theme.active_template_id != template_id:
        theme.active_template_id = template_id
        changed = True
    if banner and theme.banner_image_url != banner:
        theme.banner_image_url = banner
        changed = True
    if changed:
        session.add(theme)


def _seed_categories(
    session: Session, store: Store, entries: list[dict[str, Any]]
) -> dict[str, Category]:
    """Create the demo categories (by slug) and return them keyed by slug."""
    by_slug: dict[str, Category] = {}
    for entry in entries:
        slug = str(entry["slug"])
        category = session.exec(
            select(Category).where(
                Category.store_id == store.id,
                Category.slug == slug,
                col(Category.deleted_at).is_(None),
            )
        ).first()
        if category is None:
            category = Category(store_id=store.id, name=str(entry["name"]), slug=slug)
            session.add(category)
            session.flush()
        by_slug[slug] = category
    return by_slug


def _ensure_image(session: Session, store: Store, product: Product, url: str) -> None:
    """Attach the CDN image ``url`` to ``product`` (via a media file)."""
    key = urlparse(url).path.lstrip("/")
    media = session.exec(select(MediaFile).where(MediaFile.key == key)).first()
    if media is None:
        media = MediaFile(
            store_id=store.id,
            owner_type="product",
            owner_id=product.id,
            key=key,
            url=url,
            content_type="image/png",
            size=0,
            status=MediaStatus.ready,
        )
        session.add(media)
        session.flush()
    link = session.exec(
        select(ProductImage).where(
            ProductImage.product_id == product.id,
            ProductImage.media_file_id == media.id,
        )
    ).first()
    if link is None:
        session.add(
            ProductImage(
                store_id=store.id,
                product_id=product.id,
                media_file_id=media.id,
                position=0,
            )
        )


def _seed_products(
    session: Session,
    store: Store,
    entries: list[dict[str, Any]],
    categories: dict[str, Category],
) -> None:
    """Create the demo products (published) with category + image (by slug)."""
    for index, entry in enumerate(entries):
        slug = str(entry["slug"])
        product = session.exec(
            select(Product).where(
                Product.store_id == store.id,
                Product.slug == slug,
                col(Product.deleted_at).is_(None),
            )
        ).first()
        if product is None:
            product = Product(
                store_id=store.id,
                name=str(entry["name"]),
                slug=slug,
                price_amount_minor=int(entry["price"]),
                price_currency=_DEMO_CURRENCY,
                status=ProductStatus.published,
                is_featured=index < 4,
            )
            session.add(product)
            session.flush()
        category = categories.get(str(entry["category"]))
        if category is not None:
            exists = session.exec(
                select(ProductCategory).where(
                    ProductCategory.product_id == product.id,
                    ProductCategory.category_id == category.id,
                )
            ).first()
            if exists is None:
                session.add(
                    ProductCategory(
                        store_id=store.id,
                        product_id=product.id,
                        category_id=category.id,
                    )
                )
        image = entry.get("image")
        if isinstance(image, str) and image:
            _ensure_image(session, store, product, image)


def seed_template_demo_store(*, session: Session, template_id: str) -> Store | None:
    """Create/update a template's demo store from its ``demo.json`` (idempotent).

    Args:
        session: Active database session.
        template_id: The template whose demo store is seeded.

    Returns:
        The demo store, or ``None`` when the template has no ``demo.json``.
    """
    demo = import_assets.load_demo(template_id)
    if demo is None:
        return None
    slug = f"{template_id}-demo"
    store = _get_or_create_store(session, template_id, slug)
    _ensure_host(session, store, slug)
    banner = demo.get("banner")
    _ensure_theme(
        session, store, template_id, banner if isinstance(banner, str) else None
    )
    categories = _seed_categories(session, store, demo.get("categories", []))
    _seed_products(session, store, demo.get("products", []), categories)
    session.commit()
    return store


def seed_demo_stores(*, session: Session) -> None:
    """Seed the demo store of every active template that ships a demo (idempotent).

    Args:
        session: Active database session.
    """
    template_ids = session.exec(
        select(ContentThemeTemplate.id).where(
            col(ContentThemeTemplate.is_active).is_(True)
        )
    ).all()
    for template_id in template_ids:
        seed_template_demo_store(session=session, template_id=template_id)
