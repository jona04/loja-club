"""Billing tables: subscription plan definitions (``billing_plans``).

Money is stored as ``*_amount_minor`` (int) + ``*_currency`` (ISO 4217); the
commission is stored in basis points (``500`` = 5%) to keep it exact.
"""

from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel

from app.db.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class BillingPlanBase(SQLModel):
    """Shared plan-definition fields."""

    key: str = Field(max_length=50, description="Stable plan identifier")
    name: str = Field(max_length=100)
    monthly_price_amount_minor: int = Field(
        ge=0, description="Monthly price in minor units"
    )
    monthly_price_currency: str = Field(
        max_length=3, description="ISO 4217 currency code"
    )
    commission_bps: int = Field(
        ge=0, description="Commission per sale in basis points (500 = 5%)"
    )
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class BillingPlan(
    UUIDMixin, TimestampMixin, SoftDeleteMixin, BillingPlanBase, table=True
):
    """A Kriar subscription plan definition.

    ``key`` is unique among non-deleted plans (partial unique index), so a
    deleted plan's key can be reused.
    """

    __tablename__ = "billing_plans"
    __table_args__ = (
        Index(
            "ix_billing_plans_key_active",
            "key",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
