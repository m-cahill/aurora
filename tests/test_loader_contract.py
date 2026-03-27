"""Contract tests for ``LibraryLoader`` (M06; stdlib unittest).

Requires ``PYTHONPATH`` to include ``src`` (set in CI and documented in DEVELOPMENT.md).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


_HANDLE = object()


class _StubLibraryLoader:
    """Minimal fake satisfying :class:`LibraryLoader` (singleton-style handle)."""

    def shared_library(self) -> Any:
        return _HANDLE


class TestLibraryLoaderContract(unittest.TestCase):
    def test_module_imports(self) -> None:
        from aurora.runtime.library_loader import LibraryLoader  # noqa: PLC0415

        self.assertTrue(callable(LibraryLoader))

    def test_stub_satisfies_protocol(self) -> None:
        from aurora.runtime.library_loader import LibraryLoader  # noqa: PLC0415

        stub = _StubLibraryLoader()
        self.assertIsInstance(stub, LibraryLoader)
        self.assertIs(stub.shared_library(), _HANDLE)

    def test_contract_documents_singleton_assumption_in_docstring(self) -> None:
        import aurora.runtime.library_loader as ll  # noqa: PLC0415

        self.assertIn("singleton", ll.LibraryLoader.__doc__.lower())
        self.assertIn("shared_library", ll.LibraryLoader.__doc__)


if __name__ == "__main__":
    unittest.main()
