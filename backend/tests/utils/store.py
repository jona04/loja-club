"""Reusable multi-tenant factories for integration tests.

These build stores, memberships and per-member auth headers so commercial
features in later phases can assert tenant isolation without re-deriving setup.
"""

from dataclasses import dataclass

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.modules.accounts import repositories as accounts_repo
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate
from app.modules.stores.enums import MembershipStatus, StoreStatus
from app.modules.stores.models import Store, StoreMember, StoreRole, StoreSettings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email, random_lower_string


@dataclass
class TenantContext:
    """Two independent stores with their owners' auth headers."""

    store_a: Store
    store_b: Store
    owner_a_headers: dict[str, str]
    owner_b_headers: dict[str, str]


def create_user(db: Session) -> User:
    """Create a fresh account user with a random email.

    Args:
        db: Active database session.

    Returns:
        The created user.
    """
    return accounts_repo.create_user(
        session=db,
        user_create=UserCreate(email=random_email(), password=random_lower_string()),
    )


def create_store(
    db: Session,
    *,
    slug: str | None = None,
    status: StoreStatus = StoreStatus.active,
) -> Store:
    """Create a store together with its settings row.

    Args:
        db: Active database session.
        slug: Store slug; a random unique one is generated when omitted.
        status: Initial store status.

    Returns:
        The created store.
    """
    store = Store(
        name="Test Store",
        slug=slug or f"s-{random_lower_string()[:12]}",
        status=status,
        country="US",
        currency="USD",
        locale="en-US",
    )
    db.add(store)
    db.flush()
    db.add(StoreSettings(store_id=store.id))
    db.commit()
    db.refresh(store)
    return store


def create_member(
    db: Session,
    *,
    store: Store,
    user: User,
    role_key: str = "owner",
    status: MembershipStatus = MembershipStatus.active,
) -> StoreMember:
    """Add a user to a store with a role.

    Args:
        db: Active database session.
        store: The store to add the member to.
        user: The user to add.
        role_key: The role key (e.g. ``owner``, ``support``).
        status: Membership status.

    Returns:
        The created membership.
    """
    role = db.exec(select(StoreRole).where(StoreRole.key == role_key)).one()
    member = StoreMember(
        store_id=store.id, user_id=user.id, role_id=role.id, status=status
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def member_headers(client: TestClient, db: Session, user: User) -> dict[str, str]:
    """Return Authorization headers authenticating ``user``.

    Args:
        client: The test HTTP client.
        db: Active database session.
        user: The user to authenticate.

    Returns:
        A mapping with the ``Authorization`` bearer header.
    """
    return authentication_token_from_email(client=client, email=user.email, db=db)
