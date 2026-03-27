"""Runtime package: substrate (M05) and seam contracts (M06).

Phase B introduces minimal ``Dispatcher`` and ``LibraryLoader`` protocols only;
they are typing contracts, not MediaPipe or native implementations.
"""

from __future__ import annotations

from .dispatcher import Dispatcher
from .library_loader import LibraryLoader
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
]
