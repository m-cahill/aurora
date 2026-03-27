"""Concrete ``LibraryLoader`` implementation (M07).

Loads a shared library via ``ctypes.CDLL`` for a single **explicit** path passed at
construction. Memoizes the resulting handle on the instance: repeated
``shared_library()`` calls return the same object and do not invoke ``CDLL``
again.

This module does **not** import ``mediapipe``. It does **not** perform path
discovery (no environment variables, package resources, or search paths beyond
what the caller supplies).

**Does not prove:** correct symbols, MediaPipe compatibility, thread safety, or
that loading any particular path is meaningful for Tasks API usage.
"""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Any


class SharedLibraryLoadError(Exception):
    """Raised when ``ctypes.CDLL`` cannot load the configured library path."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Failed to load shared library: {path!r}")


class SharedLibraryLoader:
    """Load and hold a single shared-library handle for an explicit path.

    Singleton semantics apply **per instance**: the first successful call to
    ``shared_library()`` loads via ``ctypes.CDLL`` and caches the handle;
    subsequent calls return the cached value. A failed load is cached as well:
    later calls raise the same :class:`SharedLibraryLoadError` instance.

    **Does not prove:** native correctness, MediaPipe parity, or safe use of
    multiple instances pointing at the same filesystem path.
    """

    __slots__ = ("_path", "_cached", "_failure")

    def __init__(self, path: str | os.PathLike[str]) -> None:
        # Normalize for stable identity and error messages; caller supplies path.
        self._path = Path(path).expanduser().resolve()
        self._cached: Any | None = None
        self._failure: SharedLibraryLoadError | None = None

    @property
    def library_path(self) -> Path:
        """Resolved path used for loading (read-only)."""
        return self._path

    def shared_library(self) -> Any:
        """Return the memoized ``CDLL`` instance for this loader's path."""
        if self._cached is not None:
            return self._cached
        if self._failure is not None:
            raise self._failure
        path_str = str(self._path)
        try:
            handle = ctypes.CDLL(path_str)
        except OSError as exc:
            err = SharedLibraryLoadError(path_str)
            self._failure = err
            raise err from exc
        self._cached = handle
        return handle


__all__ = ["SharedLibraryLoader", "SharedLibraryLoadError"]
