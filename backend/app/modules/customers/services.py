"""Customer services: identity deduplication + guest sessions (doc 23).

``create_or_update_customer`` is a **public module service** (not embedded in a
route) so the checkout (``P6-CHK-01``) and the assisted customization (Fase 7)
can both reuse it. Identity is per-store, keyed by normalized email/phone.
"""

import secrets
import uuid
from datetime import timedelta

from sqlmodel import Session

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.customers import repositories as repo
from app.modules.customers.models import (
    CustomerAddress,
    CustomerGuestSession,
    CustomerProfile,
)
from app.modules.customers.normalization import normalize_email, normalize_phone
from app.modules.customers.schemas import AddressInput

GUEST_SESSION_TTL = timedelta(days=30)


def _same_address(stored: CustomerAddress, given: AddressInput) -> bool:
    """Return whether a stored address equals a given one (dedup of identicals)."""
    return (
        stored.recipient_name,
        stored.line1,
        stored.line2,
        stored.city,
        stored.state,
        stored.postal_code,
        stored.country,
    ) == (
        given.recipient_name,
        given.line1,
        given.line2,
        given.city,
        given.state,
        given.postal_code,
        given.country,
    )


def _add_address_if_new(
    session: Session,
    store_id: uuid.UUID,
    customer_id: uuid.UUID,
    address: AddressInput,
) -> None:
    """Append the address to the customer unless an identical one already exists."""
    for existing in repo.list_addresses(
        session=session, store_id=store_id, customer_id=customer_id
    ):
        if _same_address(existing, address):
            return
    session.add(
        CustomerAddress(
            store_id=store_id, customer_id=customer_id, **address.model_dump()
        )
    )
    session.commit()


def create_or_update_customer(
    *,
    session: Session,
    store_id: uuid.UUID,
    name: str,
    email: str | None = None,
    phone: str | None = None,
    region: str | None = None,
    address: AddressInput | None = None,
) -> CustomerProfile:
    """Find-or-create the store's customer from contact data (doc 23).

    Matches by normalized email, else ``phone_e164``, else creates. Applies
    **first-name-wins** (never overwrites the name), fills a missing email/phone
    only when it does not belong to another customer, resolves an email/phone
    conflict in favour of the **email**, and appends a new (non-duplicate)
    address.

    Args:
        session: Active database session.
        store_id: The store the customer belongs to.
        name: The contact name (used only when creating).
        email: The raw email, if given.
        phone: The raw local phone, if given (needs ``region``).
        region: ISO 3166-1 region for the phone (from the country selector).
        address: An address to append to the customer, if given.

    Returns:
        The matched-or-created :class:`CustomerProfile`.

    Raises:
        AppError: 422 if neither email nor phone is given, if a phone is given
            without a region, or if the phone is invalid for the region.
    """
    norm_email = normalize_email(email) if email else None
    norm_phone: str | None = None
    if phone:
        if not region:
            raise AppError(
                "missing_region",
                "A country is required to validate the phone",
                status_code=422,
            )
        norm_phone = normalize_phone(phone, region)
    if norm_email is None and norm_phone is None:
        raise AppError(
            "missing_contact", "An email or phone is required", status_code=422
        )

    customer: CustomerProfile | None = None
    if norm_email is not None:
        customer = repo.get_by_email(
            session=session, store_id=store_id, email=norm_email
        )
    if customer is None and norm_phone is not None:
        customer = repo.get_by_phone(
            session=session, store_id=store_id, phone_e164=norm_phone
        )

    if customer is None:
        customer = CustomerProfile(
            store_id=store_id, name=name, email=norm_email, phone_e164=norm_phone
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
    else:
        # First-name-wins: the name is left untouched. Fill a missing contact
        # only when it is not already owned by another customer (conflict → the
        # email match wins, and we never steal another customer's contact).
        changed = False
        if customer.email is None and norm_email is not None:
            if (
                repo.get_by_email(session=session, store_id=store_id, email=norm_email)
                is None
            ):
                customer.email = norm_email
                changed = True
        if customer.phone_e164 is None and norm_phone is not None:
            if (
                repo.get_by_phone(
                    session=session, store_id=store_id, phone_e164=norm_phone
                )
                is None
            ):
                customer.phone_e164 = norm_phone
                changed = True
        if changed:
            session.add(customer)
            session.commit()
            session.refresh(customer)

    if address is not None:
        _add_address_if_new(session, store_id, customer.id, address)
    return customer


def ensure_guest_session(
    *, session: Session, store_id: uuid.UUID, cookie_value: str | None
) -> tuple[CustomerGuestSession, bool]:
    """Return the store's guest session for the cookie, creating/renewing it.

    A valid (non-expired) cookie recovers the session and slides its expiry; an
    absent/unknown/expired cookie mints a new session.

    Args:
        session: Active database session.
        store_id: The store the session belongs to.
        cookie_value: The ``guest_session_id`` cookie value, if any.

    Returns:
        A ``(session, write_cookie)`` tuple — ``write_cookie`` is ``True`` when a
        new token was minted and the caller should (re)set the cookie.
    """
    now = get_datetime_utc()
    if cookie_value:
        existing = repo.get_guest_session(
            session=session, store_id=store_id, guest_session_id=cookie_value
        )
        if existing is not None and existing.expires_at > now:
            existing.expires_at = now + GUEST_SESSION_TTL
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing, False
    guest = CustomerGuestSession(
        store_id=store_id,
        guest_session_id=secrets.token_urlsafe(32),
        expires_at=now + GUEST_SESSION_TTL,
    )
    session.add(guest)
    session.commit()
    session.refresh(guest)
    return guest, True
