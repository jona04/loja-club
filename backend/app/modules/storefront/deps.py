"""Storefront dependency: resolve the published store from the request ``Host``.

Public (no-auth) — the customer reaches a store by its host. Only an **active**
store is served; anything else (unknown host, ``draft``/``paused``/...) renders
the same "loja não encontrada" without leaking internal data (INV-T4).
"""

from fastapi import Request

from app.api.deps import SessionDep
from app.core.api import AppError
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store
from app.modules.tenancy.services import resolve_store_by_host


def get_published_store(request: Request, session: SessionDep) -> Store:
    """Resolve the active store for the request ``Host``, or 404.

    Args:
        request: The incoming request (its ``Host`` header selects the store).
        session: Active database session.

    Returns:
        The resolved, published (``active``) store.

    Raises:
        AppError: 404 if the host is unknown or the store is not published.
    """
    host = (request.headers.get("host") or "").split(":")[0]
    store = resolve_store_by_host(session=session, host=host)
    if store is None or store.status != StoreStatus.active:
        raise AppError("store_not_found", "Loja não encontrada", status_code=404)
    return store
