"""Data access for platform-admin roles and permission resolution."""

import uuid

from sqlmodel import Session, select

from app.modules.platform_admin.models import PlatformAdminRole
from app.modules.platform_admin.permissions import platform_role_permissions


def user_platform_roles(*, session: Session, user_id: uuid.UUID) -> list[str]:
    """Return the global platform roles assigned to a user.

    Args:
        session: Active database session.
        user_id: The account-user id.

    Returns:
        The role keys assigned to the user (possibly empty).
    """
    return list(
        session.exec(
            select(PlatformAdminRole.role).where(PlatformAdminRole.user_id == user_id)
        ).all()
    )


def user_platform_permissions(*, session: Session, user_id: uuid.UUID) -> set[str]:
    """Return the union of platform permissions granted to a user's roles.

    Args:
        session: Active database session.
        user_id: The account-user id.

    Returns:
        The granted ``platform.*`` permission keys (empty if the user has no
        platform role).
    """
    perms: set[str] = set()
    for role in user_platform_roles(session=session, user_id=user_id):
        perms |= platform_role_permissions(role)
    return perms


def assign_platform_role(
    *, session: Session, user_id: uuid.UUID, role: str
) -> PlatformAdminRole:
    """Grant a platform role to a user (idempotent; commits).

    Args:
        session: Active database session.
        user_id: The account-user id.
        role: The platform role key to grant.

    Returns:
        The existing or newly created role assignment.
    """
    existing = session.exec(
        select(PlatformAdminRole).where(
            PlatformAdminRole.user_id == user_id,
            PlatformAdminRole.role == role,
        )
    ).first()
    if existing is not None:
        return existing
    assignment = PlatformAdminRole(user_id=user_id, role=role)
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment
