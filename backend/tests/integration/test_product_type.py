"""Integration tests for the product type + add-to-cart gate (P6-CAT-01)."""

import pytest
from sqlmodel import Session

from app.core.api import AppError
from app.modules.catalog.enums import ProductType
from app.modules.catalog.models import Product
from app.modules.catalog.schemas import ProductPublic
from app.modules.catalog.services import assert_addable_to_cart
from app.modules.stores.models import Store


def _product(db: Session, *, ptype: ProductType = ProductType.image) -> Product:
    """Create a store + product of the given type (defaults to ``image``)."""
    store = Store(name="Loja", slug=f"pt-{ptype.value}", currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    product = Product(
        store_id=store.id,
        name="P",
        slug="p",
        type=ptype,
        price_amount_minor=1000,
        price_currency="USD",
    )
    db.add(product)
    db.flush()
    db.refresh(product)
    return product


def test_product_defaults_to_image(db: Session) -> None:
    """A product created without a type defaults to ``image``."""
    store = Store(name="Loja", slug="pt-default", currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    product = Product(
        store_id=store.id,
        name="P",
        slug="p",
        price_amount_minor=1000,
        price_currency="USD",
    )
    db.add(product)
    db.flush()
    db.refresh(product)
    assert product.type == ProductType.image


def test_type_in_public_schema(db: Session) -> None:
    """``type`` is exposed on the public product schema (inherited by storefront)."""
    public = ProductPublic.model_validate(_product(db, ptype=ProductType.image_3d))
    assert public.type == ProductType.image_3d


def test_gate_allows_image_and_image_3d(db: Session) -> None:
    """``image``/``image_3d`` pass the add-to-cart gate (no exception)."""
    assert_addable_to_cart(_product(db, ptype=ProductType.image))
    assert_addable_to_cart(_product(db, ptype=ProductType.image_3d))


def test_gate_blocks_customizable_without_session(db: Session) -> None:
    """``image_3d_customizable`` is refused without an approved session."""
    product = _product(db, ptype=ProductType.image_3d_customizable)
    with pytest.raises(AppError) as exc:
        assert_addable_to_cart(product)
    assert exc.value.code == "customization_required"
    assert exc.value.status_code == 422
    # The Fase 7 seam: an approved session lets it through (no exception).
    assert_addable_to_cart(product, has_approved_customization=True)
