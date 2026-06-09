"""Store localization: country (ISO 3166-1) → currency/locale/symbol (P3-LOC-01).

A store picks its **country** and the platform derives the **currency** (ISO 4217),
the **locale** and the **symbol**. The symbol is convenience-only — the frontends
derive it via ``Intl.NumberFormat`` from currency + locale; the curated map keeps
the supported countries explicit (not a hand-maintained list of all ~250).
"""

from app.core.api import AppError

# Curated supported countries → {currency, locale, symbol}. Add more as needed.
COUNTRY_LOCALIZATION: dict[str, dict[str, str]] = {
    "BR": {"currency": "BRL", "locale": "pt-BR", "symbol": "R$"},
    "PT": {"currency": "EUR", "locale": "pt-PT", "symbol": "€"},
    "US": {"currency": "USD", "locale": "en-US", "symbol": "$"},
    "GB": {"currency": "GBP", "locale": "en-GB", "symbol": "£"},
    "CA": {"currency": "CAD", "locale": "en-CA", "symbol": "$"},
    "ES": {"currency": "EUR", "locale": "es-ES", "symbol": "€"},
    "FR": {"currency": "EUR", "locale": "fr-FR", "symbol": "€"},
    "DE": {"currency": "EUR", "locale": "de-DE", "symbol": "€"},
    "IT": {"currency": "EUR", "locale": "it-IT", "symbol": "€"},
    "MX": {"currency": "MXN", "locale": "es-MX", "symbol": "$"},
    "AR": {"currency": "ARS", "locale": "es-AR", "symbol": "$"},
    "CL": {"currency": "CLP", "locale": "es-CL", "symbol": "$"},
    "CO": {"currency": "COP", "locale": "es-CO", "symbol": "$"},
    "UY": {"currency": "UYU", "locale": "es-UY", "symbol": "$"},
    "PY": {"currency": "PYG", "locale": "es-PY", "symbol": "₲"},
}

DEFAULT_COUNTRY = "BR"

SUPPORTED_COUNTRIES: list[str] = sorted(COUNTRY_LOCALIZATION)


def localize_country(country: str) -> dict[str, str]:
    """Return ``{currency, locale, symbol}`` for an ISO 3166-1 alpha-2 country.

    Args:
        country: ISO 3166-1 alpha-2 code (case-insensitive, e.g. ``"BR"``).

    Returns:
        Mapping with ``currency`` (ISO 4217), ``locale`` and ``symbol``.

    Raises:
        AppError: 422 if the country is not supported yet.
    """
    info = COUNTRY_LOCALIZATION.get(country.upper())
    if info is None:
        raise AppError(
            "country_not_supported",
            f"Country {country!r} is not supported yet",
            422,
        )
    return info
