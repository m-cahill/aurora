"""Bounded first-party image seam surface (M08).

``AuroraImage`` routes creation through injected :class:`Dispatcher` and
:class:`LibraryLoader` seams. This module does **not** import the stdlib
foreign-function layer or load native libraries directly; callers inject
concrete seam objects.

**Does not prove:** MediaPipe compatibility, correct image decoding, or any
particular native symbol set — only governed seam routing in-repo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dispatcher import Dispatcher
from .library_loader import LibraryLoader


class ImageCreationError(Exception):
    """Raised when bounded image creation fails (loader or dispatch path).

    Chains the underlying exception when one is available (mirrors
    :class:`SharedLibraryLoadError` posture from M07).
    """


@dataclass(frozen=True, slots=True)
class AuroraImage:
    """Small bounded surface for image creation at the Python/native seam.

    Instances hold an opaque ``native_handle`` produced by the injected
    ``dispatcher``; no direct native library calls live in this module.
    """

    dispatcher: Dispatcher
    library_loader: LibraryLoader
    native_handle: Any
    source_path: str | None = None

    @classmethod
    def from_file(
        cls,
        path: str,
        dispatcher: Dispatcher,
        library_loader: LibraryLoader,
    ) -> AuroraImage:
        """Create an image handle by routing through the loader and dispatcher.

        Operation token passed to ``dispatch`` is ``\"aurora_image_from_file\"``
        with arguments ``(path, shared_library_handle)``.
        """
        try:
            lib = library_loader.shared_library()
            handle = dispatcher.dispatch("aurora_image_from_file", path, lib)
        except Exception as exc:
            err = ImageCreationError(f"Failed to create image from file {path!r}")
            raise err from exc
        return cls(
            dispatcher=dispatcher,
            library_loader=library_loader,
            native_handle=handle,
            source_path=path,
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        dispatcher: Dispatcher,
        library_loader: LibraryLoader,
    ) -> AuroraImage:
        """Create an image handle from a raw byte buffer (no NumPy dependency).

        Operation token passed to ``dispatch`` is ``\"aurora_image_from_bytes\"``
        with arguments ``(data, shared_library_handle)``.
        """
        try:
            lib = library_loader.shared_library()
            handle = dispatcher.dispatch("aurora_image_from_bytes", data, lib)
        except Exception as exc:
            err = ImageCreationError("Failed to create image from bytes")
            raise err from exc
        return cls(
            dispatcher=dispatcher,
            library_loader=library_loader,
            native_handle=handle,
            source_path=None,
        )


__all__ = ["AuroraImage", "ImageCreationError"]
