"""Sample integration tests proving per-test DB isolation (transaction rollback)."""

from sqlmodel import Session, func, select

from app.models import User
from tests.utils.user import create_random_user


def _user_count(db: Session) -> int:
    """Return the number of rows in the users table.

    Args:
        db: The database session.

    Returns:
        The total number of users.
    """
    return db.exec(select(func.count()).select_from(User)).one()


def test_isolation_first(db: Session) -> None:
    """Create a user, having confirmed only the seeded superuser existed before.

    Args:
        db: The per-test transactional session.
    """
    assert _user_count(db) == 1  # only the seeded superuser
    create_random_user(db)
    assert _user_count(db) == 2


def test_isolation_second(db: Session) -> None:
    """Confirm the user created by the previous test did not leak into this one.

    Args:
        db: The per-test transactional session.
    """
    assert _user_count(db) == 1  # previous test's user was rolled back
    create_random_user(db)
    assert _user_count(db) == 2
