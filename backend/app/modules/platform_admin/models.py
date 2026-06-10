"""Platform-admin role assignments (``platform_admin_roles``).

Maps an ``account_users`` user to a **global** platform role; there is no
per-store scope here. The permission catalog/map lives in ``permissions.py``
(in code) — only this assignment table is persisted.
"""

import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.db.base import TimestampMixin, UUIDMixin


class PlatformAdminRole(UUIDMixin, TimestampMixin, table=True):
    """A global platform role granted to an account user."""

    __tablename__ = "platform_admin_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role", name="uq_platform_admin_role_user_role"),
    )

    user_id: uuid.UUID = Field(foreign_key="account_users.id", index=True)
    role: str = Field(max_length=50, index=True)
