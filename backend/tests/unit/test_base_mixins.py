"""Unit tests for the shared base helpers."""

from datetime import timedelta

from app.db.base import get_datetime_utc


def test_get_datetime_utc_is_timezone_aware_utc() -> None:
    """``get_datetime_utc`` returns a tz-aware datetime at UTC offset zero."""
    now = get_datetime_utc()
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)
