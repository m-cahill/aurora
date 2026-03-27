"""Minimal ``Dispatcher`` contract (M06).

This module is **first-party AURORA code**. It does not import ``mediapipe`` or
copy upstream sources. It records a typing boundary for the Python/native
dispatch seam only.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Dispatcher(Protocol):
    """Contract for a single dispatch-style entry at the Python/native seam.

    Upstream MediaPipe Tasks API code routes most work through a serial dispatcher
    (e.g. ``SerialDispatcher``). This Protocol captures **only** a minimal
    ``dispatch``-shaped call surface — not lifecycle (create/close/shutdown),
    context-manager behavior, task ownership, or graph correctness.

    **Does not prove:** MediaPipe behavior, native graph execution, deterministic
    outputs, or correct binding to any particular C API.
    """

    def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke the native dispatch path; parameters are intentionally minimal."""
        ...
