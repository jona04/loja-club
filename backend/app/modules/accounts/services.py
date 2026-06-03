"""Authentication logic for account users."""

from sqlmodel import Session

from app.core.security import verify_password
from app.modules.accounts.models import User
from app.modules.accounts.repositories import get_user_by_email

# Argon2 hash of a random password, used for a constant-time comparison when the
# user is not found, to keep response time similar and avoid email enumeration.
_DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate an account user by email and password.

    Args:
        session: Active database session.
        email: The user's email.
        password: The plaintext password to verify.

    Returns:
        The authenticated User, or None if credentials are invalid.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        verify_password(password, _DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user
