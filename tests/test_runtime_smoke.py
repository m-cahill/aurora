"""Smoke tests for composed first-party runtime seams (M09; M19 audio; stdlib unittest).

Exercises :class:`~aurora.runtime.image.AuroraImage` and
:class:`~aurora.runtime.audio.AuroraAudio` with the real
:class:`~aurora.runtime.shared_library_loader.SharedLibraryLoader` (``ctypes.CDLL``
patched — no real host libraries) and a local recording fake
:class:`~aurora.runtime.dispatcher.Dispatcher`. This layer is intentionally
above M07/M08 unit tests: it proves the **composed** chain

``AuroraImage → SharedLibraryLoader → patched CDLL`` and
``AuroraImage → Dispatcher.dispatch(...)``

and the parallel audio seam (M19).

**Does not prove:** MediaPipe parity, decode correctness, real native execution,
or that dispatch tokens map to any upstream implementation.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class _RecordingDispatcher:
    """Minimal fake dispatcher that records ``dispatch`` calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((args, kwargs))
        return "smoke_native_handle"


class _BoomDispatcher:
    def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("smoke fake dispatch failure")


class TestRuntimeSmokeComposition(unittest.TestCase):
    def test_smoke_happy_path_from_file_composes_loader_and_dispatcher(self) -> None:
        from aurora.runtime.dispatch_tokens import IMAGE_FROM_FILE  # noqa: PLC0415
        from aurora.runtime.image import AuroraImage  # noqa: PLC0415
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake_cdll = object()
        lib_path = REPO_ROOT / "smoke_composition_from_file_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _RecordingDispatcher()

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake_cdll,
        ) as cdll_mock:
            img = AuroraImage.from_file(str(lib_path), disp, loader)

        cdll_mock.assert_called_once()
        self.assertEqual(loader.library_path, lib_path.resolve())
        self.assertIs(img.native_handle, "smoke_native_handle")
        self.assertEqual(img.source_path, str(lib_path))
        self.assertIs(img.dispatcher, disp)
        self.assertIs(img.library_loader, loader)
        self.assertEqual(len(disp.calls), 1)
        args, kwargs = disp.calls[0]
        self.assertEqual(kwargs, {})
        self.assertEqual(args[0], IMAGE_FROM_FILE)
        self.assertEqual(args[1], str(lib_path))
        self.assertIs(args[2], fake_cdll)

    def test_smoke_happy_path_from_bytes_composes_loader_and_dispatcher(self) -> None:
        from aurora.runtime.dispatch_tokens import IMAGE_FROM_BYTES  # noqa: PLC0415
        from aurora.runtime.image import AuroraImage  # noqa: PLC0415
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake_cdll = object()
        lib_path = REPO_ROOT / "smoke_composition_from_bytes_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _RecordingDispatcher()
        raw = b"\xff\xd8\xff"

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake_cdll,
        ) as cdll_mock:
            img = AuroraImage.from_bytes(raw, disp, loader)

        cdll_mock.assert_called_once()
        self.assertIs(img.native_handle, "smoke_native_handle")
        self.assertIsNone(img.source_path)
        self.assertEqual(len(disp.calls), 1)
        args, _kwargs = disp.calls[0]
        self.assertEqual(args[0], IMAGE_FROM_BYTES)
        self.assertEqual(args[1], raw)
        self.assertIs(args[2], fake_cdll)

    def test_smoke_loader_failure_is_image_creation_error_with_chain(self) -> None:
        from aurora.runtime.image import (  # noqa: PLC0415
            AuroraImage,
            ImageCreationError,
        )
        from aurora.runtime.shared_library_loader import (  # noqa: PLC0415
            SharedLibraryLoader,
            SharedLibraryLoadError,
        )

        lib_path = REPO_ROOT / "smoke_composition_loader_fail_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _RecordingDispatcher()
        boom = OSError("smoke fake CDLL failure")

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            side_effect=boom,
        ):
            with self.assertRaises(ImageCreationError) as ctx:
                AuroraImage.from_file(str(lib_path), disp, loader)

        self.assertIsInstance(ctx.exception.__cause__, SharedLibraryLoadError)
        self.assertIs(ctx.exception.__cause__.__cause__, boom)
        self.assertEqual(disp.calls, [])

    def test_smoke_dispatch_failure_is_image_creation_error_with_chain(self) -> None:
        from aurora.runtime.image import (  # noqa: PLC0415
            AuroraImage,
            ImageCreationError,
        )
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake_cdll = object()
        lib_path = REPO_ROOT / "smoke_composition_dispatch_fail_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _BoomDispatcher()

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake_cdll,
        ):
            with self.assertRaises(ImageCreationError) as ctx:
                AuroraImage.from_bytes(b"x", disp, loader)

        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)


