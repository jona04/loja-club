"""Data access and seed for the platform 3D catalog."""

import uuid

from sqlmodel import Session, col, select

from app.modules.customization.models import (
    Platform3DModel,
    Platform3DModelVersion,
)
from app.modules.customization.storage import model_glb_url

MUG_SLUG = "ceramic-mug"

# Initial front printable area for the mug. Coordinates are calibrated visually
# in the admin; the seed only provides a starting value.
_MUG_FRONT_AREA: dict[str, object] = {
    "id": "front",
    "label": "Frente",
    "target_mesh": None,
    "projector": {
        "position": [0.0, 0.05, 0.041],
        "normal": [0.0, 0.0, 1.0],
        "up": [0.0, 1.0, 0.0],
        "size_m": [0.18, 0.085],
    },
    "size_cm": [18.0, 8.5],
    "aspect_ratio": 2.1,
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
