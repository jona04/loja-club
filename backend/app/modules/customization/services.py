"""Service layer for the platform 3D catalog."""

import uuid

from sqlmodel import Session

from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.catalog.enums import ProductType
from app.modules.catalog.services import get_product
from app.modules.customization import repositories
from app.modules.customization.models import (
    CustomizationProductSettings,
    Platform3DModel,
    Platform3DModelVersion,
)
from app.modules.customization.schemas import (
    Platform3DModelAdmin,
    Platform3DModelPublic,
    Platform3DModelUpdate,
    Platform3DModelVersionAdmin,
    Platform3DModelVersionPublic,
    Platform3DModelVersionUpdate,
    ProductModelLink,
    ProductModelSettingsPublic,
)

# A product linked to a 3D model must be one of the 3D types; ``image`` means
# "no 3D model", so it cannot carry a link.
_LINKABLE_TYPES = {ProductType.image_3d, ProductType.image_3d_customizable}


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


def _to_settings_public(
    *,
    settings: CustomizationProductSettings,
    model: Platform3DModel,
    product_type: ProductType,
) -> ProductModelSettingsPublic:
    """Map a settings row + its catalog model to the panel DTO.

    Args:
        settings: The persisted product-model link.
        model: The linked catalog model (for display fields).
        product_type: The product's current type.

    Returns:
        The panel DTO describing the product's 3D-model link.
    """
    return ProductModelSettingsPublic(
        product_id=settings.product_id,
        type=product_type,
        platform_3d_model_id=settings.platform_3d_model_id,
        model_name=model.name,
        model_slug=model.slug,
        model_category=model.category,
        production_notes=settings.production_notes,
    )


def get_product_model(
    *, session: Session, store_id: uuid.UUID, product_id: uuid.UUID
) -> ProductModelSettingsPublic | None:
    """Return a product's current 3D-model link, or ``None`` if unlinked.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product whose link to read.

    Returns:
        The link DTO, or ``None`` if the product has no active link.

    Raises:
        AppError: 404 if the product does not exist in the store.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    settings = repositories.get_product_settings(
        session=session, store_id=store_id, product_id=product_id
    )
    if settings is None:
        return None
    model = repositories.get_model(
        session=session, model_id=settings.platform_3d_model_id
    )
    if model is None:  # pragma: no cover — FK guarantees the model exists
        return None
    return _to_settings_public(
        settings=settings, model=model, product_type=product.type
    )


def link_product_model(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: ProductModelLink,
) -> ProductModelSettingsPublic:
    """Link a product to an active catalog model and set its 3D ``type``.

    Idempotent per product: re-linking updates the chosen model/notes (one
    active settings row per product). Only an **active** catalog model with an
    active version can be linked.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product to link.
        payload: The chosen model, the product ``type`` and production notes.

    Returns:
        The resulting link DTO.

    Raises:
        AppError: 404 if the product is missing; 422 if ``type`` is not a 3D
            type, or the model is missing/disabled/has no active version.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    if payload.type not in _LINKABLE_TYPES:
        raise AppError(
            "invalid_product_type",
            "A linked product must be 'image_3d' or 'image_3d_customizable'.",
            status_code=422,
        )
    model = repositories.get_model(
        session=session, model_id=payload.platform_3d_model_id
    )
    if model is None or not model.is_active:
        raise AppError(
            "model_not_linkable",
            "The chosen 3D model is unavailable.",
            status_code=422,
        )
    if repositories.get_active_version(session=session, model_id=model.id) is None:
        raise AppError(
            "model_not_linkable",
            "The chosen 3D model has no active version.",
            status_code=422,
        )

    settings = repositories.get_product_settings(
        session=session, store_id=store_id, product_id=product_id
    )
    if settings is None:
        settings = CustomizationProductSettings(
            store_id=store_id,
            product_id=product_id,
            platform_3d_model_id=model.id,
            production_notes=payload.production_notes,
        )
    else:
        settings.platform_3d_model_id = model.id
        settings.production_notes = payload.production_notes
    product.type = payload.type
    session.add(settings)
    session.add(product)
    session.commit()
    session.refresh(settings)
    return _to_settings_public(
        settings=settings, model=model, product_type=product.type
    )


def unlink_product_model(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    unlinked_by: uuid.UUID,
) -> None:
    """Unlink a product's 3D model: soft-delete the link, revert ``type``.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product to unlink.
        unlinked_by: The acting member's user id (recorded on the soft delete).

    Raises:
        AppError: 404 if the product is missing, or 404 if it has no active link.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    settings = repositories.get_product_settings(
        session=session, store_id=store_id, product_id=product_id
    )
    if settings is None:
        raise AppError(
            "product_model_not_linked",
            "This product has no 3D model linked.",
            status_code=404,
        )
    settings.deleted_at = get_datetime_utc()
    settings.deleted_by_user_id = unlinked_by
    product.type = ProductType.image
    session.add(settings)
    session.add(product)
    session.commit()
