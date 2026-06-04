"""Integration test: the base mixins produce the expected table columns."""

from sqlalchemy import MetaData
from sqlmodel import Field

from app.db.base import (
    SoftDeleteMixin,
    StoreScopedMixin,
    TimestampMixin,
    UUIDMixin,
)


class _MixinProbe(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    StoreScopedMixin,
    table=True,
):
    """Throwaway model combining all base mixins to inspect the columns.

    It lives on its own ``MetaData`` so it never registers on
    ``SQLModel.metadata`` — otherwise ``create_all``/alembic autogenerate would
    pick the probe table up.
    """

    metadata = MetaData()

    name: str = Field()


def test_mixins_generate_expected_columns() -> None:
    """A model using all base mixins exposes the expected columns."""
    columns = set(_MixinProbe.__table__.columns.keys())
    assert {
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "deleted_by_user_id",
        "delete_reason",
        "store_id",
        "name",
    } <= columns
