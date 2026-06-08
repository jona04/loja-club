"""API request/response schemas for account users."""

import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.modules.accounts.models import UserBase


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


class UserPublic(UserBase):
    """Account user as returned via the API."""

    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    """Paginated list of account users."""

    data: list[UserPublic]
    count: int
