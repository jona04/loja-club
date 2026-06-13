"""Worker tasks for the customization module (arq)."""

from typing import Any

from sqlmodel import Session

from app.core.db import engine
from app.modules.customization import sessions


async def expire_customization_sessions(_ctx: dict[Any, Any]) -> int:
    """Worker cron: sweep customization sessions past their 30-day expiry.

    Args:
        _ctx: arq worker context (unused; ``dict[Any, Any]`` to satisfy arq's
            ``cron`` coroutine signature).

    Returns:
        How many sessions were marked expired.
    """
    with Session(engine) as session:  # pragma: no cover - worker I/O glue
        return sessions.expire_sessions(session=session)
