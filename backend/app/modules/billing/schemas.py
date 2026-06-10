"""API schemas for billing plan definitions."""

import uuid

from sqlmodel import Field, SQLModel

from app.modules.billing.models import BillingPlanBase


class BillingPlanCreate(BillingPlanBase):
    """Payload to create a plan definition."""


class BillingPlanUpdate(SQLModel):
    """Patch payload for a plan definition (unset fields are ignored)."""

    name: str | None = Field(default=None, max_length=100)
    monthly_price_amount_minor: int | None = Field(default=None, ge=0)
    monthly_price_currency: str | None = Field(default=None, max_length=3)
    commission_bps: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class BillingPlanPublic(BillingPlanBase):
    """A plan definition as returned via the API."""

    id: uuid.UUID
