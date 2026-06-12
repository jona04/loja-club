"""Integration tests for order creation/cancellation (P6-ORD-01)."""

import uuid

import pytest
from sqlmodel import Session, select

from app.core.api import AppError
from app.modules.cart.enums import CartStatus
from app.modules.cart.models import CartCart, CartItem
from app.modules.catalog.enums import ProductStatus, ProductType
from app.modules.catalog.models import InventoryItem, Product
from app.modules.customers.models import CustomerProfile
from app.modules.customers.schemas import AddressInput
from app.modules.customers.services import create_or_update_customer
from app.modules.orders.enums import OrderStatus
from app.modules.orders.models import (
    Order,
    OrderAddress,
    OrderItem,
    OrderStatusHistory,
)
from app.modules.orders.services import cancel_order, create_order
from app.modules.shipping.enums import ShippingMethodType
from app.modules.shipping.models import ShippingMethod
from app.modules.stores.models import Store


def _store(db: Session, slug: str) -> Store:
    store = Store(name="L", slug=slug, currency="BRL", locale="pt-BR")
    db.add(store)
    db.flush()
    return store


def _product(
    db: Session,
    store: Store,
    *,
    slug: str = "p",
    price: int = 1500,
    stock: int | None = None,
) -> Product:
    product = Product(
        store_id=store.id,
        name=slug.title(),
        slug=slug,
        type=ProductType.image,
        status=ProductStatus.published,
        price_amount_minor=price,
        price_currency="BRL",
    )
    db.add(product)
    db.flush()
    if stock is not None:
        db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=stock))
        db.flush()
    return product


def _cart(
    db: Session, store: Store, product: Product, qty: int, price: int = 1500
) -> CartCart:
    cart = CartCart(
        store_id=store.id,
        guest_session_id=f"g-{uuid.uuid4().hex[:8]}",
        status=CartStatus.active,
    )
    db.add(cart)
    db.flush()
    db.add(
        CartItem(
            store_id=store.id,
            cart_id=cart.id,
            product_id=product.id,
            quantity=qty,
            unit_price_amount_minor=price,
            unit_price_currency="BRL",
        )
    )
    db.flush()
    return cart


def _shipping(
    db: Session, store: Store, mtype: ShippingMethodType, price: int | None = None
) -> ShippingMethod:
    method = ShippingMethod(
        store_id=store.id, type=mtype, name=mtype.value, price_amount_minor=price
    )
    db.add(method)
    db.flush()
    return method


def _customer(db: Session, store: Store) -> CustomerProfile:
    return create_or_update_customer(
        session=db, store_id=store.id, name="Ana", email="ana@x.com"
    )


def _address() -> AddressInput:
    return AddressInput(line1="Rua A", city="SP", country="BR")


def test_create_order_freezes_and_decrements(db: Session) -> None:
    store = _store(db, "ord-create")
    product = _product(db, store, price=1500, stock=10)
    cart = _cart(db, store, product, qty=2)
    method = _shipping(db, store, ShippingMethodType.fixed_shipping, price=900)

    order = create_order(
        session=db,
        cart=cart,
        customer=_customer(db, store),
        address=_address(),
        shipping_method=method,
    )

    assert order.status == OrderStatus.pending_payment
    assert order.order_number == 1
    assert order.subtotal_amount_minor == 3000
    assert order.shipping_amount_minor == 900
    assert order.total_amount_minor == 3900
    assert order.shipping_method_type == ShippingMethodType.fixed_shipping

    items = db.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all()
    assert len(items) == 1
    assert items[0].name == "P"
    assert items[0].quantity == 2
    assert items[0].unit_price_amount_minor == 1500
    assert items[0].line_total_amount_minor == 3000

    inv = db.exec(
        select(InventoryItem).where(InventoryItem.product_id == product.id)
    ).one()
    assert inv.quantity == 8  # 10 - 2

    db.refresh(cart)
    assert cart.status == CartStatus.converted
    assert (
        db.exec(select(OrderAddress).where(OrderAddress.order_id == order.id)).first()
        is not None
    )
    history = db.exec(
        select(OrderStatusHistory).where(OrderStatusHistory.order_id == order.id)
    ).all()
    assert [h.status for h in history] == [OrderStatus.pending_payment]


