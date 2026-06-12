"""Customers: normalization + dedup + guest sessions (P6-CUST-01)."""

from datetime import timedelta
from typing import Any

import pytest
from fastapi import Response
from sqlmodel import Session, select
from starlette.requests import Request

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.customers.deps import GUEST_COOKIE, guest_session
from app.modules.customers.models import CustomerAddress
from app.modules.customers.normalization import normalize_email, normalize_phone
from app.modules.customers.schemas import AddressInput
from app.modules.customers.services import (
    create_or_update_customer,
    ensure_guest_session,
)
from app.modules.stores.models import Store


def _store(db: Session, slug: str) -> Store:
    store = Store(name="Loja", slug=slug, currency="BRL", locale="pt-BR")
    db.add(store)
    db.flush()
    return store


# --- normalization (unit) ---


def test_normalize_email_trims_lowercases_keeps_dot_and_tag() -> None:
    assert (
        normalize_email("  Ana.Maria+promo@Email.com ") == "ana.maria+promo@email.com"
    )


@pytest.mark.parametrize(
    ("phone", "region", "expected"),
    [
        ("(86) 99999-0000", "BR", "+5586999990000"),
        ("(415) 555-0132", "US", "+14155550132"),
    ],
)
def test_normalize_phone_to_e164(phone: str, region: str, expected: str) -> None:
    assert normalize_phone(phone, region) == expected


@pytest.mark.parametrize("bad", ["123", "abc", ""])
def test_normalize_phone_invalid_raises(bad: str) -> None:
    # "123" parses but is invalid; "abc"/"" fail to parse — both 422.
    with pytest.raises(AppError) as exc:
        normalize_phone(bad, "BR")
    assert exc.value.code == "invalid_phone"


# --- dedup (integration) ---


def _cust(db: Session, store: Store, **kw: Any) -> Any:
    return create_or_update_customer(session=db, store_id=store.id, **kw)


def test_match_by_email_keeps_first_name(db: Session) -> None:
    store = _store(db, "cust-email")
    a = _cust(db, store, name="Ana", email="ana@x.com")
    b = _cust(db, store, name="Aninha", email="Ana@x.com")  # same email, other name
    assert a.id == b.id
    assert b.name == "Ana"  # first-name-wins


def test_match_by_phone(db: Session) -> None:
    store = _store(db, "cust-phone")
    a = _cust(db, store, name="Bia", phone="(86) 99999-0000", region="BR")
    b = _cust(db, store, name="Bia2", phone="86999990000", region="BR")
    assert a.id == b.id


def test_creates_when_no_match(db: Session) -> None:
    store = _store(db, "cust-new")
    a = _cust(db, store, name="Cris", email="cris@x.com")
    b = _cust(db, store, name="Dan", email="dan@x.com")
    assert a.id != b.id


def test_fills_missing_phone_when_free(db: Session) -> None:
    store = _store(db, "cust-fill")
    a = _cust(db, store, name="Eva", email="eva@x.com")
    assert a.phone_e164 is None
    again = _cust(
        db, store, name="Eva", email="eva@x.com", phone="(86) 99999-0001", region="BR"
    )
    assert again.id == a.id
    assert again.phone_e164 == "+5586999990001"


def test_fills_missing_email_when_free(db: Session) -> None:
    store = _store(db, "cust-fill-email")
    a = _cust(db, store, name="Fil", phone="(86) 99999-0003", region="BR")
    assert a.email is None
    again = _cust(
        db, store, name="Fil", phone="(86) 99999-0003", region="BR", email="fil@x.com"
    )
    assert again.id == a.id
    assert again.email == "fil@x.com"


def test_conflict_email_wins_without_stealing(db: Session) -> None:
    store = _store(db, "cust-conflict")
    b = _cust(db, store, name="Bob", phone="(86) 99999-0002", region="BR")
    a = _cust(db, store, name="Alice", email="alice@x.com")
    resolved = _cust(
        db,
        store,
        name="Alice",
        email="alice@x.com",
        phone="(86) 99999-0002",
        region="BR",
    )
    assert resolved.id == a.id  # the email match wins
    assert resolved.phone_e164 is None  # B's phone is not stolen
    db.refresh(b)
    assert b.phone_e164 == "+5586999990002"


def test_missing_contact_raises(db: Session) -> None:
    store = _store(db, "cust-nocontact")
    with pytest.raises(AppError) as exc:
        _cust(db, store, name="NoOne")
    assert exc.value.code == "missing_contact"


def test_phone_without_region_raises(db: Session) -> None:
    store = _store(db, "cust-noregion")
    with pytest.raises(AppError) as exc:
        _cust(db, store, name="X", phone="86999990000")
    assert exc.value.code == "missing_region"


def test_isolated_between_stores(db: Session) -> None:
    ca = _cust(db, _store(db, "cust-iso-a"), name="Ana", email="ana@x.com")
    cb = _cust(db, _store(db, "cust-iso-b"), name="Ana", email="ana@x.com")
    assert ca.id != cb.id


# --- addresses ---


def _addr(**kw: Any) -> AddressInput:
    base: dict[str, Any] = {"line1": "Rua A", "city": "SP", "country": "BR"}
    base.update(kw)
    return AddressInput(**base)


def test_address_added_and_deduped(db: Session) -> None:
    store = _store(db, "cust-addr")
    c = _cust(db, store, name="Ana", email="ana@x.com", address=_addr())
    _cust(db, store, name="Ana", email="ana@x.com", address=_addr())  # identical
    _cust(db, store, name="Ana", email="ana@x.com", address=_addr(line1="Rua B"))  # new
    addrs = db.exec(
        select(CustomerAddress).where(CustomerAddress.customer_id == c.id)
    ).all()
    assert {a.line1 for a in addrs} == {"Rua A", "Rua B"}


# --- guest sessions ---


def test_guest_session_created_then_recovered(db: Session) -> None:
    store = _store(db, "cust-guest")
    guest, write = ensure_guest_session(
        session=db, store_id=store.id, cookie_value=None
    )
    assert write is True
    again, write2 = ensure_guest_session(
        session=db, store_id=store.id, cookie_value=guest.guest_session_id
    )
    assert again.id == guest.id
    assert write2 is False


def test_guest_session_new_when_expired(db: Session) -> None:
    store = _store(db, "cust-guest-exp")
    guest, _ = ensure_guest_session(session=db, store_id=store.id, cookie_value=None)
    guest.expires_at = get_datetime_utc() - timedelta(days=1)
    db.add(guest)
    db.commit()
    fresh, write = ensure_guest_session(
        session=db, store_id=store.id, cookie_value=guest.guest_session_id
    )
    assert fresh.id != guest.id
    assert write is True


def test_guest_session_isolated_by_store(db: Session) -> None:
    guest, _ = ensure_guest_session(
        session=db, store_id=_store(db, "guest-iso-a").id, cookie_value=None
    )
    other, write = ensure_guest_session(
        session=db,
        store_id=_store(db, "guest-iso-b").id,
        cookie_value=guest.guest_session_id,
    )
    assert other.id != guest.id
    assert write is True


def test_guest_cookie_dependency_sets_httponly_cookie(db: Session) -> None:
    """The dependency mints a session and writes the HTTP-only cookie."""
    store = _store(db, "cust-cookie")
    request = Request({"type": "http", "headers": [], "method": "GET", "path": "/"})
    response = Response()
    guest = guest_session(request, response, store, db)
    set_cookie = response.headers.get("set-cookie", "")
    assert GUEST_COOKIE in set_cookie
    assert "httponly" in set_cookie.lower()
    assert guest.guest_session_id in set_cookie
