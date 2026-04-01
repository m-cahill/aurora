"""Runtime tests for bounded ``AuroraAudio`` seam (M19; stdlib unittest).

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


class TestDispatchAudioTokenValues(unittest.TestCase):
    """M19 — pin exact audio dispatch token strings (behavior surface)."""

    def test_audio_dispatch_tokens_are_stable(self) -> None:
        from aurora.runtime.dispatch_tokens import (  # noqa: PLC0415
            AUDIO_FROM_BYTES,
            AUDIO_FROM_FILE,
        )

        self.assertEqual(AUDIO_FROM_FILE, "aurora_audio_from_file")
        self.assertEqual(AUDIO_FROM_BYTES, "aurora_audio_from_bytes")


class TestAudioDispatchInvocationContract(unittest.TestCase):
    """M19 — pin dispatch call-shape at ``audio_dispatch`` helpers (internal)."""

    def test_dispatch_audio_from_file_shape(self) -> None:
        from aurora.runtime.audio_dispatch import (  # noqa: PLC0415
            dispatch_audio_from_file,
        )
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        handle = dispatch_audio_from_file(disp, loader, "/tmp/a.wav")
        self.assertEqual(loader.calls, 1)
        self.assertEqual(len(disp.calls), 1)
        args, kwargs = disp.calls[0]
        self.assertEqual(kwargs, {})
        self.assertEqual(args[0], AUDIO_FROM_FILE)
        self.assertEqual(args[1], "/tmp/a.wav")
        self.assertIs(args[2], loader._handle)
        self.assertEqual(handle, ("ok", args))

    def test_dispatch_audio_from_bytes_shape(self) -> None:
        from aurora.runtime.audio_dispatch import (  # noqa: PLC0415
            dispatch_audio_from_bytes,
        )
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_BYTES  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        raw = b"\x00\x01"
        handle = dispatch_audio_from_bytes(disp, loader, raw)
        self.assertEqual(loader.calls, 1)
        args, kwargs = disp.calls[0]
        self.assertEqual(kwargs, {})
        self.assertEqual(args[0], AUDIO_FROM_BYTES)
        self.assertEqual(args[1], raw)
        self.assertIs(args[2], loader._handle)
        self.assertEqual(handle, ("ok", args))


class TestAuroraAudioRuntime(unittest.TestCase):
    def test_from_file_routes_through_dispatcher_and_loader(self) -> None:
        from aurora.runtime.audio import AuroraAudio  # noqa: PLC0415
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        aud = AuroraAudio.from_file("/tmp/x.wav", disp, loader)
        self.assertEqual(loader.calls, 1)
        self.assertEqual(len(disp.calls), 1)
        args, kwargs = disp.calls[0]
        self.assertEqual(kwargs, {})
        self.assertEqual(args[0], AUDIO_FROM_FILE)
        self.assertEqual(args[1], "/tmp/x.wav")
        self.assertIs(args[2], loader._handle)
        self.assertEqual(aud.source_path, "/tmp/x.wav")
        self.assertIs(aud.dispatcher, disp)
        self.assertIs(aud.library_loader, loader)

    def test_from_bytes_routes_through_dispatcher_and_loader(self) -> None:
        from aurora.runtime.audio import AuroraAudio  # noqa: PLC0415
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_BYTES  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        raw = b"\xff\xfb\x90"
        aud = AuroraAudio.from_bytes(raw, disp, loader)
        self.assertEqual(loader.calls, 1)
        args, _kwargs = disp.calls[0]
        self.assertEqual(args[0], AUDIO_FROM_BYTES)
        self.assertEqual(args[1], raw)
        self.assertIs(args[2], loader._handle)
        self.assertIsNone(aud.source_path)

    def test_loader_failure_is_audio_creation_error_with_chain(self) -> None:
        from aurora.runtime.audio import (  # noqa: PLC0415
            AudioCreationError,
            AuroraAudio,
        )
        from aurora.runtime.errors import AuroraRuntimeError  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader(fail=True)
        with self.assertRaises(AudioCreationError) as ctx:
            AuroraAudio.from_file("nope", disp, loader)
        self.assertIsInstance(ctx.exception, AuroraRuntimeError)
        self.assertIsInstance(ctx.exception.__cause__, OSError)
        self.assertEqual(disp.calls, [])

    def test_loader_failure_from_bytes_is_audio_creation_error_with_chain(self) -> None:
        from aurora.runtime.audio import (  # noqa: PLC0415
            AudioCreationError,
            AuroraAudio,
        )
        from aurora.runtime.errors import AuroraRuntimeError  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader(fail=True)
        with self.assertRaises(AudioCreationError) as ctx:
            AuroraAudio.from_bytes(b"x", disp, loader)
        self.assertIsInstance(ctx.exception, AuroraRuntimeError)
        self.assertIsInstance(ctx.exception.__cause__, OSError)
        self.assertEqual(str(ctx.exception), "Failed to create audio from bytes")
        self.assertEqual(disp.calls, [])

    def test_dispatch_failure_is_audio_creation_error_with_chain(self) -> None:
        from aurora.runtime.audio import (  # noqa: PLC0415
            AudioCreationError,
            AuroraAudio,
        )
        from aurora.runtime.errors import AuroraRuntimeError  # noqa: PLC0415

        class _BoomDispatcher:
            def dispatch(self, *args: Any, **kwargs: Any) -> Any:
                raise RuntimeError("fake dispatch")

        disp = _BoomDispatcher()
        loader = _FakeLoader()
        with self.assertRaises(AudioCreationError) as ctx:
            AuroraAudio.from_file("p", disp, loader)
        self.assertIsInstance(ctx.exception, AuroraRuntimeError)
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)

    def test_unknown_dispatch_token_raises_assertion(self) -> None:
        from aurora.runtime.audio import AuroraAudio  # noqa: PLC0415

        disp = _FakeDispatcher()
        loader = _FakeLoader()
        with self.assertRaises(AssertionError):
            AuroraAudio._from_dispatch(
                dispatcher=disp,
                library_loader=loader,
                source_path=None,
                token="not_a_real_token",
                dispatch_arg=b"x",
                failure_message="x",
            )

    def test_audio_module_has_no_raw_cdll(self) -> None:
        spec = importlib.util.find_spec("aurora.runtime.audio")
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

    def test_runtime_package_exports_audio(self) -> None:
        import aurora.runtime as rt  # noqa: PLC0415

        self.assertTrue(hasattr(rt, "AuroraAudio"))
        self.assertTrue(hasattr(rt, "AudioCreationError"))
        self.assertIn("AuroraAudio", rt.__all__)
        self.assertIn("AudioCreationError", rt.__all__)


if __name__ == "__main__":
    unittest.main()
