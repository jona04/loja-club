"""Integration-test fixtures: per-test DB isolation and an HTTP test client.

Integration tests run against a real PostgreSQL (the Loja Club dev database).
Each test runs inside a transaction that is rolled back on teardown, so tests are
isolated and order-independent (see ``docs/backlog/_foundations-and-bottlenecks.md``,
DEC-10). Unit tests live in ``tests/unit`` and must not depend on these fixtures.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Transaction
from sqlmodel import Session, SQLModel

from app import models_registry  # noqa: F401  registers all models on the metadata
from app.api.deps import get_db
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def _create_tables() -> Generator[None, None, None]:
    """Create all tables once for the whole integration-test session.

    The test database is disposable, so tables are created directly from the
    SQLModel metadata instead of running Alembic migrations.

    Yields:
        None. The tables are left in place for the entire session.
    """
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Yield a session wrapped in a transaction that is rolled back per test.

    Uses the SQLAlchemy "join an external transaction" pattern: a SAVEPOINT is
    restarted whenever application code commits, so the outer transaction can
    still be rolled back at teardown, keeping every test isolated. The session is
    pre-seeded with the first superuser.

    Yields:
        The transactional :class:`~sqlmodel.Session`.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(_session: Session, _trans: Transaction) -> None:
        """Restart the SAVEPOINT after application code commits."""
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    init_db(session)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """Yield a TestClient whose ``get_db`` dependency uses the test transaction.

    Args:
        db: The per-test transactional session to bind to the app.

    Yields:
        A :class:`~fastapi.testclient.TestClient` bound to the app with the
        database dependency overridden.
    """

    def _get_db_override() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Return Authorization headers for the first superuser.

    Args:
        client: The test HTTP client.

    Returns:
        A mapping with the ``Authorization`` bearer header for the superuser.
    """
    return get_superuser_token_headers(client)


@pytest.fixture
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Return Authorization headers for a normal (non-superuser) test user.

    Args:
        client: The test HTTP client.
        db: The per-test transactional session.

    Returns:
        A mapping with the ``Authorization`` bearer header for the test user.
    """
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
