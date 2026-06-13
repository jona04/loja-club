"""Integration tests for the platform-admin 3D catalog routes."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.modules.customization import repositories
from app.modules.customization.repositories import MUG_SLUG

_BASE = f"{settings.API_V1_STR}/platform/3d-models"


def _mug_ids(db: Session) -> tuple[str, str]:
    """Return the seeded mug's (model_id, active_version_id) as strings."""
    mug = next(
        m for m in repositories.list_all_models(session=db) if m.slug == MUG_SLUG
    )
    version = repositories.get_active_version(session=db, model_id=mug.id)
    assert version is not None
    return str(mug.id), str(version.id)


def test_list_requires_platform_permission(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(_BASE, headers=normal_user_token_headers)
    assert response.status_code == 403


def test_list_includes_active_version(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(_BASE, headers=superuser_token_headers)
    assert response.status_code == 200
    mug = next(m for m in response.json() if m["slug"] == MUG_SLUG)
    assert mug["is_active"] is True
    assert mug["active_version"]["version"] == 1


def test_toggle_hides_model_from_public_catalog(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    model_id, _ = _mug_ids(db)
    response = client.patch(
        f"{_BASE}/{model_id}",
        json={"is_active": False},
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    public = client.get(
        f"{settings.API_V1_STR}/3d-catalog/models",
        headers=superuser_token_headers,
    )
    slugs = {m["slug"] for m in public.json()}
    assert MUG_SLUG not in slugs


def test_update_version_persists_printable_areas(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    _, version_id = _mug_ids(db)
    new_areas = [{"id": "front", "label": "Frente", "max_layers": 3}]
    response = client.patch(
        f"{_BASE}/versions/{version_id}",
        json={"printable_areas": new_areas},
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["printable_areas"] == new_areas


def test_update_version_rejects_malformed_area(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    _, version_id = _mug_ids(db)
    response = client.patch(
        f"{_BASE}/versions/{version_id}",
        json={"printable_areas": [{"label": "no id"}]},
        headers=superuser_token_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_printable_area"


def test_update_missing_model_returns_404(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{_BASE}/00000000-0000-0000-0000-000000000000",
        json={"is_active": False},
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
