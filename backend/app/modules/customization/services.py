"""Service layer for the platform 3D catalog."""

from sqlmodel import Session

from app.modules.customization import repositories
from app.modules.customization.schemas import (
    Platform3DModelPublic,
    Platform3DModelVersionPublic,
)


def list_catalog(*, session: Session) -> list[Platform3DModelPublic]:
    """Return the active catalog models, each with its active version.

    Args:
        session: Active database session.

    Returns:
        The active catalog models as public DTOs.
    """
    result: list[Platform3DModelPublic] = []
    for model in repositories.list_active_models(session=session):
        version = repositories.get_active_version(session=session, model_id=model.id)
        active_version = (
            Platform3DModelVersionPublic(
                id=version.id,
                version=version.version,
                glb_url=version.glb_url,
                printable_areas=version.printable_areas,
                text_config=version.text_config,
                art_limits=version.art_limits,
            )
            if version is not None
            else None
        )
        result.append(
            Platform3DModelPublic(
                id=model.id,
                name=model.name,
                category=model.category,
                slug=model.slug,
                active_version=active_version,
            )
        )
    return result
