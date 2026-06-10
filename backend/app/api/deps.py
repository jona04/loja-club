"""Shared FastAPI dependencies: database session and authenticated user."""

from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload
from app.modules.accounts.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for the duration of a request.

    Yields:
        A SQLModel session bound to the application engine, closed when the
        request finishes.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Resolve the authenticated user from a bearer access token.

    Args:
        session: Active database session.
        token: The raw JWT access token from the ``Authorization`` header.

    Returns:
        The active user matching the token's subject.

    Raises:
        HTTPException: 403 if the token is invalid, 404 if the user no longer
            exists, or 400 if the user is inactive.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(
    current_user: CurrentUser, session: SessionDep
) -> User:
    """Authorize the current user as a platform owner (the platform superuser).

    Backed by the global ``platform_owner`` role (doc 08); the legacy
    ``is_superuser`` flag is no longer consulted for authorization.

    Args:
        current_user: The user resolved from the access token.
        session: Active database session.

    Returns:
        The same user when it holds the ``platform_owner`` role.

    Raises:
        HTTPException: 403 if the user is not a platform owner.
    """
    from app.modules.platform_admin.enums import PlatformRole
    from app.modules.platform_admin.repositories import user_platform_roles

    if PlatformRole.platform_owner.value not in user_platform_roles(
        session=session, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
