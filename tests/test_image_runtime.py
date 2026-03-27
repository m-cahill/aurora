"""Runtime tests for bounded ``AuroraImage`` seam (M08; stdlib unittest).

Uses fakes for ``Dispatcher`` and ``LibraryLoader`` — no real host libraries.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class _FakeDispatcher:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((args, kwargs))
        return ("ok", args)


class _FakeLoader:
    def __init__(self, handle: Any = None, *, fail: bool = False) -> None:
        self._handle = handle if handle is not None else object()
        self._fail = fail
        self.calls = 0

    def shared_library(self) -> Any:
        self.calls += 1
        if self._fail:
            raise OSError("fake load failure")
        return self._handle


class TestAuroraImageRuntime(unittest.TestCase):
    def test_from_file_routes_through_dispatcher_and_loader(self) -> None:
        from aurora.runtime.image import AuroraImage  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        img = AuroraImage.from_file("/tmp/x.bin", disp, loader)
        self.assertEqual(loader.calls, 1)
        self.assertEqual(len(disp.calls), 1)
        args, kwargs = disp.calls[0]
        self.assertEqual(kwargs, {})
        self.assertEqual(args[0], "aurora_image_from_file")
        self.assertEqual(args[1], "/tmp/x.bin")
        self.assertIs(args[2], loader._handle)
        self.assertEqual(img.source_path, "/tmp/x.bin")
        self.assertIs(img.dispatcher, disp)
        self.assertIs(img.library_loader, loader)

    def test_from_bytes_routes_through_dispatcher_and_loader(self) -> None:
        from aurora.runtime.image import AuroraImage  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        raw = b"\xff\xd8\xff"
        img = AuroraImage.from_bytes(raw, disp, loader)
        self.assertEqual(loader.calls, 1)
        args, _kwargs = disp.calls[0]
        self.assertEqual(args[0], "aurora_image_from_bytes")
        self.assertEqual(args[1], raw)
        self.assertIs(args[2], loader._handle)
        self.assertIsNone(img.source_path)

    def test_loader_failure_is_image_creation_error_with_chain(self) -> None:
        from aurora.runtime.image import (  # noqa: PLC0415
            AuroraImage,
            ImageCreationError,
        )

        disp = _FakeDispatcher()
        loader = _FakeLoader(fail=True)
        with self.assertRaises(ImageCreationError) as ctx:
            AuroraImage.from_file("nope", disp, loader)
        self.assertIsInstance(ctx.exception.__cause__, OSError)
        self.assertEqual(disp.calls, [])

    def test_dispatch_failure_is_image_creation_error_with_chain(self) -> None:
        from aurora.runtime.image import (  # noqa: PLC0415
            AuroraImage,
            ImageCreationError,
        )

        class _BoomDispatcher:
            def dispatch(self, *args: Any, **kwargs: Any) -> Any:
                raise RuntimeError("fake dispatch")

        disp = _BoomDispatcher()
        loader = _FakeLoader()
        with self.assertRaises(ImageCreationError) as ctx:
            AuroraImage.from_file("p", disp, loader)
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)

    def test_image_module_has_no_raw_cdll(self) -> None:
        spec = importlib.util.find_spec("aurora.runtime.image")
        assert spec is not None and spec.origin is not None
        text = Path(spec.origin).read_text(encoding="utf-8")
        tree = ast.parse(text, filename=spec.origin)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    head = alias.name.split(".", 1)[0]
                    self.assertNotEqual(head, "ctypes")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module
                if mod is not None:
                    head = mod.split(".", 1)[0]
                    self.assertNotEqual(head, "ctypes")

    def test_runtime_package_exports_image(self) -> None:
        import aurora.runtime as rt  # noqa: PLC0415

        self.assertTrue(hasattr(rt, "AuroraImage"))
        self.assertTrue(hasattr(rt, "ImageCreationError"))
        self.assertIn("AuroraImage", rt.__all__)
        self.assertIn("ImageCreationError", rt.__all__)


if __name__ == "__main__":
    unittest.main()
