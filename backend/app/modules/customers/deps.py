"""Customer dependencies: the guest-session cookie (public storefront).

Used by the public cart/checkout (host-resolved): resolves or mints the per-store
guest session and writes an HTTP-only cookie. The store comes from the request
``Host`` (``get_published_store``).
"""

from typing import Annotated

from fastapi import Depends, Request, Response

from app.api.deps import SessionDep
from app.modules.customers.models import CustomerGuestSession
from app.modules.customers.services import GUEST_SESSION_TTL, ensure_guest_session
from app.modules.storefront.deps import get_published_store
from app.modules.stores.models import Store

GUEST_COOKIE = "guest_session_id"

PublishedStore = Annotated[Store, Depends(get_published_store)]


def guest_session(
    request: Request,
    response: Response,
    store: PublishedStore,
    session: SessionDep,
) -> CustomerGuestSession:
    """Resolve (or create) the request's guest session, setting the cookie.

    Reads the ``guest_session_id`` cookie; recovers the session when valid,
    otherwise mints a new one and writes an HTTP-only cookie (30 days).

    Args:
        request: The incoming request (carries the cookie + the store host).
        response: The response the cookie is written to.
        store: The resolved, published store.
        session: Active database session.

    Returns:
        The store's :class:`CustomerGuestSession` for this browser.
    """
    cookie_value = request.cookies.get(GUEST_COOKIE)
    guest, write_cookie = ensure_guest_session(
        session=session, store_id=store.id, cookie_value=cookie_value
    )
    if write_cookie:
        response.set_cookie(
            GUEST_COOKIE,
            guest.guest_session_id,
            max_age=int(GUEST_SESSION_TTL.total_seconds()),
            httponly=True,
            samesite="lax",
        )
    return guest
