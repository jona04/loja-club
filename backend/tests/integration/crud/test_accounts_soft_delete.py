"""Soft-delete behavior for account_users (P1-ACCT-01)."""

from sqlmodel import Session

from app.db.base import get_datetime_utc
from app.modules.accounts import repositories, services
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def _make_user(db: Session) -> tuple[User, str, str]:
    email = random_email()
    password = random_lower_string()
    user = repositories.create_user(
        session=db, user_create=UserCreate(email=email, password=password)
    )
    return user, email, password


def test_get_user_by_email_excludes_soft_deleted(db: Session) -> None:
    user, email, _ = _make_user(db)
    user.deleted_at = get_datetime_utc()
    db.add(user)
    db.commit()
    assert repositories.get_user_by_email(session=db, email=email) is None


def test_authenticate_excludes_soft_deleted(db: Session) -> None:
    user, email, password = _make_user(db)
    user.deleted_at = get_datetime_utc()
    db.add(user)
    db.commit()
    assert services.authenticate(session=db, email=email, password=password) is None


def test_update_user_bumps_updated_at(db: Session) -> None:
    user, _, _ = _make_user(db)
    created = user.created_at
    repositories.update_user(
        session=db, db_user=user, user_in=UserUpdate(full_name="Updated")
    )
    assert user.updated_at is not None
    assert user.updated_at >= created
