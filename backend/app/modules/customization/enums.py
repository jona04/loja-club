"""Enumerations for the customization module."""

from enum import Enum


class CustomizationSessionStatus(str, Enum):
    """Lifecycle of a customer's 3D customization session (doc 30 §4).

    - ``draft``: being edited; autosave writes the ``state_json`` here.
    - ``approved``: the customer approved a snapshot; frozen for editing, ready
      to add to the cart.
    - ``added_to_cart``: an approved session that is in a cart.
    - ``ordered``: copied (frozen) into a placed order (terminal).
    - ``abandoned``: explicitly given up by the customer.
    - ``expired``: aged past ``expires_at`` and swept by the worker (terminal).

    Editing (autosave/upload) is allowed only in ``draft``; ``approved`` and
    beyond are immutable. Deleting a session is a soft delete, never a status.
    """

    draft = "draft"
    approved = "approved"
    added_to_cart = "added_to_cart"
    ordered = "ordered"
    abandoned = "abandoned"
    expired = "expired"


class CustomizationProductionStatus(str, Enum):
    """Operational production status of an ordered customization (doc 22).

    A separate axis from the session lifecycle: it lives on the frozen
    ``customization_order_items`` row and is advanced by the merchant as they
    produce the art. It starts at ``received`` when the order is placed.

    - ``received``: art received (initial, set at order time).
    - ``reviewing``: the merchant is evaluating the art.
    - ``needs_contact``: the merchant needs to talk to the customer.
    - ``approved_for_production``: cleared to produce.
    - ``in_production``: being produced.
    - ``production_done``: production finished (terminal).
    """

    received = "received"
    reviewing = "reviewing"
    needs_contact = "needs_contact"
    approved_for_production = "approved_for_production"
    in_production = "in_production"
    production_done = "production_done"
