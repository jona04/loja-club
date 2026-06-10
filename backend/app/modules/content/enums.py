"""Enumerations for the content module."""

from enum import Enum


class MenuLocation(str, Enum):
    """Where a store navigation menu renders on the storefront (doc 10).

    Read by the storefront API (``P3-SF-01``) to select the header/footer menu.
    """

    header = "header"
    footer = "footer"
