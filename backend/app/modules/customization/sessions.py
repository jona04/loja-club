"""Customization-session lifecycle: start, autosave, upload, approve, assisted.

The backend behind the storefront 3D editor (doc 30 §4/§5/§6/§9). The
``state_json`` is always validated **against the pinned version** here — the
client is never trusted. Customer art and approval snapshots are stored
privately (``private/<store_id>/customizations/...``) and only ever served via
short-lived presigned URLs.
"""

import io
import secrets
import uuid
from datetime import datetime, timedelta

from PIL import Image, UnidentifiedImageError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import storage
from app.core.api import AppError
from app.db.base import get_datetime_utc
from app.modules.catalog.enums import ProductType
from app.modules.catalog.services import get_product
from app.modules.customers.models import CustomerProfile
from app.modules.customers.normalization import normalize_email, normalize_phone
from app.modules.customers.services import create_or_update_customer
from app.modules.customization import repositories
from app.modules.customization.enums import CustomizationSessionStatus
from app.modules.customization.models import (
    CustomizationSession,
    CustomizationUpload,
    Platform3DModelVersion,
)
from app.modules.customization.schemas import (
    AssistedSessionCreate,
    AssistedSessionPublic,
    ContactConfirm,
    Platform3DModelVersionPublic,
    SessionPublic,
    StateJson,
    UploadPublic,
)
from app.modules.customization.storage import customization_upload_key

# Sessions age out 30 days after creation (swept to ``expired`` by the worker).
SESSION_TTL = timedelta(days=30)
SNAPSHOT_MIME = "image/png"
_DEFAULT_MIMES = ("image/png", "image/jpeg")
_DEFAULT_MAX_BYTES = 15 * 1024 * 1024
_DEFAULT_MIN_DIMENSION = 300
_EXT = {"image/png": "png", "image/jpeg": "jpg"}


# --- internal helpers -------------------------------------------------------


def _version_public(version: Platform3DModelVersion) -> Platform3DModelVersionPublic:
    """Map a version model to the public DTO the editor consumes."""
    return Platform3DModelVersionPublic(
        id=version.id,
        version=version.version,
        glb_url=version.glb_url,
        printable_areas=version.printable_areas,
        text_config=version.text_config,
        art_limits=version.art_limits,
    )


def _to_session_public(
    *, obj: CustomizationSession, version: Platform3DModelVersion
) -> SessionPublic:
    """Build a session DTO, presigning the snapshot URL when present."""
    snapshot_url = (
        storage.generate_presigned_url(obj.snapshot_key) if obj.snapshot_key else None
    )
    return SessionPublic(
        id=obj.id,
        product_id=obj.product_id,
        status=obj.status,
        state_json=obj.state_json,
        version=_version_public(version),
        snapshot_url=snapshot_url,
        expires_at=obj.expires_at,
        approved_at=obj.approved_at,
    )


def _initial_state(*, model_id: uuid.UUID, version_id: uuid.UUID) -> dict[str, object]:
    """Return the empty editor state pinned to a model version."""
    return {
        "schema_version": 1,
        "model": {"model_id": str(model_id), "version_id": str(version_id)},
        "layers": [],
    }


def _resolve_customizable_version(
    *, session: Session, store_id: uuid.UUID, product_id: uuid.UUID
) -> Platform3DModelVersion:
    """Resolve the active version of the model linked to a customizable product.

    Args:
        session: Active database session.
        store_id: The owning store id.
        product_id: The product being customized.

    Returns:
        The active catalog version to pin the session to.

    Raises:
        AppError: 404 if the product is missing; 422 if it is not customizable,
            has no linked model, or the model has no active version.
    """
    product = get_product(session=session, store_id=store_id, product_id=product_id)
    if product.type != ProductType.image_3d_customizable:
        raise AppError(
            "not_customizable", "This product is not customizable", status_code=422
        )
    settings = repositories.get_product_settings(
        session=session, store_id=store_id, product_id=product_id
    )
    if settings is None:
        raise AppError(
            "not_customizable", "This product has no 3D model linked", status_code=422
        )
    version = repositories.get_active_version(
        session=session, model_id=settings.platform_3d_model_id
    )
    if version is None:
        raise AppError(
            "model_unavailable",
            "The linked 3D model has no active version",
            status_code=422,
        )
    return version


