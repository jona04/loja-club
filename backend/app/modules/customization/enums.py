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
