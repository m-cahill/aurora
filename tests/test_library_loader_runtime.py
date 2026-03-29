"""Runtime tests for ``SharedLibraryLoader`` (M07; stdlib unittest).

Uses patched ``ctypes.CDLL`` — no real host shared libraries.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class TestSharedLibraryLoaderRuntime(unittest.TestCase):
    def test_satisfies_library_loader_protocol(self) -> None:
        from aurora.runtime.library_loader import LibraryLoader  # noqa: PLC0415
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake = object()
        path = REPO_ROOT / "nonexistent_loader_test_path.so"
        loader = SharedLibraryLoader(path)
        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake,
        ):
            self.assertIsInstance(loader, LibraryLoader)
            self.assertIs(loader.shared_library(), fake)

    def test_memoizes_single_cdll_handle(self) -> None:
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        path = REPO_ROOT / "memo_loader_test_path.so"
        loader = SharedLibraryLoader(path)
        fake = object()
        cdll = mock.Mock(return_value=fake)
        with mock.patch("aurora.runtime.shared_library_loader.ctypes.CDLL", cdll):
            a = loader.shared_library()
            b = loader.shared_library()
        self.assertIs(a, b)
        self.assertIs(a, fake)
        cdll.assert_called_once()

    def test_load_failure_is_deterministic(self) -> None:
        from aurora.runtime.errors import AuroraRuntimeError  # noqa: PLC0415
        from aurora.runtime.shared_library_loader import (  # noqa: PLC0415
            SharedLibraryLoader,
            SharedLibraryLoadError,
        )

        path = REPO_ROOT / "fail_loader_test_path.so"
        loader = SharedLibraryLoader(path)
        boom = OSError("no such fake library")
        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            side_effect=boom,
        ):
            with self.assertRaises(SharedLibraryLoadError) as ctx:
                loader.shared_library()
            first = ctx.exception
            with self.assertRaises(SharedLibraryLoadError) as ctx2:
                loader.shared_library()
            second = ctx2.exception
        self.assertIs(first, second)
        self.assertIsInstance(first, SharedLibraryLoadError)
        self.assertIsInstance(first, AuroraRuntimeError)
        self.assertIs(first.__cause__, boom)

    def test_runtime_package_exports(self) -> None:
        import aurora.runtime as rt  # noqa: PLC0415

        self.assertTrue(hasattr(rt, "SharedLibraryLoader"))
        self.assertTrue(hasattr(rt, "SharedLibraryLoadError"))
        self.assertIn("SharedLibraryLoader", rt.__all__)
        self.assertIn("SharedLibraryLoadError", rt.__all__)


if __name__ == "__main__":
    unittest.main()
