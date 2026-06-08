"""Async task queue (arq).

The rest of the app enqueues work only through :func:`enqueue`, staying
decoupled from the queue library. Tasks are registered in
:class:`WorkerSettings` and run by the ``worker`` service
(``arq app.core.queue.WorkerSettings``).
"""

from typing import Any

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings
from app.modules.media.tasks import generate_image_variants


def _redis_settings() -> RedisSettings:
    """Return arq Redis settings derived from the app settings.

    Returns:
        The :class:`~arq.connections.RedisSettings` for the worker/pool.
    """
    return RedisSettings.from_dsn(str(settings.REDIS_URL))


_pool: ArqRedis | None = None


async def _get_pool() -> ArqRedis:
    """Return the shared arq Redis pool, creating it on first use (INV-F6).

    Returns:
        The process-wide :class:`~arq.connections.ArqRedis` pool.
    """
    global _pool
    if _pool is None:
        _pool = await create_pool(_redis_settings())
    return _pool


async def enqueue(task_name: str, *args: Any, **kwargs: Any) -> None:
    """Enqueue a background job by task name.

    The rest of the app uses only this function, staying decoupled from arq, and
    reuses a single long-lived pool (INV-F6).

    Args:
        task_name: Name of a function registered in ``WorkerSettings.functions``.
        *args: Positional arguments forwarded to the task.
        **kwargs: Keyword arguments forwarded to the task.
    """
    pool = await _get_pool()
    await pool.enqueue_job(task_name, *args, **kwargs)


async def close_pool() -> None:
    """Close the shared arq pool (call on application shutdown).

    Resets the cache so a later call rebuilds the pool on the active loop.
    """
    global _pool
    pool, _pool = _pool, None
    if pool is not None:
        try:
            await pool.aclose()
        except RuntimeError:  # pragma: no cover - cross-loop close in tests
            pass


async def dummy_task(ctx: dict[str, Any], marker: str) -> str:
    """Example no-op task that writes a marker to Redis to prove processing.

    Args:
        ctx: arq worker context (the Redis pool is under ``"redis"``).
        marker: Token written to ``queue:dummy:<marker>``.

    Returns:
        The received marker.
    """
    await ctx["redis"].set(f"queue:dummy:{marker}", "done")
    return marker


class WorkerSettings:
    """arq worker configuration (registered functions + Redis connection)."""

    functions = [dummy_task, generate_image_variants]
    redis_settings = _redis_settings()
