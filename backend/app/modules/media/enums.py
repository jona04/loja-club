"""Enumerations for the media module."""

from enum import Enum


class MediaStatus(str, Enum):
    """Processing status of an uploaded media file."""

    processing = "processing"
    ready = "ready"
    failed = "failed"
