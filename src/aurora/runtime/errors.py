"""Internal runtime error taxonomy (M13).

:class:`AuroraRuntimeError` is the shared base for first-party seam exceptions.
Public leaf types (
:class:`~aurora.runtime.shared_library_loader.SharedLibraryLoadError`,
:class:`~aurora.runtime.image.ImageCreationError`) keep their own constructors
and message text; this module does not replace them with a single generic type.

**Does not prove:** MediaPipe correctness, native behavior, or an exhaustive
runtime error taxonomy.
"""

from __future__ import annotations


class AuroraRuntimeError(Exception):
    """Base class for first-party runtime seam errors (M13).

    Subclasses preserve their own constructors and externally visible message
    semantics.
    """


__all__ = ["AuroraRuntimeError"]
