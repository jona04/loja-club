"""Async task queue (arq).

The rest of the app enqueues work only through :func:`enqueue`, staying
decoupled from the queue library. Tasks are registered in
:class:`WorkerSettings` and run by the ``worker`` service
(``arq app.core.queue.WorkerSettings``).
"""

from typing import Any

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings
from app.modules.media.tasks import generate_image_variants


def _redis_settings() -> RedisSettings:
    """Return arq Redis settings derived from the app settings.

    Returns:
        The :class:`~arq.connections.RedisSettings` for the worker/pool.
    """
    return RedisSettings.from_dsn(str(settings.REDIS_URL))


async def enqueue(task_name: str, *args: Any, **kwargs: Any) -> None:
    """Enqueue a background job by task name.

    The rest of the app uses only this function, staying decoupled from arq.

    Args:
        task_name: Name of a function registered in ``WorkerSettings.functions``.
        *args: Positional arguments forwarded to the task.
        **kwargs: Keyword arguments forwarded to the task.
    """
    pool = await create_pool(_redis_settings())
    try:
        await pool.enqueue_job(task_name, *args, **kwargs)
    finally:
        await pool.aclose()


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
