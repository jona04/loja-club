"""DTOs for the platform 3D catalog (merchant-facing browse)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import field_validator
from sqlmodel import SQLModel

from app.modules.catalog.enums import ProductType
from app.modules.customization.enums import (
    CustomizationProductionStatus,
    CustomizationSessionStatus,
)


class Platform3DModelVersionPublic(SQLModel):
    """The active version of a catalog model, as exposed to the merchant."""

    id: uuid.UUID
    version: int
    glb_url: str
    printable_areas: list[dict[str, object]]
    text_config: dict[str, object]
    art_limits: dict[str, object]


class Platform3DModelPublic(SQLModel):
    """A catalog model plus its active version (or ``None`` if none active)."""

    id: uuid.UUID
    name: str
    category: str
    slug: str
    active_version: Platform3DModelVersionPublic | None


class Platform3DModelVersionAdmin(SQLModel):
    """A model version as seen by the admin (includes ``is_active``)."""

    id: uuid.UUID
    version: int
    glb_url: str
    printable_areas: list[dict[str, object]]
    text_config: dict[str, object]
    art_limits: dict[str, object]
    is_active: bool


class Platform3DModelAdmin(SQLModel):
    """A catalog model for the admin (includes ``is_active`` + active version)."""

    id: uuid.UUID
    name: str
    category: str
    slug: str
    is_active: bool
    active_version: Platform3DModelVersionAdmin | None


class Platform3DModelUpdate(SQLModel):
    """Partial update of a catalog model's metadata/visibility."""

    name: str | None = None
    category: str | None = None
    is_active: bool | None = None


class Platform3DModelVersionUpdate(SQLModel):
    """Partial update of a version's editor parameters/visibility."""

    printable_areas: list[dict[str, object]] | None = None
    text_config: dict[str, object] | None = None
    art_limits: dict[str, object] | None = None
    is_active: bool | None = None


class ProductModelLink(SQLModel):
    """Request to link a product to a catalog 3D model (merchant choice)."""

    platform_3d_model_id: uuid.UUID
    type: ProductType
    production_notes: str | None = None


class ProductModelSettingsPublic(SQLModel):
    """A product's current 3D-model link, for the merchant panel."""

    product_id: uuid.UUID
    type: ProductType
    platform_3d_model_id: uuid.UUID
    model_name: str
    model_slug: str
    model_category: str
    production_notes: str | None


# --- Customization sessions (doc 30 §4) ---


class LayerTransform(SQLModel):
    """A layer's placement in the printable region (doc 30 §4).

    ``x``/``y`` are the center in region units; they may fall **outside** [0,1]
    when a layer is larger than the region (panned so an edge meets the region
    edge). ``scale`` is the width fraction; ``scale_y`` (optional) is a free
    height fraction for non-uniform distortion (``None`` = natural aspect).
    """

    x: float
    y: float
    scale: float
    scale_y: float | None = None
    rotation_deg: float = 0.0


class StateLayer(SQLModel):
    """One layer of the editor state: a raster image or a text run."""

    id: str
    kind: Literal["image", "text"]
    area_id: str
    z: int = 0
    transform: LayerTransform
    # image layers reference a private upload:
    upload_id: uuid.UUID | None = None
    # text layers carry their content + style:
    text: str | None = None
    font: str | None = None
    font_size: int | None = None
    color: str | None = None


class StateModelRef(SQLModel):
    """The catalog model + pinned version the state was built against."""

    model_id: uuid.UUID
    version_id: uuid.UUID


class StateJson(SQLModel):
    """The full editor state (doc 30 §4): pinned model + ordered layers.

    Structural shape only; the version-specific rules (allowed fonts, area ids,
    per-area layer caps, referenced uploads) are enforced in the service against
    the pinned version — never trusting the client.
    """

    schema_version: int = 1
    model: StateModelRef
    layers: list[StateLayer] = []


class SessionStart(SQLModel):
    """Request to start (or resume) a customization session for a product."""

    product_id: uuid.UUID


class UploadPublic(SQLModel):
    """A customer upload, with a short-lived presigned read URL."""

    id: uuid.UUID
    mime: str
    size_bytes: int
    width: int | None
    height: int | None
    url: str
    low_resolution: bool = False


class SessionPublic(SQLModel):
    """A customization session as the editor (or a read-only viewer) sees it."""

    id: uuid.UUID
    product_id: uuid.UUID
    status: CustomizationSessionStatus
    state_json: dict[str, object]
    version: Platform3DModelVersionPublic
    uploads: list[UploadPublic]
    snapshot_url: str | None
    composite_url: str | None
    expires_at: datetime
    approved_at: datetime | None


# --- Merchant panel: operate customizations (doc 22 / P7-OPS-01) ---


class MerchantSessionListItem(SQLModel):
    """A store's customization session as a row in the merchant panel list.

    Lightweight (one presigned thumbnail); the full art + downloads are in the
    detail. ``production_status`` is present only once the session is ordered.
    """

    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    status: CustomizationSessionStatus
    is_assisted: bool
    snapshot_url: str | None
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None
    order_id: uuid.UUID | None
    order_item_id: uuid.UUID | None
    production_status: CustomizationProductionStatus | None


class MerchantSessionDetail(SessionPublic):
    """A session's full detail for the merchant: art + downloads + order link."""

    product_name: str
    is_assisted: bool
    order_id: uuid.UUID | None
    order_item_id: uuid.UUID | None
    production_status: CustomizationProductionStatus | None


class ProductionStatusUpdate(SQLModel):
    """Request to advance the production status of an ordered customization."""

    production_status: CustomizationProductionStatus


class AssistedSessionCreate(SQLModel):
    """Request (panel) to assemble a session on a customer's behalf (doc 30 §9)."""

    product_id: uuid.UUID
    name: str
    email: str | None = None
    phone: str | None = None
    region: str | None = None


class AssistedSessionPublic(SessionPublic):
    """An assisted session plus its shareable read-only public token."""

    public_token: str


class ContactConfirm(SQLModel):
    """The contact a public-link approver types to prove who they are."""

    email: str | None = None
    phone: str | None = None
    region: str | None = None

    @field_validator("email", "phone", "region")
    @classmethod
    def _blank_to_none(cls, value: str | None) -> str | None:
        """Treat empty/whitespace form fields as absent.

        Args:
            value: The raw field value.

        Returns:
            ``None`` when blank, else the stripped value.
        """
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
