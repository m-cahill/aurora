"""Runtime package: substrate (M05), seam contracts (M06), and concrete loader (M07).

``Dispatcher`` / ``LibraryLoader`` are minimal ``typing.Protocol`` definitions.
``SharedLibraryLoader`` is a first-party ``ctypes.CDLL`` wrapper — not MediaPipe.
"""

from __future__ import annotations

from .dispatcher import Dispatcher
from .library_loader import LibraryLoader
from .shared_library_loader import SharedLibraryLoader, SharedLibraryLoadError
from .surface import (
    SUBSTRATE_CONTRACT_VERSION,
    RuntimeSubstrateMetadata,
    get_runtime_substrate_metadata,
)

__all__ = [
    "SUBSTRATE_CONTRACT_VERSION",
    "RuntimeSubstrateMetadata",
    "get_runtime_substrate_metadata",
    "Dispatcher",
    "LibraryLoader",
    "SharedLibraryLoader",
    "SharedLibraryLoadError",
]