def _pinned_version(
    *, session: Session, obj: CustomizationSession
) -> Platform3DModelVersion:
    """Return the version the session is pinned to (regardless of activeness)."""
    version = repositories.get_version(
        session=session, version_id=obj.platform_3d_model_version_id
    )
    if version is None:  # pragma: no cover — FK guarantees the version exists
        raise AppError(
            "model_unavailable", "The pinned 3D model is unavailable", status_code=422
        )
    return version


def _require_editable(obj: CustomizationSession) -> None:
    """Guard that a session can still be edited (draft + not past expiry).

    Args:
        obj: The session to check.

    Raises:
        AppError: 409 if already approved/terminal; 410 if past its expiry.
    """
    if obj.status != CustomizationSessionStatus.draft:
        raise AppError(
            "session_not_editable",
            "This session can no longer be edited",
            status_code=409,
        )
    if obj.expires_at <= get_datetime_utc():
        raise AppError("session_expired", "This session has expired", status_code=410)


def _parse_state(data: dict[str, object]) -> StateJson:
    """Parse a stored/incoming state dict into the typed contract (422 if bad)."""
    try:
        return StateJson.model_validate(data)
    except ValidationError as exc:
        raise AppError(
            "invalid_state", "Malformed customization state", status_code=422
        ) from exc


def _validate_state(
    *,
    state: StateJson,
    version: Platform3DModelVersion,
    upload_ids: set[uuid.UUID],
) -> None:
    """Validate the editor state against the pinned version (never the client).

    Checks the schema version, that the state pins this version, and every
    layer: its area exists, its transform is in range, image layers reference an
    upload of this session, text layers use an allowed font/size, and no area
    exceeds its ``max_layers``.

    Args:
        state: The parsed editor state.
        version: The pinned catalog version (source of allowed areas/fonts).
        upload_ids: Ids of uploads that belong to this session.

    Raises:
        AppError: 422 with a specific code on the first rule that fails.
    """
    if state.schema_version != 1:
        raise AppError(
            "unsupported_schema", "Unsupported state schema version", status_code=422
        )
    if state.model.version_id != version.id:
        raise AppError(
            "version_mismatch",
            "The state is pinned to a different model version",
            status_code=422,
        )

    areas = {
        area["id"]: area
        for area in version.printable_areas
        if isinstance(area.get("id"), str)
    }
    fonts_raw = version.text_config.get("fonts")
    fonts = (
        {f for f in fonts_raw if isinstance(f, str)}
        if isinstance(fonts_raw, list)
        else set()
    )
    min_size = version.text_config.get("min_size")
    max_size = version.text_config.get("max_size")
    per_area: dict[str, int] = {}

    for layer in state.layers:
        if layer.area_id not in areas:
            raise AppError(
                "unknown_area", f"Unknown printable area: {layer.area_id}", 422
            )
        per_area[layer.area_id] = per_area.get(layer.area_id, 0) + 1
        t = layer.transform
        if not (0.0 <= t.x <= 1.0 and 0.0 <= t.y <= 1.0) or t.scale <= 0:
            raise AppError(
                "transform_out_of_range",
                "Layer transform is out of the printable region",
                status_code=422,
            )
        if layer.kind == "image":
            if layer.upload_id is None or layer.upload_id not in upload_ids:
                raise AppError(
                    "unknown_upload",
                    "Image layer references an unknown upload",
                    status_code=422,
                )
        else:  # text
            if not layer.text or not layer.text.strip():
                raise AppError("empty_text", "Text layer is empty", status_code=422)
            if fonts and layer.font not in fonts:
                raise AppError(
                    "font_not_allowed", "Font is not allowed", status_code=422
                )
            if (
                layer.font_size is None
                or (isinstance(min_size, int) and layer.font_size < min_size)
                or (isinstance(max_size, int) and layer.font_size > max_size)
            ):
                raise AppError(
                    "font_size_out_of_range",
                    "Font size is out of the allowed range",
                    status_code=422,
                )

    for area_id, count in per_area.items():
        max_layers = areas[area_id].get("max_layers")
        if isinstance(max_layers, int) and count > max_layers:
            raise AppError(
                "too_many_layers",
                f"Area '{area_id}' allows at most {max_layers} layers",
                status_code=422,
            )


