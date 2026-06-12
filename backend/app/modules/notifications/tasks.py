"""Worker tasks for the notifications module (arq).

Every email is sent here, on the worker — never inline in a request (INV-F5).
arq retries the task on failure, so a transient SMTP error does not lose the
email; the order is already persisted regardless.
"""

from typing import Any

from app.utils import send_email


async def send_order_email(
    _ctx: dict[str, Any], email_to: str, subject: str, html_content: str
) -> None:
    """Worker task: send a pre-rendered order email.

    Args:
        _ctx: arq worker context (unused).
        email_to: Recipient address.
        subject: Email subject line.
        html_content: Rendered HTML body.
    """
    send_email(  # pragma: no cover - worker I/O glue (SMTP)
        email_to=email_to, subject=subject, html_content=html_content
    )
