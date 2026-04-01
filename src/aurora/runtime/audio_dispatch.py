"""Internal ``AuroraAudio`` dispatch invocation contract (M19).

Single source of truth for acquiring the shared-library handle and invoking
:class:`~aurora.runtime.dispatcher.Dispatcher` with the M19 operation tokens
and the frozen positional argument order: ``(token, payload, lib)``.

**Does not prove:** native behavior, decode correctness, or MediaPipe parity —
only the in-repo call shape at the Python seam.

Callers (``AuroraAudio``) own :class:`~aurora.runtime.audio.AudioCreationError`
wrapping and dataclass construction; this module returns the opaque native
handle only.
"""

from __future__ import annotations

from typing import Any

from .dispatch_tokens import AUDIO_FROM_BYTES, AUDIO_FROM_FILE
from .dispatcher import Dispatcher
from .library_loader import LibraryLoader


def dispatch_audio_from_file(
    dispatcher: Dispatcher,
    library_loader: LibraryLoader,
    path: str,
) -> Any:
    """Dispatch ``AUDIO_FROM_FILE`` with ``path`` (after ``shared_library``)."""
    lib = library_loader.shared_library()
    return dispatcher.dispatch(AUDIO_FROM_FILE, path, lib)


def dispatch_audio_from_bytes(
    dispatcher: Dispatcher,
    library_loader: LibraryLoader,
    data: bytes,
) -> Any:
    """Dispatch ``AUDIO_FROM_BYTES`` with ``data`` (after ``shared_library``)."""
    lib = library_loader.shared_library()
    return dispatcher.dispatch(AUDIO_FROM_BYTES, data, lib)
