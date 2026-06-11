"""Unit tests for the store localization helper (P3-LOC-01)."""

import pytest

from app.core.api import AppError
from app.core.localization import localize_country


def test_localize_known_countries() -> None:
    assert localize_country("BR") == {
        "currency": "BRL",
        "locale": "pt-BR",
        "symbol": "R$",
    }
    assert localize_country("US")["currency"] == "USD"
    assert localize_country("US")["symbol"] == "$"
    assert localize_country("PT")["currency"] == "EUR"


def test_localize_is_case_insensitive() -> None:
    assert localize_country("br") == localize_country("BR")


def test_localize_unknown_country_raises() -> None:
    with pytest.raises(AppError) as exc:
        localize_country("ZZ")
    assert exc.value.status_code == 422
    assert exc.value.code == "country_not_supported"
