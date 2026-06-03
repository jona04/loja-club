"""Sample integration tests for the health endpoints and the Redis cache."""

from fastapi.testclient import TestClient

from app.core.cache import cache_get, cache_set


def test_health_ok(client: TestClient) -> None:
    """``/health`` returns ok.

    Args:
        client: The test HTTP client.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_redis_ok(client: TestClient) -> None:
    """``/health/redis`` returns ok when Redis is reachable.

    Args:
        client: The test HTTP client.
    """
    response = client.get("/health/redis")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cache_set_get_roundtrip() -> None:
    """``cache_set`` followed by ``cache_get`` returns the stored value."""
    cache_set("k1", "v1", ttl=60, prefix="test")
    assert cache_get("k1", prefix="test") == "v1"
