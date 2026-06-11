"""Audit recording helper.

Adds the entry to the session; the caller commits it together with the audited
operation (so the action and its audit trail are one unit of work).
"""

import uuid

from sqlmodel import Session

from app.modules.audit.models import AuditLog


def record_audit(
    *,
    session: Session,
    user_id: uuid.UUID | None,
    action: str,
    store_id: uuid.UUID | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
) -> AuditLog:
    """Record a sensitive action in ``audit_logs``.

    Args:
        session: Active database session (the caller commits).
        user_id: The actor performing the action.
        action: The action key (e.g. ``platform.stores.block``).
        store_id: The affected store, when applicable.
        target_type: The affected entity type, when applicable.
        target_id: The affected entity id (as a string), when applicable.

    Returns:
        The audit-log entry, added to the session (not yet committed).
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        store_id=store_id,
        target_type=target_type,
        target_id=target_id,
    )
    session.add(entry)
    return entry
