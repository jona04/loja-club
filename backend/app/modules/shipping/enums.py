"""Enumerations for the shipping module."""

from enum import Enum


class ShippingMethodType(str, Enum):
    """A store's shipping/delivery option offered at checkout (doc 11).

    - ``fixed_shipping``: a flat shipping fee (``price_amount_minor``).
    - ``free_shipping``: free, optionally above a minimum order
      (``min_order_amount_minor``).
    - ``local_pickup``: the customer picks the order up; no fee.
    - ``private_delivery``: delivery arranged with the store after the purchase
      (no automatic price/ETA — the checkout/order makes that clear).
    """

    fixed_shipping = "fixed_shipping"
    free_shipping = "free_shipping"
    local_pickup = "local_pickup"
    private_delivery = "private_delivery"
