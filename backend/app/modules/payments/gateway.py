"""Payment gateway seam (the integration point reserved for Fase 8).

In Fase 6 there is **no gateway**: the order stops at ``pending_payment`` and the
payment is arranged off-platform (the merchant marks it paid manually). The
checkout still calls :func:`get_gateway` after creating the order so Fase 8 can
swap the no-op for a real gateway (Pagar.me/Mercado Pago/…) without touching the
checkout flow.
"""

from typing import Protocol

from app.modules.orders.models import Order


class PaymentGateway(Protocol):
    """The interface a real gateway will implement in Fase 8."""

    def initiate(self, order: Order) -> None:
        """Start the payment for an order (charge/split/webhook in Fase 8)."""
        ...


class NoOpGateway:
    """No gateway (Fase 6): the order stays ``pending_payment`` (paid manually)."""

    def initiate(self, order: Order) -> None:
        """Do nothing — payment is arranged off-platform."""
        return None


def get_gateway() -> PaymentGateway:
    """Return the active payment gateway.

    Returns:
        The :class:`NoOpGateway` in Fase 6; Fase 8 selects a real gateway by
        configuration.
    """
    return NoOpGateway()
