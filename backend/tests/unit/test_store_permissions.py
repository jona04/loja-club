"""Unit tests for the store permission catalog and role map (doc 08)."""

from app.modules.stores.permissions import (
    PERMISSIONS,
    ROLE_PERMISSIONS,
    role_permissions,
)

# Permission counts per role, taken directly from doc 08 (guards transcription).
_EXPECTED_ROLE_COUNTS = {
    "owner": 63,
    "admin": 54,
    "manager": 28,
    "support": 10,
    "catalog": 15,
    "marketing": 14,
}


def test_catalog_has_no_duplicates() -> None:
    assert len(PERMISSIONS) == len(set(PERMISSIONS)) == 63


def test_owner_holds_full_catalog() -> None:
    assert ROLE_PERMISSIONS["owner"] == set(PERMISSIONS)


def test_every_permission_in_at_least_one_role() -> None:
    granted = set().union(*ROLE_PERMISSIONS.values())
    assert set(PERMISSIONS) <= granted


def test_no_role_grants_unknown_permission() -> None:
    catalog = set(PERMISSIONS)
    for role, perms in ROLE_PERMISSIONS.items():
        assert perms <= catalog, f"{role} grants permission(s) outside the catalog"


def test_role_permission_counts_match_doc() -> None:
    for role, count in _EXPECTED_ROLE_COUNTS.items():
        assert len(ROLE_PERMISSIONS[role]) == count


def test_role_permissions_helper() -> None:
    assert role_permissions("support") == ROLE_PERMISSIONS["support"]
    assert role_permissions("does-not-exist") == set()


def test_role_distinctions_from_doc() -> None:
    assert "layout.update" not in ROLE_PERMISSIONS["support"]
    assert "orders.refund" in ROLE_PERMISSIONS["owner"]
    assert "orders.refund" not in ROLE_PERMISSIONS["admin"]
    assert "catalog.product.create" not in ROLE_PERMISSIONS["marketing"]
    assert "catalog.product_customization.update" in ROLE_PERMISSIONS["catalog"]
    assert "billing.update_plan" not in ROLE_PERMISSIONS["admin"]
