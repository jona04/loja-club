"""Enumerations for the checkout module."""

from enum import Enum


class CheckoutStatus(str, Enum):
    """Status of a checkout session (doc 23).

    - ``active``: checkout in progress (expires in ~24h).
    - ``completed``: the order was placed.

    Expired/abandoned cleanup (marking stale ``active`` sessions) is a follow-up.
    """

    active = "active"
    completed = "completed"
