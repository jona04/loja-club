"""Database engine and initial-data seeding (first superuser)."""

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.modules.accounts import repositories
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate
from app.modules.content.repositories import seed_content_templates
from app.modules.platform_admin.enums import PlatformRole
from app.modules.platform_admin.repositories import assign_platform_role
from app.modules.stores.repositories import seed_store_permissions, seed_store_roles

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (see app.models_registry) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """Seed bootstrap data: superuser, store roles/permissions, theme templates.

    Tables themselves are managed by Alembic migrations; this ensures the
    bootstrap superuser (from settings), the store roles, the permission
    catalog/map and the global theme templates exist. All idempotent. Runs on
    prestart and is also used by the test fixtures (whose schema comes from
    ``create_all``, not migrations).

    Args:
        session: Active database session used to query and seed.
    """
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = repositories.create_user(session=session, user_create=user_in)

    # The bootstrap superuser is the platform owner (doc 08); is_superuser is no
    # longer used for authorization (replaced by platform_admin_roles).
    assign_platform_role(
        session=session, user_id=user.id, role=PlatformRole.platform_owner.value
    )

    seed_store_roles(session=session)
    seed_store_permissions(session=session)
    seed_content_templates(session=session)


def dispose_engine() -> None:
    """Dispose the engine's connection pool (on app shutdown, INV-F6)."""
    engine.dispose()
