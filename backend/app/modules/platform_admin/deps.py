"""Platform-admin dependencies: global ``platform.*`` permission enforcement."""

from collections.abc import Callable

from app.api.deps import CurrentUser, SessionDep
from app.core.api import AppError
from app.modules.accounts.models import User
from app.modules.platform_admin.repositories import user_platform_permissions


def require_platform_permission(permission: str) -> Callable[..., User]:
    """Build a dependency that authorizes a global ``platform.*`` permission.

    The platform parallel of ``require_permission`` (doc 08), without a store
    scope: it resolves the user's global roles from ``platform_admin_roles`` and
    checks the in-code role->permission map. Authorization is enforced in the
    backend regardless of what the frontend shows (INV-A4/S1).

    Args:
        permission: Required ``platform.*`` permission key (e.g.
            ``platform.stores.block``).

    Returns:
        A FastAPI dependency that returns the authorized user.
    """

    def _require(current_user: CurrentUser, session: SessionDep) -> User:
        granted = user_platform_permissions(session=session, user_id=current_user.id)
        if permission not in granted:
            raise AppError("forbidden", "Missing platform permission", status_code=403)
        return current_user

    return _require
