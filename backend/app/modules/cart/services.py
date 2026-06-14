"""Cart services: the server-side cart, keyed by the guest session (doc 10/11).

Public (no panel auth): the store comes from the request host and the cart from
the ``guest_session_id`` cookie. Adding an item passes the **add-to-cart gate**
(``P6-CAT-01``) and validates stock against ``catalog_inventory_items``. Prices
are snapshotted per line when added; the **order** re-freezes them (``P6-ORD-01``).
"""

import uuid

from sqlmodel import Session, col, select

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.cart.enums import CartStatus
from app.modules.cart.models import CartCart, CartItem
from app.modules.cart.schemas import AddItemInput, CartItemPublic, CartPublic
from app.modules.catalog.enums import ProductStatus, ProductType, ProductVariantStatus
from app.modules.catalog.models import InventoryItem, Product, ProductVariant
from app.modules.catalog.services import assert_addable_to_cart, list_images
from app.modules.customization import orders as customization_orders
from app.modules.discounts import services as discount_services
from app.modules.stores.models import Store


def get_or_create_cart(
    *, session: Session, store_id: uuid.UUID, guest_session_id: str
) -> CartCart:
    """Return the guest's active cart for the store, creating one if absent.

    Args:
        session: Active database session.
        store_id: The store the cart belongs to.
        guest_session_id: The browser's guest-session token.

    Returns:
        The active :class:`CartCart`.
    """
    cart = session.exec(
        select(CartCart).where(
            CartCart.store_id == store_id,
            CartCart.guest_session_id == guest_session_id,
            CartCart.status == CartStatus.active,
            col(CartCart.deleted_at).is_(None),
        )
    ).first()
    if cart is None:
        cart = CartCart(store_id=store_id, guest_session_id=guest_session_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


def _get_published_product(
    session: Session, store_id: uuid.UUID, product_id: uuid.UUID
) -> Product:
    """Return a published product of the store, or raise 404."""
    product = session.exec(
        select(Product).where(
            Product.id == product_id,
            Product.store_id == store_id,
            Product.status == ProductStatus.published,
            col(Product.deleted_at).is_(None),
        )
    ).first()
    if product is None:
        raise AppError("product_not_found", "Product not found", status_code=404)
    return product


def _get_variant(
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID,
) -> ProductVariant:
    """Return an active variant of the product, or raise 404."""
    variant = session.exec(
        select(ProductVariant).where(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
            ProductVariant.store_id == store_id,
            ProductVariant.status == ProductVariantStatus.active,
            col(ProductVariant.deleted_at).is_(None),
        )
    ).first()
    if variant is None:
        raise AppError("variant_not_found", "Variant not found", status_code=404)
    return variant


def _resolve_price(product: Product, variant: ProductVariant | None) -> tuple[int, str]:
    """Return the unit price (minor units + currency) for a product/variant."""
    if variant is not None and variant.price_override_amount_minor is not None:
        return variant.price_override_amount_minor, (
            variant.price_override_currency or product.price_currency
        )
    return product.price_amount_minor, product.price_currency


def _available_stock(
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
) -> int | None:
    """Return the tracked stock, or ``None`` when inventory is not tracked."""
    variant_cond = (
        InventoryItem.variant_id == variant_id
        if variant_id is not None
        else col(InventoryItem.variant_id).is_(None)
    )
    item = session.exec(
        select(InventoryItem).where(
            InventoryItem.store_id == store_id,
            InventoryItem.product_id == product_id,
            variant_cond,
            col(InventoryItem.deleted_at).is_(None),
        )
    ).first()
    return item.quantity if item else None


def _check_stock(
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
    requested_total: int,
) -> None:
    """Refuse when the requested total exceeds the tracked stock.

    Untracked products (no inventory row) are not limited.

    Raises:
        AppError: 409 when the requested quantity exceeds the stock.
    """
    available = _available_stock(session, store_id, product_id, variant_id)
    if available is not None and requested_total > available:
        raise AppError(
            "insufficient_stock",
            f"Only {available} left in stock",
            status_code=409,
        )


def _active_items(session: Session, cart: CartCart) -> list[CartItem]:
    """Return the cart's active items, oldest first."""
    return list(
        session.exec(
            select(CartItem)
            .where(
                CartItem.cart_id == cart.id,
                CartItem.store_id == cart.store_id,
                col(CartItem.deleted_at).is_(None),
            )
            .order_by(col(CartItem.created_at))
        ).all()
    )


def _find_line(
    session: Session,
    cart: CartCart,
    product_id: uuid.UUID,
    variant_id: uuid.UUID | None,
) -> CartItem | None:
    """Return the existing line for a product/variant in the cart, or ``None``."""
    variant_cond = (
        CartItem.variant_id == variant_id
        if variant_id is not None
        else col(CartItem.variant_id).is_(None)
    )
    return session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            variant_cond,
            col(CartItem.deleted_at).is_(None),
        )
    ).first()


def _get_line(session: Session, cart: CartCart, item_id: uuid.UUID) -> CartItem:
    """Return an active line of the cart by id, or raise 404."""
    item = session.exec(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
            CartItem.store_id == cart.store_id,
            col(CartItem.deleted_at).is_(None),
        )
    ).first()
    if item is None:
        raise AppError("cart_item_not_found", "Cart item not found", status_code=404)
    return item


