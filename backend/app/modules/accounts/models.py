"""Account-user models: platform/admin and merchant staff users.

These are the users who sign in to the dashboard/admin (``account_users``),
as opposed to store customers (handled later in the ``customers`` module).
"""

import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.db.base import get_datetime_utc


class UserBase(SQLModel):
    """Shared account-user fields."""

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Payload to create an account user."""

    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    """Self-registration payload."""

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    """Admin update payload (all fields optional)."""

    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    """Self profile-update payload."""

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Self password-change payload."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    """Account-user table (admin, merchant owner and staff)."""

    __tablename__ = "account_users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class UserPublic(UserBase):
    """Account user as returned via the API."""

    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    """Paginated list of account users."""

    data: list[UserPublic]
    count: int
