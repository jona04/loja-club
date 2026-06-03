"""Security primitives: JWT access tokens and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Token subject (typically the user id); coerced to ``str``.
        expires_delta: How long from now the token stays valid.

    Returns:
        The encoded JWT as a string.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    """Verify a password against a hash, upgrading the hash if outdated.

    Args:
        plain_password: The clear-text password to check.
        hashed_password: The stored hash to verify against.

    Returns:
        A tuple ``(is_valid, new_hash)`` where ``new_hash`` is a re-hashed
        value when the stored hash uses an outdated scheme, otherwise ``None``.
    """
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a clear-text password using the configured Argon2 scheme.

    Args:
        password: The clear-text password to hash.

    Returns:
        The encoded password hash.
    """
    return password_hash.hash(password)
