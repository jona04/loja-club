"""Data access and seed for the platform 3D catalog."""

import uuid
from datetime import datetime

from sqlmodel import Session, col, func, select

from app.modules.customization.enums import CustomizationSessionStatus
from app.modules.customization.models import (
    CustomizationCartItem,
    CustomizationOrderItem,
    CustomizationProductSettings,
    CustomizationSession,
    CustomizationUpload,
    Platform3DModel,
    Platform3DModelVersion,
)
from app.modules.customization.storage import model_glb_url

# Statuses that age out: still-open sessions that were never carried/ordered.
_EXPIRABLE_STATUSES = (
    CustomizationSessionStatus.draft,
    CustomizationSessionStatus.approved,
)

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


def get_session(
    *, session: Session, store_id: uuid.UUID, session_id: uuid.UUID
) -> CustomizationSession | None:
    """Return a store's customization session by id (non-deleted).

    Args:
        session: Active database session.
        store_id: The owning store id.
        session_id: The customization session id.

    Returns:
        The session, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(CustomizationSession).where(
            CustomizationSession.id == session_id,
            CustomizationSession.store_id == store_id,
            col(CustomizationSession.deleted_at).is_(None),
        )
    ).first()


def list_store_sessions(
    *,
    session: Session,
    store_id: uuid.UUID,
    status: CustomizationSessionStatus | None,
    skip: int,
    limit: int,
) -> tuple[list[CustomizationSession], int]:
    """List a store's customization sessions (most recently updated first).

    For the merchant panel's near-real-time view (doc 22): every non-deleted
    session of the store, optionally filtered by status.

    Args:
        session: Active database session.
        store_id: The owning store id.
        status: Optional status filter.
        skip: Offset.
        limit: Page size.

    Returns:
        A ``(sessions, total)`` tuple.
    """
    count_stmt = (
        select(func.count())
        .select_from(CustomizationSession)
        .where(
            CustomizationSession.store_id == store_id,
            col(CustomizationSession.deleted_at).is_(None),
        )
    )
    list_stmt = select(CustomizationSession).where(
        CustomizationSession.store_id == store_id,
        col(CustomizationSession.deleted_at).is_(None),
    )
    if status is not None:
        count_stmt = count_stmt.where(CustomizationSession.status == status)
        list_stmt = list_stmt.where(CustomizationSession.status == status)
    total = session.exec(count_stmt).one()
    rows = list(
        session.exec(
            list_stmt.order_by(col(CustomizationSession.updated_at).desc())
            .offset(skip)
            .limit(limit)
        ).all()
    )
    return rows, total


def list_order_items_by_sessions(
    *, session: Session, store_id: uuid.UUID, session_ids: list[uuid.UUID]
) -> list[CustomizationOrderItem]:
    """Return the store's frozen order items for the given session ids.

    Args:
        session: Active database session.
        store_id: The owning store id.
        session_ids: The customization session ids to look up.

    Returns:
        The matching (non-deleted) order items.
    """
    if not session_ids:
        return []
    return list(
        session.exec(
            select(CustomizationOrderItem).where(
                CustomizationOrderItem.store_id == store_id,
                col(CustomizationOrderItem.customization_session_id).in_(session_ids),
                col(CustomizationOrderItem.deleted_at).is_(None),
            )
        ).all()
    )


def get_order_item_by_session(
    *, session: Session, store_id: uuid.UUID, session_id: uuid.UUID
) -> CustomizationOrderItem | None:
    """Return the frozen order item for a session, if it was ordered.

    Args:
        session: Active database session.
        store_id: The owning store id.
        session_id: The customization session id.

    Returns:
        The order item, or ``None`` if the session is not in an order.
    """
    return session.exec(
        select(CustomizationOrderItem).where(
            CustomizationOrderItem.store_id == store_id,
            CustomizationOrderItem.customization_session_id == session_id,
            col(CustomizationOrderItem.deleted_at).is_(None),
        )
    ).first()


def get_guest_draft(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    guest_session_id: str,
) -> CustomizationSession | None:
    """Return a guest's open draft session for a product, if any.

    Args:
        session: Active database session.
        store_id: The owning store id.
        product_id: The product being customized.
        guest_session_id: The guest browser's session id.

    Returns:
        The most recent open draft, or ``None``.
    """
    return session.exec(
        select(CustomizationSession)
        .where(
            CustomizationSession.store_id == store_id,
            CustomizationSession.product_id == product_id,
            CustomizationSession.guest_session_id == guest_session_id,
            CustomizationSession.status == CustomizationSessionStatus.draft,
            col(CustomizationSession.deleted_at).is_(None),
        )
        .order_by(col(CustomizationSession.created_at).desc())
    ).first()


def get_session_by_token(
    *, session: Session, public_token: str
) -> CustomizationSession | None:
    """Return a session by its public token (global lookup, non-deleted).

    Not store-scoped: the unguessable token is the credential. Expiry is checked
    by the caller.

    Args:
        session: Active database session.
        public_token: The session's public token.

    Returns:
        The session, or ``None`` if missing/deleted.
    """
    return session.exec(
        select(CustomizationSession).where(
            CustomizationSession.public_token == public_token,
            col(CustomizationSession.deleted_at).is_(None),
        )
    ).first()


def list_session_uploads(
    *, session: Session, session_id: uuid.UUID
) -> list[CustomizationUpload]:
    """Return a session's non-deleted uploads, oldest first.

    Args:
        session: Active database session.
        session_id: The customization session id.

    Returns:
        The session's uploads.
    """
    return list(
        session.exec(
            select(CustomizationUpload)
            .where(
                CustomizationUpload.customization_session_id == session_id,
                col(CustomizationUpload.deleted_at).is_(None),
            )
            .order_by(col(CustomizationUpload.created_at))
        ).all()
    )


def get_cart_item_link(
    *, session: Session, store_id: uuid.UUID, cart_item_id: uuid.UUID
) -> CustomizationCartItem | None:
    """Return the active customization link for a cart line, if any.

    Args:
        session: Active database session.
        store_id: The owning store id.
        cart_item_id: The cart line id.

    Returns:
        The link row, or ``None`` if the line has no customization.
    """
    return session.exec(
        select(CustomizationCartItem).where(
            CustomizationCartItem.store_id == store_id,
            CustomizationCartItem.cart_item_id == cart_item_id,
            col(CustomizationCartItem.deleted_at).is_(None),
        )
    ).first()


def list_expirable_sessions(
    *, session: Session, now: datetime
) -> list[CustomizationSession]:
    """Return open sessions whose ``expires_at`` has passed (to be swept).

    Args:
        session: Active database session.
        now: The current time.

    Returns:
        Non-deleted sessions in an expirable status past their expiry.
    """
    return list(
        session.exec(
            select(CustomizationSession).where(
                col(CustomizationSession.status).in_(_EXPIRABLE_STATUSES),
                CustomizationSession.expires_at < now,
                col(CustomizationSession.deleted_at).is_(None),
            )
        ).all()
    )


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
                "max_bytes": 30 * 1024 * 1024,
                "min_dimension": 300,
            },
            is_active=True,
        )
    )
    session.commit()
