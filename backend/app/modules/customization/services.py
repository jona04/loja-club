"""Service layer for the platform 3D catalog."""

import uuid

from sqlmodel import Session

from app.core.api import AppError
from app.modules.customization import repositories
from app.modules.customization.models import Platform3DModelVersion
from app.modules.customization.schemas import (
    Platform3DModelAdmin,
    Platform3DModelPublic,
    Platform3DModelUpdate,
    Platform3DModelVersionAdmin,
    Platform3DModelVersionPublic,
    Platform3DModelVersionUpdate,
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


def _to_version_admin(
    version: Platform3DModelVersion,
) -> Platform3DModelVersionAdmin:
    """Map a version model to its admin DTO.

    Args:
        version: The persisted version.

    Returns:
        The admin DTO mirroring the version.
    """
    return Platform3DModelVersionAdmin(
        id=version.id,
        version=version.version,
        glb_url=version.glb_url,
        printable_areas=version.printable_areas,
        text_config=version.text_config,
        art_limits=version.art_limits,
        is_active=version.is_active,
    )


def list_models_admin(*, session: Session) -> list[Platform3DModelAdmin]:
    """List every catalog model (active and inactive) for the admin.

    Args:
        session: Active database session.

    Returns:
        The catalog models, each with its active version (if any).
    """
    result: list[Platform3DModelAdmin] = []
    for model in repositories.list_all_models(session=session):
        version = repositories.get_active_version(session=session, model_id=model.id)
        result.append(
            Platform3DModelAdmin(
                id=model.id,
                name=model.name,
                category=model.category,
                slug=model.slug,
                is_active=model.is_active,
                active_version=(
                    _to_version_admin(version) if version is not None else None
                ),
            )
        )
    return result


def update_model(
    *, session: Session, model_id: uuid.UUID, payload: Platform3DModelUpdate
) -> Platform3DModelAdmin:
    """Update a catalog model's metadata/visibility (enable/disable).

    Args:
        session: Active database session.
        model_id: The model to update.
        payload: The partial update.

    Returns:
        The updated model as an admin DTO.

    Raises:
        AppError: 404 if the model does not exist.
    """
    model = repositories.get_model(session=session, model_id=model_id)
    if model is None:
        raise AppError("model_not_found", "3D model not found", status_code=404)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(model, field, value)
    session.add(model)
    session.commit()
    session.refresh(model)
    version = repositories.get_active_version(session=session, model_id=model.id)
    return Platform3DModelAdmin(
        id=model.id,
        name=model.name,
        category=model.category,
        slug=model.slug,
        is_active=model.is_active,
        active_version=(_to_version_admin(version) if version is not None else None),
    )


def _validate_printable_areas(areas: list[dict[str, object]]) -> None:
    """Validate the shape of a printable-areas payload.

    Args:
        areas: The printable areas to validate.

    Raises:
        AppError: 422 if any area is missing a non-empty string ``id``.
    """
    for area in areas:
        area_id = area.get("id")
        if not isinstance(area_id, str) or not area_id:
            raise AppError(
                "invalid_printable_area",
                "Each printable area needs a non-empty string 'id'.",
                status_code=422,
            )


def update_version(
    *,
    session: Session,
    version_id: uuid.UUID,
    payload: Platform3DModelVersionUpdate,
) -> Platform3DModelVersionAdmin:
    """Update a version's editor parameters/visibility.

    Editing affects only new sessions; orders that already froze a version keep
    their snapshot and state.

    Args:
        session: Active database session.
        version_id: The version to update.
        payload: The partial update (printable areas, limits, visibility).

    Returns:
        The updated version as an admin DTO.

    Raises:
        AppError: 404 if the version does not exist; 422 if the printable areas
            are malformed.
    """
    version = repositories.get_version(session=session, version_id=version_id)
    if version is None:
        raise AppError(
            "model_version_not_found", "Model version not found", status_code=404
        )
    data = payload.model_dump(exclude_unset=True)
    if "printable_areas" in data:
        _validate_printable_areas(data["printable_areas"])
    for field, value in data.items():
        setattr(version, field, value)
    session.add(version)
    session.commit()
    session.refresh(version)
    return _to_version_admin(version)
