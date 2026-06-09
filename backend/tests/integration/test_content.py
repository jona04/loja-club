"""Integration tests for the content module: models, seed, store isolation."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.modules.content.enums import MenuLocation
from app.modules.content.models import (
    ContentBanner,
    ContentMenu,
    ContentMenuItem,
    ContentPage,
    ContentStoreThemeSettings,
    ContentThemeTemplate,
)
from app.modules.content.repositories import (
    CANONICAL_TEMPLATES,
    seed_content_templates,
)
from app.modules.content.schemas import ThemeTemplatePublic
from app.modules.stores.models import Store


def _store(db: Session, slug: str) -> Store:
    store = Store(name="Loja", slug=slug, currency="USD", locale="en-US")
    db.add(store)
    db.flush()
    return store


def test_seed_creates_classic_and_modern(db: Session) -> None:
    ids = {t.id for t in db.exec(select(ContentThemeTemplate)).all()}
    assert {"classic", "modern"} <= ids


def test_seed_is_idempotent(db: Session) -> None:
    seed_content_templates(session=db)
    seed_content_templates(session=db)
    count = len(db.exec(select(ContentThemeTemplate)).all())
    assert count == len(CANONICAL_TEMPLATES)


def test_store_theme_settings_unique_per_store(db: Session) -> None:
    store = _store(db, "theme-uniq")
    db.add(ContentStoreThemeSettings(store_id=store.id, active_template_id="classic"))
    db.flush()
    db.add(ContentStoreThemeSettings(store_id=store.id, active_template_id="modern"))
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()


def test_content_is_store_scoped(db: Session) -> None:
    a = _store(db, "content-a")
    b = _store(db, "content-b")
    db.add(ContentPage(store_id=a.id, slug="about", title="About A"))
    db.add(ContentBanner(store_id=b.id, image_url="https://cdn/b.png"))
    db.flush()
    a_pages = db.exec(select(ContentPage).where(ContentPage.store_id == a.id)).all()
    b_pages = db.exec(select(ContentPage).where(ContentPage.store_id == b.id)).all()
    assert len(a_pages) == 1
    assert len(b_pages) == 0


def test_menu_with_items(db: Session) -> None:
    store = _store(db, "menu-store")
    menu = ContentMenu(store_id=store.id, name="Main", location=MenuLocation.header)
    db.add(menu)
    db.flush()
    db.add(ContentMenuItem(store_id=store.id, menu_id=menu.id, label="Home", url="/"))
    db.flush()
    items = db.exec(
        select(ContentMenuItem).where(ContentMenuItem.menu_id == menu.id)
    ).all()
    assert len(items) == 1
    assert items[0].label == "Home"


def test_theme_template_public_schema(db: Session) -> None:
    template = db.exec(
        select(ContentThemeTemplate).where(ContentThemeTemplate.id == "classic")
    ).one()
    public = ThemeTemplatePublic.model_validate(template)
    assert public.id == "classic"
    assert public.name
