"""Money value object: an amount in minor units plus an ISO 4217 currency.

Money is **never** a bare number. A monetary value is always
``(amount_minor, currency)``. Persisted models store two columns per value —
``<name>_amount_minor: int`` and ``<name>_currency: str`` (length 3) — and build
a :class:`Money` in code. The minor-unit exponent is not fixed at 2; it comes
from the currency (via babel), so JPY (0 decimals) or BHD (3) work without
special-casing.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from babel.numbers import format_currency, get_currency_precision


class CurrencyMismatchError(Exception):
    """Raised when combining two Money values with different currencies."""


@dataclass(frozen=True)
class Money:
    """An immutable monetary amount.

    Attributes:
        amount_minor: Amount in the currency's minor units (e.g. cents).
        currency: ISO 4217 currency code (e.g. ``"USD"``, ``"BRL"``, ``"JPY"``).
    """

    amount_minor: int
    currency: str

    def __post_init__(self) -> None:
        """Validate the currency code.

        Raises:
            ValueError: If the currency code is not exactly 3 characters.
        """
        if len(self.currency) != 3:
            raise ValueError(f"Invalid ISO 4217 currency code: {self.currency!r}")

    def _check_same_currency(self, other: Money) -> None:
        """Ensure ``other`` shares this currency.

        Args:
            other: The Money to compare with.

        Raises:
            CurrencyMismatchError: If the currencies differ.
        """
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot combine {self.currency} with {other.currency}"
            )

    def __add__(self, other: Money) -> Money:
        """Return the sum of two amounts of the same currency.

        Args:
            other: The Money to add.

        Returns:
            A new Money with the summed minor units.

        Raises:
            CurrencyMismatchError: If the currencies differ.
        """
        self._check_same_currency(other)
        return Money(self.amount_minor + other.amount_minor, self.currency)

    def __sub__(self, other: Money) -> Money:
        """Return the difference of two amounts of the same currency.

        Args:
            other: The Money to subtract.

        Returns:
            A new Money with the subtracted minor units.

        Raises:
            CurrencyMismatchError: If the currencies differ.
        """
        self._check_same_currency(other)
        return Money(self.amount_minor - other.amount_minor, self.currency)

    def __mul__(self, quantity: int) -> Money:
        """Return the amount multiplied by an integer quantity.

        Args:
            quantity: Integer multiplier (e.g. a cart line quantity).

        Returns:
            A new Money scaled by ``quantity``.
        """
        return Money(self.amount_minor * quantity, self.currency)

    def apply_rate(self, rate: Decimal) -> Money:
        """Return the amount multiplied by a decimal rate, rounded half-up.

        Used for commissions and percentage discounts (e.g. ``Decimal("0.015")``).

        Args:
            rate: The multiplier as a Decimal.

        Returns:
            A new Money with the rounded minor units (``ROUND_HALF_UP``).
        """
        scaled = (Decimal(self.amount_minor) * rate).quantize(
            Decimal(1), rounding=ROUND_HALF_UP
        )
        return Money(int(scaled), self.currency)

    @property
    def decimal_amount(self) -> Decimal:
        """Return the amount in major units as a Decimal.

        Returns:
            The minor amount divided by ``10 ** precision`` for the currency.
        """
        precision: int = get_currency_precision(self.currency)
        return Decimal(self.amount_minor) / (Decimal(10) ** precision)

    def format(self, locale: str = "en_US") -> str:
        """Format the amount for display in the given locale.

        Args:
            locale: A locale tag (``"en_US"``, ``"en-US"`` or ``"pt_BR"``).

        Returns:
            The localized currency string, respecting the currency's decimals.
        """
        formatted: str = format_currency(
            self.decimal_amount, self.currency, locale=locale.replace("-", "_")
        )
        return formatted
