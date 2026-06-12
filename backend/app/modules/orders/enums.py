"""Enumerations for the orders module."""

from enum import Enum


class OrderStatus(str, Enum):
    """Operational status of an order in the no-gateway phase (doc 11).

    ``pending_payment`` → ``paid`` (marked manually) → ``processing`` →
    ``shipped`` → ``delivered``; ``canceled`` at any allowed point (restocks).
    The payment statuses (``payment_failed``/``refunded``/``chargeback``) arrive
    with the gateway in Fase 8 — none is created here.
    """

    pending_payment = "pending_payment"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"
