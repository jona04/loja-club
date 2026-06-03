"""Sample integration test for the arq task queue (enqueue + worker)."""

import asyncio

from arq.connections import RedisSettings
from arq.worker import Worker

from app.core.cache import get_redis
from app.core.config import settings
from app.core.queue import dummy_task, enqueue


def test_enqueue_dummy_task_is_processed_by_worker() -> None:
    """enqueue() schedules dummy_task and a burst worker runs it end to end.

    The worker executes the task, which writes ``queue:dummy:<marker>`` to
    Redis; asserting that key proves the enqueue -> process round trip.
    """
    marker = "p0-cfg-04"
    redis = get_redis()
    redis.delete(f"queue:dummy:{marker}")

    async def scenario() -> None:
        await enqueue("dummy_task", marker)
        worker = Worker(
            functions=[dummy_task],
            redis_settings=RedisSettings.from_dsn(str(settings.REDIS_URL)),
            burst=True,
            poll_delay=0.0,
            handle_signals=False,
        )
        try:
            await worker.async_run()
        finally:
            await worker.close()

    asyncio.run(scenario())

    assert redis.get(f"queue:dummy:{marker}") == "done"
