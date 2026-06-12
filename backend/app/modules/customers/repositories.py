"""Customer repositories: identity, address and guest-session lookups."""

import uuid

from sqlmodel import Session, col, select

from app.modules.customers.models import (
    CustomerAddress,
    CustomerGuestSession,
    CustomerProfile,
)


def get_by_email(
    *, session: Session, store_id: uuid.UUID, email: str
) -> CustomerProfile | None:
    """Return the store's active customer with that normalized email, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        email: Normalized email (dedup key).

    Returns:
        The matching :class:`CustomerProfile`, or ``None``.
    """
    return session.exec(
        select(CustomerProfile).where(
            CustomerProfile.store_id == store_id,
            CustomerProfile.email == email,
            col(CustomerProfile.deleted_at).is_(None),
        )
    ).first()


def get_by_phone(
    *, session: Session, store_id: uuid.UUID, phone_e164: str
) -> CustomerProfile | None:
    """Return the store's active customer with that ``phone_e164``, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        phone_e164: Normalized phone (E.164 dedup key).

    Returns:
        The matching :class:`CustomerProfile`, or ``None``.
    """
    return session.exec(
        select(CustomerProfile).where(
            CustomerProfile.store_id == store_id,
            CustomerProfile.phone_e164 == phone_e164,
            col(CustomerProfile.deleted_at).is_(None),
        )
    ).first()


def list_addresses(
    *, session: Session, store_id: uuid.UUID, customer_id: uuid.UUID
) -> list[CustomerAddress]:
    """Return a customer's active addresses.

    Args:
        session: Active database session.
        store_id: The owning store.
        customer_id: The customer whose addresses are listed.

    Returns:
        The customer's non-deleted :class:`CustomerAddress` rows.
    """
    return list(
        session.exec(
            select(CustomerAddress).where(
                CustomerAddress.store_id == store_id,
                CustomerAddress.customer_id == customer_id,
                col(CustomerAddress.deleted_at).is_(None),
            )
        ).all()
    )


def get_guest_session(
    *, session: Session, store_id: uuid.UUID, guest_session_id: str
) -> CustomerGuestSession | None:
    """Return the store's guest session for a token, or ``None``.

    Args:
        session: Active database session.
        store_id: The owning store.
        guest_session_id: The cookie token.

    Returns:
        The matching :class:`CustomerGuestSession`, or ``None``.
    """
    return session.exec(
        select(CustomerGuestSession).where(
            CustomerGuestSession.store_id == store_id,
            CustomerGuestSession.guest_session_id == guest_session_id,
        )
    ).first()