class TestRuntimeSmokeAudioComposition(unittest.TestCase):
    """M19 — composed smoke for ``AuroraAudio`` (parallel to image M09)."""

    def test_smoke_happy_path_audio_from_file_composes_loader_and_dispatcher(self) -> None:
        from aurora.runtime.audio import AuroraAudio  # noqa: PLC0415
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake_cdll = object()
        lib_path = REPO_ROOT / "smoke_audio_composition_from_file_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _RecordingDispatcher()

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake_cdll,
        ) as cdll_mock:
            aud = AuroraAudio.from_file(str(lib_path), disp, loader)

        cdll_mock.assert_called_once()
        self.assertEqual(loader.library_path, lib_path.resolve())
        self.assertIs(aud.native_handle, "smoke_native_handle")
        self.assertEqual(aud.source_path, str(lib_path))
        self.assertIs(aud.dispatcher, disp)
        self.assertIs(aud.library_loader, loader)
        self.assertEqual(len(disp.calls), 1)
        args, kwargs = disp.calls[0]
        self.assertEqual(kwargs, {})
        self.assertEqual(args[0], AUDIO_FROM_FILE)
        self.assertEqual(args[1], str(lib_path))
        self.assertIs(args[2], fake_cdll)

    def test_smoke_happy_path_audio_from_bytes_composes_loader_and_dispatcher(self) -> None:
        from aurora.runtime.audio import AuroraAudio  # noqa: PLC0415
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_BYTES  # noqa: PLC0415
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake_cdll = object()
        lib_path = REPO_ROOT / "smoke_audio_composition_from_bytes_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _RecordingDispatcher()
        raw = b"\xff\xfb\x90"

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake_cdll,
        ) as cdll_mock:
            aud = AuroraAudio.from_bytes(raw, disp, loader)

        cdll_mock.assert_called_once()
        self.assertIs(aud.native_handle, "smoke_native_handle")
        self.assertIsNone(aud.source_path)
        self.assertEqual(len(disp.calls), 1)
        args, _kwargs = disp.calls[0]
        self.assertEqual(args[0], AUDIO_FROM_BYTES)
        self.assertEqual(args[1], raw)
        self.assertIs(args[2], fake_cdll)

    def test_smoke_audio_loader_failure_is_audio_creation_error_with_chain(self) -> None:
        from aurora.runtime.audio import (  # noqa: PLC0415
            AudioCreationError,
            AuroraAudio,
        )
        from aurora.runtime.shared_library_loader import (  # noqa: PLC0415
            SharedLibraryLoader,
            SharedLibraryLoadError,
        )

        lib_path = REPO_ROOT / "smoke_audio_composition_loader_fail_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _RecordingDispatcher()
        boom = OSError("smoke fake CDLL failure")

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            side_effect=boom,
        ):
            with self.assertRaises(AudioCreationError) as ctx:
                AuroraAudio.from_file(str(lib_path), disp, loader)

        self.assertIsInstance(ctx.exception.__cause__, SharedLibraryLoadError)
        self.assertIs(ctx.exception.__cause__.__cause__, boom)
        self.assertEqual(disp.calls, [])

    def test_smoke_audio_dispatch_failure_is_audio_creation_error_with_chain(self) -> None:
        from aurora.runtime.audio import (  # noqa: PLC0415
            AudioCreationError,
            AuroraAudio,
        )
        from aurora.runtime.shared_library_loader import SharedLibraryLoader  # noqa: PLC0415

        fake_cdll = object()
        lib_path = REPO_ROOT / "smoke_audio_composition_dispatch_fail_dummy.so"
        loader = SharedLibraryLoader(lib_path)
        disp = _BoomDispatcher()

        with mock.patch(
            "aurora.runtime.shared_library_loader.ctypes.CDLL",
            return_value=fake_cdll,
        ):
            with self.assertRaises(AudioCreationError) as ctx:
                AuroraAudio.from_bytes(b"x", disp, loader)

        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)


if __name__ == "__main__":
    unittest.main()