def _image_dimensions(data: bytes) -> tuple[int, int]:
    """Return an image's (width, height), or raise 422 if it can't be decoded."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            return int(img.width), int(img.height)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise AppError(
            "invalid_image", "The file is not a readable image", status_code=422
        ) from exc


# --- public service API -----------------------------------------------------


def start_session(
    *,
    session: Session,
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    guest_session_id: str,
) -> SessionPublic:
    """Start (or resume) a guest's draft session for a customizable product.

    Args:
        session: Active database session.
        store_id: The resolved store id.
        product_id: The product to customize.
        guest_session_id: The guest browser's session id.

    Returns:
        The new or resumed session DTO.

    Raises:
        AppError: 404 if the product is missing; 422 if it is not customizable.
    """
    version = _resolve_customizable_version(
        session=session, store_id=store_id, product_id=product_id
    )
    existing = repositories.get_guest_draft(
        session=session,
        store_id=store_id,
        product_id=product_id,
        guest_session_id=guest_session_id,
    )
    if existing is not None:
        return _to_session_public(obj=existing, version=version)
    obj = CustomizationSession(
        store_id=store_id,
        product_id=product_id,
        platform_3d_model_version_id=version.id,
        state_json=_initial_state(model_id=version.model_id, version_id=version.id),
        status=CustomizationSessionStatus.draft,
        guest_session_id=guest_session_id,
        expires_at=get_datetime_utc() + SESSION_TTL,
    )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return _to_session_public(obj=obj, version=version)


def get_guest_session(
    *,
    session: Session,
    store_id: uuid.UUID,
    session_id: uuid.UUID,
    guest_session_id: str,
) -> CustomizationSession:
    """Load a session and assert the guest owns it.

    Args:
        session: Active database session.
        store_id: The resolved store id.
        session_id: The session id.
        guest_session_id: The requesting guest's session id.

    Returns:
        The owned session.

    Raises:
        AppError: 404 if missing or owned by another guest/the store.
    """
    obj = repositories.get_session(
        session=session, store_id=store_id, session_id=session_id
    )
    if obj is None or obj.guest_session_id != guest_session_id:
        raise AppError("session_not_found", "Session not found", status_code=404)
    return obj


def view_session(*, session: Session, obj: CustomizationSession) -> SessionPublic:
    """Return a session DTO for an already-loaded, ownership-checked session."""
    return _to_session_public(
        obj=obj, version=_pinned_version(session=session, obj=obj)
    )


def autosave(
    *, session: Session, obj: CustomizationSession, state: StateJson
) -> SessionPublic:
    """Validate and persist the editor state of an editable session.

    Args:
        session: Active database session.
        obj: The (owned) session to update.
        state: The incoming editor state.

    Returns:
        The updated session DTO.

    Raises:
        AppError: 409/410 if not editable; 422 if the state is invalid.
    """
    _require_editable(obj)
    version = _pinned_version(session=session, obj=obj)
    upload_ids = {
        u.id
        for u in repositories.list_session_uploads(session=session, session_id=obj.id)
    }
    _validate_state(state=state, version=version, upload_ids=upload_ids)
    obj.state_json = state.model_dump(mode="json")
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return _to_session_public(obj=obj, version=version)


def add_upload(
    *,
    session: Session,
    obj: CustomizationSession,
    data: bytes,
    content_type: str,
) -> UploadPublic:
    """Store a customer's raster art privately and record the upload.

    Args:
        session: Active database session.
        obj: The (owned) editable session.
        data: The raw image bytes.
        content_type: The declared MIME type.

    Returns:
        The created upload DTO (with a presigned read URL + low-res warning).

    Raises:
        AppError: 409/410 if not editable; 422 unsupported type / unreadable
            image; 413 if too large.
    """
    _require_editable(obj)
    version = _pinned_version(session=session, obj=obj)
    limits = version.art_limits
    mimes_raw = limits.get("mimes")
    mimes = mimes_raw if isinstance(mimes_raw, list) else list(_DEFAULT_MIMES)
    max_bytes_raw = limits.get("max_bytes")
    max_bytes = max_bytes_raw if isinstance(max_bytes_raw, int) else _DEFAULT_MAX_BYTES
    min_dimension_raw = limits.get("min_dimension")
    min_dimension = (
        min_dimension_raw
        if isinstance(min_dimension_raw, int)
        else _DEFAULT_MIN_DIMENSION
    )

    if content_type not in mimes:
        raise AppError(
            "unsupported_media", f"Unsupported file type: {content_type}", 422
        )
    if len(data) > max_bytes:
        raise AppError("file_too_large", "The file exceeds the maximum size", 413)
    width, height = _image_dimensions(data)
    low_resolution = min(width, height) < min_dimension

    filename = f"{uuid.uuid4().hex}.{_EXT.get(content_type, 'bin')}"
    key = customization_upload_key(obj.store_id, obj.id, filename)
    storage.upload_fileobj(key, io.BytesIO(data), content_type)
    upload = CustomizationUpload(
        store_id=obj.store_id,
        customization_session_id=obj.id,
        key=key,
        mime=content_type,
        size_bytes=len(data),
        width=width,
        height=height,
    )
    session.add(upload)
    session.commit()
    session.refresh(upload)
    return UploadPublic(
        id=upload.id,
        mime=upload.mime,
        size_bytes=upload.size_bytes,
        width=upload.width,
        height=upload.height,
        url=storage.generate_presigned_url(key),
        low_resolution=bool(low_resolution),
    )


def approve_session(
    *,
    session: Session,
    obj: CustomizationSession,
    snapshot_data: bytes,
    snapshot_content_type: str,
) -> SessionPublic:
    """Freeze a session: store the approval snapshot and mark it approved.

    The current ``state_json`` is re-validated against the pinned version; the
    snapshot (client-side PNG, doc 30 §5) is mandatory and stored privately.

    Args:
        session: Active database session.
        obj: The (owned) editable session.
        snapshot_data: The approval snapshot PNG bytes.
        snapshot_content_type: The snapshot MIME type (must be PNG).

    Returns:
        The approved session DTO.

    Raises:
        AppError: 409/410 if not editable; 422 if the snapshot is not a PNG or
            the saved state is invalid.
    """
    _require_editable(obj)
    if snapshot_content_type != SNAPSHOT_MIME:
        raise AppError("invalid_snapshot", "The snapshot must be a PNG", 422)
    _image_dimensions(snapshot_data)
    version = _pinned_version(session=session, obj=obj)
    state = _parse_state(obj.state_json)
    upload_ids = {
        u.id
        for u in repositories.list_session_uploads(session=session, session_id=obj.id)
    }
    _validate_state(state=state, version=version, upload_ids=upload_ids)

    filename = f"snapshot-{uuid.uuid4().hex}.png"
    key = customization_upload_key(obj.store_id, obj.id, filename)
    storage.upload_fileobj(key, io.BytesIO(snapshot_data), SNAPSHOT_MIME)
    obj.snapshot_key = key
    obj.status = CustomizationSessionStatus.approved
    obj.approved_at = get_datetime_utc()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return _to_session_public(obj=obj, version=version)


def create_assisted_session(
    *,
    session: Session,
    store_id: uuid.UUID,
    created_by: uuid.UUID,
    payload: AssistedSessionCreate,
) -> AssistedSessionPublic:
    """Assemble a session on a customer's behalf with a shareable link (§9).

    Args:
        session: Active database session.
        store_id: The active store id.
        created_by: The store user assembling the session.
        payload: Product + customer contact.

    Returns:
        The session DTO plus its read-only ``public_token``.

    Raises:
        AppError: 404/422 as in :func:`_resolve_customizable_version`; 422 if the
            contact is insufficient (no email/phone).
    """
    version = _resolve_customizable_version(
        session=session, store_id=store_id, product_id=payload.product_id
    )
    customer = create_or_update_customer(
        session=session,
        store_id=store_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        region=payload.region,
    )
    token = secrets.token_urlsafe(32)
    obj = CustomizationSession(
        store_id=store_id,
        product_id=payload.product_id,
        platform_3d_model_version_id=version.id,
        state_json=_initial_state(model_id=version.model_id, version_id=version.id),
        status=CustomizationSessionStatus.draft,
        customer_id=customer.id,
        created_by_user_id=created_by,
        public_token=token,
        expires_at=get_datetime_utc() + SESSION_TTL,
    )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    public = _to_session_public(obj=obj, version=version)
    return AssistedSessionPublic(**public.model_dump(), public_token=token)


def _live_token_session(*, session: Session, token: str) -> CustomizationSession:
    """Resolve a session by public token, rejecting expired/missing ones.

    Args:
        session: Active database session.
        token: The session's public token.

    Returns:
        The live session.

    Raises:
        AppError: 404 if missing; 410 if expired.
    """
    obj = repositories.get_session_by_token(session=session, public_token=token)
    if obj is None:
        raise AppError("session_not_found", "Session not found", status_code=404)
    if (
        obj.status == CustomizationSessionStatus.expired
        or obj.expires_at <= get_datetime_utc()
    ):
        raise AppError("session_expired", "This link has expired", status_code=410)
    return obj


def view_public_session(*, session: Session, token: str) -> SessionPublic:
    """Return the read-only session a public link points to (doc 30 §9)."""
    obj = _live_token_session(session=session, token=token)
    return _to_session_public(
        obj=obj, version=_pinned_version(session=session, obj=obj)
    )


def _confirm_contact(
    *, session: Session, obj: CustomizationSession, contact: ContactConfirm
) -> None:
    """Assert the typed contact matches the session's pre-registered customer.

    Args:
        session: Active database session.
        obj: The session being approved via its public link.
        contact: The email/phone the approver typed.

    Raises:
        AppError: 403 if there is no customer or the contact does not match.
    """
    customer = (
        session.get(CustomerProfile, obj.customer_id)
        if obj.customer_id is not None
        else None
    )
    if customer is None:
        raise AppError("contact_required", "Confirm your contact to approve", 403)

    matched = False
    if contact.email and customer.email:
        matched = normalize_email(contact.email) == customer.email
    if not matched and contact.phone and contact.region and customer.phone_e164:
        try:
            matched = (
                normalize_phone(contact.phone, contact.region) == customer.phone_e164
            )
        except AppError:
            matched = False
    if not matched:
        raise AppError(
            "contact_mismatch", "The contact does not match our records", 403
        )


def approve_via_token(
    *,
    session: Session,
    token: str,
    contact: ContactConfirm,
    snapshot_data: bytes,
    snapshot_content_type: str,
) -> SessionPublic:
    """Approve a session through its public link, confirming the contact (§9).

    Args:
        session: Active database session.
        token: The session's public token.
        contact: The email/phone the approver typed to prove who they are.
        snapshot_data: The approval snapshot PNG bytes.
        snapshot_content_type: The snapshot MIME type (must be PNG).

    Returns:
        The approved session DTO.

    Raises:
        AppError: 404/410 for a missing/expired link; 403 on contact mismatch;
            422/409 as in :func:`approve_session`.
    """
    obj = _live_token_session(session=session, token=token)
    _confirm_contact(session=session, obj=obj, contact=contact)
    return approve_session(
        session=session,
        obj=obj,
        snapshot_data=snapshot_data,
        snapshot_content_type=snapshot_content_type,
    )


def expire_sessions(*, session: Session, now: datetime | None = None) -> int:
    """Sweep open sessions past their expiry to ``expired`` (soft-deleted).

    Never a hard delete: the row stays for history. Run daily by the worker.

    Args:
        session: Active database session.
        now: The reference time (defaults to the current UTC time).

    Returns:
        How many sessions were expired.
    """
    moment = now or get_datetime_utc()
    stale = repositories.list_expirable_sessions(session=session, now=moment)
    for obj in stale:
        obj.status = CustomizationSessionStatus.expired
        obj.deleted_at = moment
        session.add(obj)
    if stale:
        session.commit()
    return len(stale)
