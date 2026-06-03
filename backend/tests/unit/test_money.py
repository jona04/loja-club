"""Unit tests for the Money value object."""

from decimal import Decimal

import pytest

from app.core.money import CurrencyMismatchError, Money


def test_add_same_currency() -> None:
    """Adding two same-currency amounts sums the minor units."""
    assert Money(1990, "USD") + Money(10, "USD") == Money(2000, "USD")


def test_subtract_same_currency() -> None:
    """Subtracting two same-currency amounts subtracts the minor units."""
    assert Money(2000, "BRL") - Money(500, "BRL") == Money(1500, "BRL")


def test_combining_different_currencies_raises() -> None:
    """Combining different currencies raises CurrencyMismatchError."""
    with pytest.raises(CurrencyMismatchError):
        _ = Money(100, "USD") + Money(100, "BRL")


def test_multiply_by_quantity() -> None:
    """Multiplying by an integer scales the minor units."""
    assert Money(1990, "USD") * 3 == Money(5970, "USD")


def test_apply_rate_rounds_half_up() -> None:
    """apply_rate multiplies by a decimal rate and rounds half-up."""
    assert Money(101, "USD").apply_rate(Decimal("0.5")) == Money(51, "USD")  # 50.5 → 51
    assert Money(10000, "USD").apply_rate(Decimal("0.015")) == Money(150, "USD")


def test_decimal_amount_respects_currency_precision() -> None:
    """decimal_amount uses the currency exponent, not a fixed 2 decimals."""
    assert Money(1990, "USD").decimal_amount == Decimal("19.90")
    assert Money(1990, "JPY").decimal_amount == Decimal("1990")  # 0 decimals
    assert Money(1990, "BHD").decimal_amount == Decimal("1.990")  # 3 decimals


def test_format_two_and_zero_decimal_currencies() -> None:
    """Formatting respects 2-decimal and 0-decimal currencies."""
    assert "19.90" in Money(1990, "USD").format("en_US")
    jpy = Money(1990, "JPY").format("en_US")
    assert "." not in jpy
    assert "1,990" in jpy


def test_invalid_currency_code_raises() -> None:
    """A currency code that is not 3 characters raises ValueError."""
    with pytest.raises(ValueError):
        _ = Money(100, "US")
