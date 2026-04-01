"""Runtime package: substrate (M05), seam contracts (M06), and concrete loader (M07).

``Dispatcher`` / ``LibraryLoader`` are minimal ``typing.Protocol`` definitions.
``SharedLibraryLoader`` is a first-party ``ctypes.CDLL`` wrapper — not MediaPipe.
``AuroraImage`` / ``ImageCreationError`` (M08) route image creation through injected seams;
``image.py`` does not load native libraries directly.
``AuroraAudio`` / ``AudioCreationError`` (M19) are the bounded audio seam sibling — not
acoustic kernel extraction or decode correctness.
"""

from __future__ import annotations

from .audio import AudioCreationError, AuroraAudio
from .dispatcher import Dispatcher
from .image import AuroraImage, ImageCreationError
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
    "AuroraImage",
    "ImageCreationError",
    "AuroraAudio",
    "AudioCreationError",
    "LibraryLoader",
    "SharedLibraryLoader",
    "SharedLibraryLoadError",
]
