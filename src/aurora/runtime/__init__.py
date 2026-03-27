"""Runtime substrate package (M05).

Phase B seam work (``Dispatcher``, loaders, etc.) is out of scope until
explicitly authorized; this package only establishes an importable substrate.
"""

from __future__ import annotations

from .surface import (
    SUBSTRATE_CONTRACT_VERSION,
    RuntimeSubstrateMetadata,
    get_runtime_substrate_metadata,
)

__all__ = [
    "SUBSTRATE_CONTRACT_VERSION",
    "RuntimeSubstrateMetadata",
    "get_runtime_substrate_metadata",
]
