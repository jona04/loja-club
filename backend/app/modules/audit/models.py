"""Audit log table (``audit_logs``).

Records sensitive actions (admin operations such as blocking a store or
impersonating a user). This is the minimal table; login/security events,
retention and hardening are added later.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index
from sqlmodel import Field

from app.db.base import UUIDMixin, get_datetime_utc


class AuditLog(UUIDMixin, table=True):
    """A recorded sensitive action. Append-only."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_store_created", "store_id", "created_at"),
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
    )

    store_id: uuid.UUID | None = Field(default=None, foreign_key="store_stores.id")
    user_id: uuid.UUID | None = Field(default=None, foreign_key="account_users.id")
    action: str = Field(max_length=100, index=True)
    target_type: str | None = Field(default=None, max_length=50)
    target_id: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
