"""Integration tests for platform-admin template operations."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.api import AppError
from app.core.config import settings
from app.modules.content.models import ContentThemeTemplate
from app.modules.platform_admin import services
from app.modules.platform_admin.schemas import ThemeTemplateCreate, ThemeTemplateUpdate


def test_seed_loads_settings_schema(db: Session) -> None:
    aurora = db.get(ContentThemeTemplate, "aurora")
    assert aurora is not None
    assert aurora.settings_schema is not None
    keys = {field["key"] for field in aurora.settings_schema}
    assert "announcement_text" in keys
    assert "hero_subtitle" in keys


def test_list_templates(db: Session) -> None:
    ids = {t.id for t in services.list_templates(session=db)}
    assert {"aurora", "bazar", "studio"} <= ids


def test_get_template_includes_schema(db: Session) -> None:
    template = services.get_template(session=db, template_id="studio")
    assert template.id == "studio"
    keys = {field["key"] for field in (template.settings_schema or [])}
    assert "show_filters" in keys


def test_get_template_not_found(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        services.get_template(session=db, template_id="nope")
    assert exc.value.status_code == 404


def test_create_template_duplicate_id_conflict(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        services.create_template(
            session=db, payload=ThemeTemplateCreate(id="aurora", name="Aurora 2")
        )
    assert exc.value.status_code == 409


def test_create_and_update_template(db: Session) -> None:
    created = services.create_template(
        session=db,
        payload=ThemeTemplateCreate(id="custom", name="Custom", is_active=False),
    )
    assert created.id == "custom"
    assert created.is_active is False
    updated = services.update_template(
        session=db, template_id="custom", payload=ThemeTemplateUpdate(is_active=True)
    )
    assert updated.is_active is True


def test_list_templates_requires_platform_permission(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/templates",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_list_templates_over_http(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/templates", headers=superuser_token_headers
    )
    assert r.status_code == 200
    ids = {t["id"] for t in r.json()}
    assert {"aurora", "bazar", "studio"} <= ids
