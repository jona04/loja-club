"""API request/response schemas for the stores module."""

import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.modules.stores.enums import MembershipStatus
from app.modules.stores.models import StoreBase, StoreSettingsBase


class StoreCreate(SQLModel):
    """Payload to create a store. The ``country`` derives currency/locale (P3-LOC-01)."""

    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    country: str = Field(min_length=2, max_length=2, description="ISO 3166-1 alpha-2")


class StorePublic(StoreBase):
    """Store as returned via the API."""

    id: uuid.UUID


class StoreSettingsUpdate(SQLModel):
    """Editable store settings (all optional)."""

    public_name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    logo_url: str | None = Field(default=None, max_length=2048)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=32)
    whatsapp_number: str | None = Field(default=None, max_length=32)
    address: str | None = None
    social_links: dict[str, str] | None = None


class StoreSettingsPublic(StoreSettingsBase):
    """Store settings as returned via the API."""

    id: uuid.UUID
    store_id: uuid.UUID
    social_links: dict[str, str] | None = None


class StoreMemberInvite(SQLModel):
    """Payload to invite a member by email with a role."""

    email: EmailStr
    role: str = Field(max_length=50)


class StoreMemberRoleUpdate(SQLModel):
    """Payload to change a member's role."""

    role: str = Field(max_length=50)


class StoreMemberPublic(SQLModel):
    """A store member as returned via the API."""

    id: uuid.UUID
    user_id: uuid.UUID
    email: EmailStr
    role: str
    status: MembershipStatus


class MyMembership(SQLModel):
    """The current user's role and permissions in the active store."""

    role: str
    permissions: list[str]
