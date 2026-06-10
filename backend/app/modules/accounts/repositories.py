"""Data access for account users."""

import uuid

from sqlmodel import Session, col, select

from app.core.security import get_password_hash
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create and persist an account user.

    Args:
        session: Active database session.
        user_create: Email, password and profile data.

    Returns:
        The created User.
    """
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update an account user, re-hashing the password when provided.

    Args:
        session: Active database session.
        db_user: The user to update.
        user_in: Fields to change (unset fields are ignored).

    Returns:
        The updated User.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data: dict[str, str] = {}
    if "password" in user_data:
        extra_data["hashed_password"] = get_password_hash(user_data["password"])
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Return the account user with the given email, or None.

    Args:
        session: Active database session.
        email: Email to look up.

    Returns:
        The matching User, or None.
    """
    return session.exec(
        select(User).where(User.email == email, col(User.deleted_at).is_(None))
    ).first()


def get_active_user(*, session: Session, user_id: uuid.UUID) -> User | None:
    """Return a non-soft-deleted account user by id, or None.

    Args:
        session: Active database session.
        user_id: The user id to look up.

    Returns:
        The user if it exists and is not soft-deleted, otherwise None.
    """
    user = session.get(User, user_id)
    if user is None or user.deleted_at is not None:
        return None
    return user
