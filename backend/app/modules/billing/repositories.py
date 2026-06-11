"""Data access and seed for billing plan definitions."""

from sqlmodel import Session, col, select

from app.modules.billing.models import BillingPlan


def seed_billing_plans(*, session: Session) -> None:
    """Seed the initial plan definitions (idempotent).

    Args:
        session: Active database session used to query and seed.
    """
    plans = [
        ("free", "Free", 0, "BRL", 500, "Bom para aquisição inicial"),
        ("starter", "Starter", 4990, "BRL", 300, "Entrada para lojistas pequenos"),
        ("pro", "Pro", 9990, "BRL", 150, "Plano principal"),
        ("business", "Business", 19990, "BRL", 50, "Para lojistas com maior volume"),
    ]
    for key, name, price, currency, bps, description in plans:
        existing = session.exec(
            select(BillingPlan).where(
                BillingPlan.key == key, col(BillingPlan.deleted_at).is_(None)
            )
        ).first()
        if existing is None:
            session.add(
                BillingPlan(
                    key=key,
                    name=name,
                    monthly_price_amount_minor=price,
                    monthly_price_currency=currency,
                    commission_bps=bps,
                    description=description,
                )
            )
    session.commit()
