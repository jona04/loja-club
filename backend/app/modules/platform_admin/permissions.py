"""Canonical platform permission catalog and role -> permission map.

Single source of truth for the global ``platform.*`` permissions. The map is
kept **in code only** — there is no ``platform_permissions`` table — so
``require_platform_permission`` resolves the user's global roles from
``platform_admin_roles`` and checks this map. The map is **positive**: a role
grants only the permissions listed for it.
"""

# Full catalog of platform permissions (the owner holds all of them).
PLATFORM_PERMISSIONS: list[str] = [
    "platform.stores.view",
    "platform.stores.block",
    "platform.stores.unblock",
    "platform.users.view",
    "platform.plans.view",
    "platform.plans.update",
    "platform.webhooks.view",
    "platform.audit.view",
    "platform.support.impersonate",
    "platform.3d_models.view",
    "platform.3d_models.manage",
    "platform.templates.view",
    "platform.templates.manage",
]

# Positive role -> permission map. Owner holds the full catalog.
PLATFORM_ROLE_PERMISSIONS: dict[str, set[str]] = {
    "platform_owner": set(PLATFORM_PERMISSIONS),
    "platform_ops": {
        "platform.stores.view",
        "platform.stores.block",
        "platform.stores.unblock",
        "platform.users.view",
        "platform.plans.view",
        "platform.webhooks.view",
        "platform.audit.view",
        "platform.support.impersonate",
        "platform.3d_models.view",
    },
    "platform_finance": {
        "platform.stores.view",
        "platform.plans.view",
        "platform.plans.update",
        "platform.audit.view",
    },
    "platform_support": {
        "platform.stores.view",
        "platform.users.view",
        "platform.webhooks.view",
        "platform.audit.view",
        "platform.support.impersonate",
        "platform.3d_models.view",
    },
    "platform_catalog": {
        "platform.3d_models.view",
        "platform.3d_models.manage",
        "platform.templates.view",
        "platform.templates.manage",
    },
}


def platform_role_permissions(role_key: str) -> set[str]:
    """Return the set of permission keys granted to a platform role.

    Args:
        role_key: The platform role key (e.g. ``platform_owner``).

    Returns:
        The granted permission keys, or an empty set for an unknown role.
    """
    return PLATFORM_ROLE_PERMISSIONS.get(role_key, set())
