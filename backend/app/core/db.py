"""Database engine and initial-data seeding (first superuser)."""

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.modules.accounts import repositories
from app.modules.accounts.models import User
from app.modules.accounts.schemas import UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (see app.models_registry) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """Seed the database with the first superuser if it does not exist.

    Tables themselves are managed by Alembic migrations; this only ensures the
    bootstrap superuser from settings is present.

    Args:
        session: Active database session used to query and create the user.
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
