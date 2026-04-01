"""Centralized ``Dispatcher.dispatch`` operation tokens (M14; M19 audio).

These string values are the de facto contract between bounded domain surfaces
(e.g. :class:`~aurora.runtime.image.AuroraImage`, :class:`~aurora.runtime.audio.AuroraAudio`)
and any :class:`~aurora.runtime.dispatcher.Dispatcher` implementation. Values are
frozen for behavior compatibility; new domains should add constants here rather
than scattering literals.

**Does not prove:** that any native implementation recognizes these tokens — only
in-repo naming stability at the seam.
"""

from __future__ import annotations

__all__ = [
    "IMAGE_FROM_FILE",
    "IMAGE_FROM_BYTES",
    "AUDIO_FROM_FILE",
    "AUDIO_FROM_BYTES",
]

# Bounded AuroraImage operations (M08/M14); values must remain byte-identical.
IMAGE_FROM_FILE = "aurora_image_from_file"
IMAGE_FROM_BYTES = "aurora_image_from_bytes"

# Bounded AuroraAudio operations (M19); parallel vocabulary to image seam.
AUDIO_FROM_FILE = "aurora_audio_from_file"
AUDIO_FROM_BYTES = "aurora_audio_from_bytes"