def add_item(*, session: Session, cart: CartCart, data: AddItemInput) -> None:
    """Add a product/variant to the cart (merging an existing line).

    Passes the add-to-cart gate and validates stock against the resulting total.

    Raises:
        AppError: 404 if the product/variant is missing; 422 if the product
            needs customization (gate); 409 if stock is insufficient.
    """
    product = _get_published_product(session, cart.store_id, data.product_id)
    # Customizable products require an approved session; each design is its own
    # line (never merged with another), linked for freezing at order time.
    cust_session = None
    if product.type == ProductType.image_3d_customizable:
        cust_session = customization_orders.resolve_approved_session(
            session=session,
            store_id=cart.store_id,
            product_id=data.product_id,
            guest_session_id=cart.guest_session_id or "",
            session_id=data.customization_session_id,
        )
    assert_addable_to_cart(product, has_approved_customization=cust_session is not None)
    variant = (
        _get_variant(session, cart.store_id, data.product_id, data.variant_id)
        if data.variant_id is not None
        else None
    )
    existing = (
        None
        if cust_session is not None
        else _find_line(session, cart, data.product_id, data.variant_id)
    )
    new_total = (existing.quantity if existing else 0) + data.quantity
    _check_stock(session, cart.store_id, data.product_id, data.variant_id, new_total)
    if existing is not None:
        existing.quantity = new_total
        session.add(existing)
    else:
        price, currency = _resolve_price(product, variant)
        item = CartItem(
            store_id=cart.store_id,
            cart_id=cart.id,
            product_id=data.product_id,
            variant_id=data.variant_id,
            quantity=data.quantity,
            unit_price_amount_minor=price,
            unit_price_currency=currency,
        )
        session.add(item)
        if cust_session is not None:
            session.flush()
            customization_orders.link_session_to_cart_item(
                session=session, cart_item_id=item.id, cust_session=cust_session
            )
    session.commit()


def update_item(
    *, session: Session, cart: CartCart, item_id: uuid.UUID, quantity: int
) -> None:
    """Set a cart line's quantity (validating stock).

    Raises:
        AppError: 404 if the line is missing; 409 if stock is insufficient.
    """
    item = _get_line(session, cart, item_id)
    _check_stock(session, cart.store_id, item.product_id, item.variant_id, quantity)
    item.quantity = quantity
    session.add(item)
    session.commit()


def remove_item(*, session: Session, cart: CartCart, item_id: uuid.UUID) -> None:
    """Soft-delete a cart line.

    Raises:
        AppError: 404 if the line is missing.
    """
    item = _get_line(session, cart, item_id)
    item.deleted_at = get_datetime_utc()
    session.add(item)
    session.commit()


def apply_coupon(*, session: Session, cart: CartCart, code: str) -> None:
    """Validate a coupon against the cart subtotal and apply it.

    Raises:
        AppError: 422 if the coupon is invalid/expired/below the minimum/over its
            usage limit (see ``discounts.services.validate_coupon``).
    """
    items = _active_items(session, cart)
    subtotal = sum(i.unit_price_amount_minor * i.quantity for i in items)
    coupon = discount_services.validate_coupon(
        session=session,
        store_id=cart.store_id,
        code=code,
        subtotal_amount_minor=subtotal,
    )
    cart.coupon_code = coupon.code
    session.add(cart)
    session.commit()


def remove_coupon(*, session: Session, cart: CartCart) -> None:
    """Remove any coupon applied to the cart."""
    cart.coupon_code = None
    session.add(cart)
    session.commit()


def _item_public(
    session: Session, store_id: uuid.UUID, item: CartItem
) -> CartItemPublic:
    """Build a render-ready public line (name/slug; customized art or 1st image)."""
    product = session.get(Product, item.product_id)
    images = list_images(session=session, store_id=store_id, product_id=item.product_id)
    # A customized line shows its own snapshot so two designs are distinguishable.
    custom_image = customization_orders.cart_item_image_url(
        session=session, store_id=store_id, cart_item_id=item.id
    )
    return CartItemPublic(
        id=item.id,
        product_id=item.product_id,
        variant_id=item.variant_id,
        name=product.name if product else "",
        slug=product.slug if product else "",
        image_url=custom_image or (images[0].url if images else None),
        quantity=item.quantity,
        unit_price_amount_minor=item.unit_price_amount_minor,
        unit_price_currency=item.unit_price_currency,
        line_total_amount_minor=item.unit_price_amount_minor * item.quantity,
    )


def to_public(*, session: Session, cart: CartCart) -> CartPublic:
    """Build the cart's public payload (items + subtotal).

    Args:
        session: Active database session.
        cart: The cart to represent.

    Returns:
        The :class:`CartPublic` with render-ready items and the subtotal.
    """
    items = _active_items(session, cart)
    item_publics = [_item_public(session, cart.store_id, item) for item in items]
    subtotal = sum(line.line_total_amount_minor for line in item_publics)
    if items:
        currency = items[0].unit_price_currency
    else:
        store = session.get(Store, cart.store_id)
        currency = store.currency if store else ""
    coupon, discount = discount_services.quote_discount(
        session=session,
        store_id=cart.store_id,
        code=cart.coupon_code,
        subtotal_amount_minor=subtotal,
    )
    return CartPublic(
        id=cart.id,
        currency=currency,
        item_count=sum(item.quantity for item in items),
        subtotal_amount_minor=subtotal,
        coupon_code=coupon.code if coupon is not None else None,
        discount_amount_minor=discount,
        total_amount_minor=subtotal - discount,
        items=item_publics,
    )
