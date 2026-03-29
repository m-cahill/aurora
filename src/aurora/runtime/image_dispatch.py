"""Internal ``AuroraImage`` dispatch invocation contract (M15).

Single source of truth for acquiring the shared-library handle and invoking
:class:`~aurora.runtime.dispatcher.Dispatcher` with the M14 operation tokens
and the frozen positional argument order: ``(token, payload, lib)``.

**Does not prove:** native behavior or decode correctness — only the in-repo
call shape at the Python seam.

Callers (``AuroraImage``) own :class:`~aurora.runtime.image.ImageCreationError`
wrapping and dataclass construction; this module returns the opaque native
handle only.
"""

from __future__ import annotations

from typing import Any

from .dispatch_tokens import IMAGE_FROM_BYTES, IMAGE_FROM_FILE
from .dispatcher import Dispatcher
from .library_loader import LibraryLoader


def dispatch_image_from_file(
    dispatcher: Dispatcher,
    library_loader: LibraryLoader,
    path: str,
) -> Any:
    """Dispatch ``IMAGE_FROM_FILE`` with ``path`` (after ``shared_library``)."""
    lib = library_loader.shared_library()
    return dispatcher.dispatch(IMAGE_FROM_FILE, path, lib)


def dispatch_image_from_bytes(
    dispatcher: Dispatcher,
    library_loader: LibraryLoader,
    data: bytes,
) -> Any:
    """Dispatch ``IMAGE_FROM_BYTES`` with ``data`` (after ``shared_library``)."""
    lib = library_loader.shared_library()
    return dispatcher.dispatch(IMAGE_FROM_BYTES, data, lib)
