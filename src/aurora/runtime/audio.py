"""Bounded first-party audio seam surface (M19).

``AuroraAudio`` routes creation through injected :class:`Dispatcher` and
:class:`LibraryLoader` seams, parallel in shape to :class:`~aurora.runtime.image.AuroraImage`.
This module does **not** import the stdlib foreign-function layer or load native
libraries directly; callers inject concrete seam objects.

**Does not prove:** MediaPipe compatibility, correct audio decoding, acoustic
kernel behavior, or any particular native symbol set — only governed seam
routing in-repo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from .audio_dispatch import dispatch_audio_from_bytes, dispatch_audio_from_file
from .dispatch_tokens import AUDIO_FROM_BYTES, AUDIO_FROM_FILE
from .dispatcher import Dispatcher
from .errors import AuroraRuntimeError
from .library_loader import LibraryLoader


class AudioCreationError(AuroraRuntimeError):
    """Raised when bounded audio creation fails (loader or dispatch path).

    Chains the underlying exception when one is available (mirrors
    :class:`~aurora.runtime.image.ImageCreationError` posture from M08).
    """


@dataclass(frozen=True, slots=True)
class AuroraAudio:
    """Small bounded surface for audio creation at the Python/native seam.

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
    ) -> AuroraAudio:
        """Shared path for ``from_file`` / ``from_bytes`` (private; not public API)."""
        if token not in (AUDIO_FROM_FILE, AUDIO_FROM_BYTES):
            raise AssertionError(f"unexpected AuroraAudio dispatch token: {token!r}")
        try:
            if token == AUDIO_FROM_FILE:
                handle = dispatch_audio_from_file(
                    dispatcher, library_loader, cast(str, dispatch_arg)
                )
            else:
                handle = dispatch_audio_from_bytes(
                    dispatcher, library_loader, cast(bytes, dispatch_arg)
                )
        except Exception as exc:
            err = AudioCreationError(failure_message)
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
    ) -> AuroraAudio:
        """Create an audio handle by routing through the loader and dispatcher.

        Operation token passed to ``dispatch`` is ``AUDIO_FROM_FILE`` (see
        ``aurora.runtime.dispatch_tokens``) with arguments
        ``(path, shared_library_handle)``.
        """
        return cls._from_dispatch(
            dispatcher=dispatcher,
            library_loader=library_loader,
            source_path=path,
            token=AUDIO_FROM_FILE,
            dispatch_arg=path,
            failure_message=f"Failed to create audio from file {path!r}",
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        dispatcher: Dispatcher,
        library_loader: LibraryLoader,
    ) -> AuroraAudio:
        """Create an audio handle from a raw byte buffer (no NumPy dependency).

        Operation token passed to ``dispatch`` is ``AUDIO_FROM_BYTES`` (see
        ``aurora.runtime.dispatch_tokens``) with arguments
        ``(data, shared_library_handle)``.
        """
        return cls._from_dispatch(
            dispatcher=dispatcher,
            library_loader=library_loader,
            source_path=None,
            token=AUDIO_FROM_BYTES,
            dispatch_arg=data,
            failure_message="Failed to create audio from bytes",
        )


__all__ = ["AuroraAudio", "AudioCreationError"]