def test_price_frozen_after_product_change(db: Session) -> None:
    store = _store(db, "ord-freeze")
    product = _product(db, store, price=1500, stock=10)
    order = create_order(
        session=db,
        cart=_cart(db, store, product, qty=1),
        customer=_customer(db, store),
        address=_address(),
        shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
    )
    product.price_amount_minor = 9999
    db.add(product)
    db.commit()
    item = db.exec(select(OrderItem).where(OrderItem.order_id == order.id)).one()
    assert item.unit_price_amount_minor == 1500  # unchanged


def test_pickup_has_no_shipping_cost(db: Session) -> None:
    store = _store(db, "ord-pickup")
    product = _product(db, store, price=1000, stock=5)
    order = create_order(
        session=db,
        cart=_cart(db, store, product, qty=1, price=1000),
        customer=_customer(db, store),
        address=_address(),
        shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
    )
    assert order.shipping_amount_minor == 0
    assert order.total_amount_minor == 1000


def test_insufficient_stock_at_order(db: Session) -> None:
    store = _store(db, "ord-stock")
    product = _product(db, store, stock=3)
    cart = _cart(db, store, product, qty=5)  # more than stock
    with pytest.raises(AppError) as exc:
        create_order(
            session=db,
            cart=cart,
            customer=_customer(db, store),
            address=_address(),
            shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
        )
    assert exc.value.code == "insufficient_stock"


def test_empty_cart_is_422(db: Session) -> None:
    store = _store(db, "ord-empty")
    cart = CartCart(store_id=store.id, guest_session_id="g", status=CartStatus.active)
    db.add(cart)
    db.flush()
    with pytest.raises(AppError) as exc:
        create_order(
            session=db,
            cart=cart,
            customer=_customer(db, store),
            address=_address(),
            shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
        )
    assert exc.value.code == "empty_cart"


def test_cancel_restocks(db: Session) -> None:
    store = _store(db, "ord-cancel")
    product = _product(db, store, stock=10)
    order = create_order(
        session=db,
        cart=_cart(db, store, product, qty=4),
        customer=_customer(db, store),
        address=_address(),
        shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
    )
    inv = db.exec(
        select(InventoryItem).where(InventoryItem.product_id == product.id)
    ).one()
    assert inv.quantity == 6  # decremented

    canceled = cancel_order(session=db, order=order)
    assert canceled.status == OrderStatus.canceled
    db.refresh(inv)
    assert inv.quantity == 10  # restocked


def test_cannot_cancel_shipped(db: Session) -> None:
    store = _store(db, "ord-shipped")
    product = _product(db, store, stock=5)
    order = create_order(
        session=db,
        cart=_cart(db, store, product, qty=1),
        customer=_customer(db, store),
        address=_address(),
        shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
    )
    order.status = OrderStatus.shipped
    db.add(order)
    db.commit()
    with pytest.raises(AppError) as exc:
        cancel_order(session=db, order=order)
    assert exc.value.code == "cannot_cancel"


def test_untracked_product_order_and_cancel(db: Session) -> None:
    store = _store(db, "ord-untracked")
    product = _product(db, store, stock=None)  # no inventory row → no limit
    order = create_order(
        session=db,
        cart=_cart(db, store, product, qty=3),
        customer=_customer(db, store),
        address=_address(),
        shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
    )
    assert order.status == OrderStatus.pending_payment
    canceled = cancel_order(session=db, order=order)  # nothing to restock
    assert canceled.status == OrderStatus.canceled


def test_order_number_sequential_and_isolated(db: Session) -> None:
    a = _store(db, "ord-num-a")
    b = _store(db, "ord-num-b")
    pa = _product(db, a, slug="pa", stock=10)
    pb = _product(db, b, slug="pb", stock=10)

    def _order(store: Store, product: Product) -> Order:
        return create_order(
            session=db,
            cart=_cart(db, store, product, qty=1),
            customer=_customer(db, store),
            address=_address(),
            shipping_method=_shipping(db, store, ShippingMethodType.local_pickup),
        )

    assert _order(a, pa).order_number == 1
    assert _order(a, pa).order_number == 2  # store A increments
    assert _order(b, pb).order_number == 1  # store B independent
