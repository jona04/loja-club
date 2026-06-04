"""Account-user table and its shared base.

These are the users who sign in to the dashboard/admin (``account_users``), as
opposed to store customers (handled later in the ``customers`` module). API
request/response schemas live in ``schemas.py``.
"""

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class UserBase(SQLModel):
    """Shared account-user fields."""

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, UserBase, table=True):
    """Account-user table (admin, merchant owner and staff)."""

    __tablename__ = "account_users"

    hashed_password: str
