"""Data access and seed for the platform 3D catalog."""

import uuid

from sqlmodel import Session, col, select

from app.modules.customization.models import (
    CustomizationProductSettings,
    Platform3DModel,
    Platform3DModelVersion,
)
from app.modules.customization.storage import model_glb_url

MUG_SLUG = "ceramic-mug"

# Initial front printable area for the mug, as a region of the model's UV space
# (0..1). The GLB carries a clean cylindrical UV channel (added in pre-processing
# via `--cylindrical-uv`), so the art follows the real surface; a UV rectangle
# maps to a continuous band. Calibrated visually in the admin; this is just the
# starting value (a front band that avoids the back seam).
_MUG_FRONT_AREA: dict[str, object] = {
    "id": "front",
    "label": "Frente",
    "uv_rect": {"u0": 0.2, "v0": 0.3, "u1": 0.8, "v1": 0.7},
    "max_layers": 5,
}


def list_active_models(*, session: Session) -> list[Platform3DModel]:
    """List active, non-deleted catalog models, oldest first.

    Args:
        session: Active database session.

    Returns:
        The active catalog models.
    """
    return list(
        session.exec(
            select(Platform3DModel)
            .where(
                col(Platform3DModel.is_active).is_(True),
                col(Platform3DModel.deleted_at).is_(None),
            )
            .order_by(col(Platform3DModel.created_at))
        ).all()
    )


def list_all_models(*, session: Session) -> list[Platform3DModel]:
    """List all non-deleted catalog models (active and inactive), oldest first.

    Args:
        session: Active database session.

    Returns:
        Every non-deleted catalog model (for admin governance).
    """
    return list(
        session.exec(
            select(Platform3DModel)
            .where(col(Platform3DModel.deleted_at).is_(None))
            .order_by(col(Platform3DModel.created_at))
        ).all()
    )


def get_model(*, session: Session, model_id: uuid.UUID) -> Platform3DModel | None:
    """Return a non-deleted catalog model by id.

    Args:
        session: Active database session.
        model_id: The catalog model's id.

    Returns:
        The model, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(Platform3DModel).where(
            Platform3DModel.id == model_id,
            col(Platform3DModel.deleted_at).is_(None),
        )
    ).first()


def get_version(
    *, session: Session, version_id: uuid.UUID
) -> Platform3DModelVersion | None:
    """Return a non-deleted model version by id.

    Args:
        session: Active database session.
        version_id: The version's id.

    Returns:
        The version, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(Platform3DModelVersion).where(
            Platform3DModelVersion.id == version_id,
            col(Platform3DModelVersion.deleted_at).is_(None),
        )
    ).first()


def get_active_version(
    *, session: Session, model_id: uuid.UUID
) -> Platform3DModelVersion | None:
    """Return the highest active, non-deleted version of a model.

    Args:
        session: Active database session.
        model_id: The catalog model's id.

    Returns:
        The active version, or ``None`` if the model has none.
    """
    return session.exec(
        select(Platform3DModelVersion)
        .where(
            Platform3DModelVersion.model_id == model_id,
            col(Platform3DModelVersion.is_active).is_(True),
            col(Platform3DModelVersion.deleted_at).is_(None),
        )
        .order_by(col(Platform3DModelVersion.version).desc())
    ).first()


def get_product_settings(
    *, session: Session, store_id: uuid.UUID, product_id: uuid.UUID
) -> CustomizationProductSettings | None:
    """Return a product's active (non-deleted) 3D-model link, if any.

    Args:
        session: Active database session.
        store_id: The active store id.
        product_id: The product whose link to fetch.

    Returns:
        The settings row, or ``None`` if the product has no active link.
    """
    return session.exec(
        select(CustomizationProductSettings).where(
            CustomizationProductSettings.store_id == store_id,
            CustomizationProductSettings.product_id == product_id,
            col(CustomizationProductSettings.deleted_at).is_(None),
        )
    ).first()


def seed_platform_3d_models(*, session: Session) -> None:
    """Seed the initial catalog models (idempotent).

    Args:
        session: Active database session used to query and seed.
    """
    existing = session.exec(
        select(Platform3DModel).where(
            Platform3DModel.slug == MUG_SLUG,
            col(Platform3DModel.deleted_at).is_(None),
        )
    ).first()
    if existing is not None:
        return

    model = Platform3DModel(
        name="Caneca de cerâmica",
        category="caneca",
        slug=MUG_SLUG,
        is_active=True,
    )
    session.add(model)
    session.flush()
    session.add(
        Platform3DModelVersion(
            model_id=model.id,
            version=1,
            glb_url=model_glb_url(MUG_SLUG, 1),
            printable_areas=[_MUG_FRONT_AREA],
            text_config={
                "fonts": ["inter", "roboto", "montserrat"],
                "min_size": 8,
                "max_size": 96,
            },
            art_limits={
                "mimes": ["image/png", "image/jpeg"],
                "max_bytes": 15 * 1024 * 1024,
                "min_dimension": 300,
            },
            is_active=True,
        )
    )
    session.commit()
