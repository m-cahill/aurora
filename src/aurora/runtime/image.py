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
from typing import Any, cast

from .dispatch_tokens import IMAGE_FROM_BYTES, IMAGE_FROM_FILE
from .dispatcher import Dispatcher
from .errors import AuroraRuntimeError
from .image_dispatch import dispatch_image_from_bytes, dispatch_image_from_file
from .library_loader import LibraryLoader


class ImageCreationError(AuroraRuntimeError):
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
    def _from_dispatch(
        cls,
        *,
        dispatcher: Dispatcher,
        library_loader: LibraryLoader,
        source_path: str | None,
        token: str,
        dispatch_arg: str | bytes,
        failure_message: str,
    ) -> AuroraImage:
        """Shared path for ``from_file`` / ``from_bytes`` (private; not public API)."""
        if token not in (IMAGE_FROM_FILE, IMAGE_FROM_BYTES):
            raise AssertionError(f"unexpected AuroraImage dispatch token: {token!r}")
        try:
            if token == IMAGE_FROM_FILE:
                handle = dispatch_image_from_file(
                    dispatcher, library_loader, cast(str, dispatch_arg)
                )
            else:
                handle = dispatch_image_from_bytes(
                    dispatcher, library_loader, cast(bytes, dispatch_arg)
                )
        except Exception as exc:
            err = ImageCreationError(failure_message)
            raise err from exc
        return cls(
            dispatcher=dispatcher,
            library_loader=library_loader,
            native_handle=handle,
            source_path=source_path,
        )

    @classmethod
    def from_file(
        cls,
        path: str,
        dispatcher: Dispatcher,
        library_loader: LibraryLoader,
    ) -> AuroraImage:
        """Create an image handle by routing through the loader and dispatcher.

        Operation token passed to ``dispatch`` is ``IMAGE_FROM_FILE`` (see
        ``aurora.runtime.dispatch_tokens``) with arguments
        ``(path, shared_library_handle)``.
        """
        return cls._from_dispatch(
            dispatcher=dispatcher,
            library_loader=library_loader,
            source_path=path,
            token=IMAGE_FROM_FILE,
            dispatch_arg=path,
            failure_message=f"Failed to create image from file {path!r}",
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        dispatcher: Dispatcher,
        library_loader: LibraryLoader,
    ) -> AuroraImage:
        """Create an image handle from a raw byte buffer (no NumPy dependency).

        Operation token passed to ``dispatch`` is ``IMAGE_FROM_BYTES`` (see
        ``aurora.runtime.dispatch_tokens``) with arguments
        ``(data, shared_library_handle)``.
        """
        return cls._from_dispatch(
            dispatcher=dispatcher,
            library_loader=library_loader,
            source_path=None,
            token=IMAGE_FROM_BYTES,
            dispatch_arg=data,
            failure_message="Failed to create image from bytes",
        )


__all__ = ["AuroraImage", "ImageCreationError"]
