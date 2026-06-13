"""Enumerations for the discounts module."""

from enum import Enum


class CouponType(str, Enum):
    """How a coupon's ``value`` is interpreted (doc 09).

    ``percentage`` — ``value`` is a percent (1..100) off the subtotal.
    ``fixed`` — ``value`` is a fixed amount (minor units, store currency) off.
    """

    percentage = "percentage"
    fixed = "fixed"
