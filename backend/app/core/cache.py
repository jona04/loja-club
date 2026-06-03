"""Redis client and small cache helpers."""

from typing import cast

from redis import Redis

from app.core.config import settings

# Shared client; the connection pool connects lazily on the first command.
redis_client: Redis = Redis.from_url(str(settings.REDIS_URL), decode_responses=True)


def get_redis() -> Redis:
    """Return the shared Redis client.

    Returns:
        The process-wide Redis client (string responses).
    """
    return redis_client


def _build_key(key: str, prefix: str) -> str:
    """Join an optional prefix and the key with ``:``.

    Args:
        key: Cache key.
        prefix: Optional prefix.

    Returns:
        ``"<prefix>:<key>"`` when a prefix is given, otherwise ``key``.
    """
    return f"{prefix}:{key}" if prefix else key


def cache_set(
    key: str, value: str, *, ttl: int | None = None, prefix: str = ""
) -> None:
    """Store a string value, optionally with a TTL and key prefix.

    Args:
        key: Cache key.
        value: String value to store.
        ttl: Optional time-to-live in seconds.
        prefix: Optional key prefix (joined with ``:``).
    """
    get_redis().set(_build_key(key, prefix), value, ex=ttl)


def cache_get(key: str, *, prefix: str = "") -> str | None:
    """Return a stored string value, or ``None`` if absent.

    Args:
        key: Cache key.
        prefix: Optional key prefix (joined with ``:``).

    Returns:
        The stored value, or ``None``.
    """
    return cast("str | None", get_redis().get(_build_key(key, prefix)))
