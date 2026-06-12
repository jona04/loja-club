"""Enumerations for the cart module."""

from enum import Enum


class CartStatus(str, Enum):
    """Lifecycle status of a cart.

    - ``active``: the customer's current cart (one active per guest/store).
    - ``converted``: turned into an order (set when the order is created,
      ``P6-ORD-01``); a new active cart is started afterwards.

    Abandoned/expired cleanup (30 days, doc 23) is a follow-up.
    """

    active = "active"
    converted = "converted"
