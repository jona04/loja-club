"""Email and phone normalization for customer identity/dedup (doc 23)."""

import phonenumbers

from app.core.api import AppError


def normalize_email(email: str) -> str:
    """Normalize an email to its deduplication key (trim + lowercase).

    Dots and ``+tag`` suffixes are kept on purpose — removing them would merge
    distinct addresses (doc 23).

    Args:
        email: The raw email entered by the customer.

    Returns:
        The trimmed, lowercased email.
    """
    return email.strip().lower()


def normalize_phone(phone: str, region: str) -> str:
    """Normalize a local phone number to E.164 for the given region (doc 23).

    The country is not typed by the customer — it comes from the checkout's
    country selector (ISO 3166-1 region). The library validates and renders the
    number, so no per-country rule is hard-coded.

    Args:
        phone: The local phone number as entered.
        region: The ISO 3166-1 alpha-2 region (e.g. ``BR``, ``US``).

    Returns:
        The phone in E.164 (``+<country><national number>``).

    Raises:
        AppError: 422 if the number is invalid for the region.
    """
    try:
        parsed = phonenumbers.parse(phone, region)
    except phonenumbers.NumberParseException as exc:
        raise AppError(
            "invalid_phone", "Invalid phone number", status_code=422
        ) from exc
    if not phonenumbers.is_valid_number(parsed):
        raise AppError("invalid_phone", "Invalid phone number", status_code=422)
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
