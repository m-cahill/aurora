"""Minimal ``LibraryLoader`` contract (M06).

This module is **first-party AURORA code**. It does not load native libraries or
import ``mediapipe``. It documents the audit-established **singleton**
shared-library assumption at the contract level.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LibraryLoader(Protocol):
    """Contract for the process-wide shared native library handle.

    Audits treat a single ``_shared_lib``-style **singleton** (one ``CDLL`` /
    shared-library handle per process for the Tasks API bindings) as a real
    runtime constraint. Implementations of this Protocol must preserve that
    assumption: ``shared_library()`` returns the same handle for the lifetime of
    the loader’s intended use in this process unless a future milestone
    explicitly documents and proves a different isolation model.

    **Does not prove:** correct native loading, symbol resolution, MediaPipe
    compatibility, thread safety, or that multiple independent ``CDLL``
    instances are safe.

    This is a **contract and documentation** surface for M06, not a loader
    implementation.
    """

    def shared_library(self) -> Any:
        """Return the singleton shared-library handle for this process."""
        ...
