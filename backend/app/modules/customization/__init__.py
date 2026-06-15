"""Customization module: the platform 3D catalog and personalization.

It starts with the **public 3D catalog** (platform-owned, seeded):
:class:`~app.modules.customization.models.Platform3DModel` and its immutable
versions, which the merchant picks from. Customization sessions, uploads and
order freezing build on top of it.
"""
