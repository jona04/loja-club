"""Base SQLModel mixins and helpers shared by domain models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    """Return the current time as a timezone-aware UTC datetime.

    Returns:
        The current time with UTC tzinfo set.
    """
    return datetime.now(timezone.utc)


class UUIDMixin(SQLModel):
    """Mixin adding a UUID primary key."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class TimestampMixin(SQLModel):
    """Mixin adding timezone-aware ``created_at`` / ``updated_at`` timestamps."""

    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": get_datetime_utc},
    )


class SoftDeleteMixin(SQLModel):
    """Mixin adding soft-delete columns (business records are never hard-deleted)."""

    deleted_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    deleted_by_user_id: uuid.UUID | None = Field(default=None)
    delete_reason: str | None = Field(default=None, max_length=255)


class StoreScopedMixin(SQLModel):
    """Mixin adding a ``store_id`` foreign key to isolate per-store data."""

    store_id: uuid.UUID = Field(foreign_key="store_stores.id", index=True)
