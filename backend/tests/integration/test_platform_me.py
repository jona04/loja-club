"""Integration tests for the platform ``/me`` identity endpoint."""

from fastapi.testclient import TestClient

from app.core.config import settings


def test_platform_me_superuser_is_admin(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/me", headers=superuser_token_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert body["is_platform_admin"] is True
    assert "platform_owner" in body["platform_roles"]


def test_platform_me_normal_user_not_admin(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/platform/me", headers=normal_user_token_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert body["is_platform_admin"] is False
    assert body["platform_roles"] == []


def test_platform_me_requires_login(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/platform/me")
    assert r.status_code == 401
