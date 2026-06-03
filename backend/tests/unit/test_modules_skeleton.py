"""Smoke tests for the module skeleton and the central model registry."""

import importlib

from sqlmodel import SQLModel


def test_module_packages_importable() -> None:
    """A few domain module packages import without error."""
    for name in ("accounts", "stores", "catalog", "orders"):
        importlib.import_module(f"app.modules.{name}")


def test_registry_populates_metadata() -> None:
    """Importing the registry registers the known tables on the metadata."""
    import app.models_registry  # noqa: F401

    assert "account_users" in SQLModel.metadata.tables
