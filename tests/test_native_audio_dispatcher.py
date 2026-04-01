"""Tests for M21 native audio dispatcher and ctypes bindings (stdlib unittest).

Uses in-process fake callables attached to a library stand-in — no real Tasks binary.
"""

from __future__ import annotations

import ctypes
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _make_fake_lib() -> Any:
    """Object with MpAudioClassifier* attributes for :func:`bind_audio_classifier`."""
    from aurora.runtime.audio_native_bindings import MpAudioClassifierResultC  # noqa: PLC0415

    lib = mock.Mock()
    lib.MpErrorFree = mock.Mock()

    def _create(opts: Any, out: Any, err: Any) -> int:
        out_ptr = ctypes.cast(out, ctypes.POINTER(ctypes.c_void_p))
        out_ptr.contents.value = 99
        return 0

    def _classify(cls: Any, data: Any, res: Any, err: Any) -> int:
        res_ptr = ctypes.cast(res, ctypes.POINTER(MpAudioClassifierResultC))
        res_ptr.contents.results_count = 3
        return 0

    def _close_result(res: Any) -> None:
        return None

    def _close(cls: Any, err: Any) -> int:
        return 0

    lib.MpAudioClassifierCreate = _create
    lib.MpAudioClassifierClassify = _classify
    lib.MpAudioClassifierCloseResult = _close_result
    lib.MpAudioClassifierClose = _close
    return lib


class _CLikeFunc:
    """Minimal stand-in for a ``CDLL`` function pointer (has ``argtypes`` / ``restype``)."""

    argtypes: list[Any] | None = None
    restype: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> int:
        return 0


class TestAudioNativeBindings(unittest.TestCase):
    def test_apply_ctypes_signature_sets_when_argtypes_attr_exists(self) -> None:
        from aurora.runtime.audio_native_bindings import (  # noqa: PLC0415
            _apply_ctypes_signature,
        )

        fn = _CLikeFunc()
        _apply_ctypes_signature(fn, [ctypes.c_int], ctypes.c_int)
        self.assertEqual(fn.argtypes, [ctypes.c_int])
        self.assertEqual(fn.restype, ctypes.c_int)

    def test_bind_sets_argtypes_and_restype(self) -> None:
        from aurora.runtime.audio_native_bindings import bind_audio_classifier  # noqa: PLC0415

        lib = _make_fake_lib()
        api = bind_audio_classifier(lib)
        # Plain Python fakes have no ``argtypes``; CDLL-backed functions do.
        if hasattr(api.create, "restype"):
            self.assertEqual(api.create.restype, ctypes.c_int)
            self.assertEqual(api.classify.restype, ctypes.c_int)
            self.assertIsNone(api.close_result.restype)
            self.assertEqual(api.close.restype, ctypes.c_int)
        else:
            self.assertTrue(callable(api.create))
            self.assertTrue(callable(api.classify))

    def test_bind_sets_signatures_on_c_like_symbols(self) -> None:
        from aurora.runtime.audio_native_bindings import bind_audio_classifier  # noqa: PLC0415

        lib = mock.Mock()
        lib.MpAudioClassifierCreate = _CLikeFunc()
        lib.MpAudioClassifierClassify = _CLikeFunc()
        lib.MpAudioClassifierCloseResult = _CLikeFunc()
        lib.MpAudioClassifierClose = _CLikeFunc()
        api = bind_audio_classifier(lib)
        self.assertIsNotNone(api.create.argtypes)
        self.assertEqual(api.create.restype, ctypes.c_int)

    def test_free_error_message_calls_mp_error_free_when_present(self) -> None:
        from aurora.runtime.audio_native_bindings import free_error_message  # noqa: PLC0415

        lib = mock.Mock()
        err = ctypes.c_char_p(b"oops")
        free_error_message(lib, err)
        lib.MpErrorFree.assert_called_once()

    def test_free_error_message_noops_without_value(self) -> None:
        from aurora.runtime.audio_native_bindings import free_error_message  # noqa: PLC0415

        lib = mock.Mock()
        err = ctypes.c_char_p()
        free_error_message(lib, err)
        lib.MpErrorFree.assert_not_called()

    def test_free_error_message_noops_when_symbol_missing(self) -> None:
        from aurora.runtime.audio_native_bindings import free_error_message  # noqa: PLC0415

        lib = mock.Mock(spec=[])  # no MpErrorFree
        err = ctypes.c_char_p(b"x")
        free_error_message(lib, err)


class TestNativeAudioDispatcher(unittest.TestCase):
    def test_dispatch_success_shape(self) -> None:
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"\x00" * 8)
            tmp_path = tmp.name
        try:
            disp = NativeAudioDispatcher(model_asset_path="/models/x.tflite")
            lib = _make_fake_lib()
            out = disp.dispatch(AUDIO_FROM_FILE, tmp_path, lib)
            self.assertEqual(out["kind"], "native_audio_file")
            self.assertEqual(out["results_count"], 3)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_dispatch_rejects_kwargs(self) -> None:
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        disp = NativeAudioDispatcher(model_asset_path="m.tflite")
        with self.assertRaises(TypeError):
            disp.dispatch(AUDIO_FROM_FILE, "p", _make_fake_lib(), bad=True)

    def test_dispatch_rejects_wrong_arity(self) -> None:
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        disp = NativeAudioDispatcher(model_asset_path="m.tflite")
        with self.assertRaises(TypeError):
            disp.dispatch("only_one")

    def test_audio_from_bytes_deferred(self) -> None:
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_BYTES  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import (  # noqa: PLC0415
            AudioNativeBytesDeferredError,
            NativeAudioDispatcher,
        )

        disp = NativeAudioDispatcher(model_asset_path="m.tflite")
        with self.assertRaises(AudioNativeBytesDeferredError):
            disp.dispatch(AUDIO_FROM_BYTES, b"x", _make_fake_lib())

    def test_unknown_token(self) -> None:
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        disp = NativeAudioDispatcher(model_asset_path="m.tflite")
        with self.assertRaises(ValueError):
            disp.dispatch("not_a_token", "p", _make_fake_lib())

    def test_payload_must_be_str(self) -> None:
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        disp = NativeAudioDispatcher(model_asset_path="m.tflite")
        with self.assertRaises(TypeError):
            disp.dispatch(AUDIO_FROM_FILE, 123, _make_fake_lib())

    def test_invoke_status_raises_on_non_ok(self) -> None:
        from aurora.runtime.native_audio_dispatcher import _invoke_mp_status  # noqa: PLC0415

        def _fail(*args: Any, **kwargs: Any) -> int:
            return 99

        lib = mock.Mock()
        with self.assertRaises(RuntimeError) as ctx:
            _invoke_mp_status(lib, _fail)
        self.assertIn("status 99", str(ctx.exception))

    def test_invoke_status_success(self) -> None:
        from aurora.runtime.audio_native_bindings import K_MP_OK  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import _invoke_mp_status  # noqa: PLC0415

        def _ok(*args: Any, **kwargs: Any) -> int:
            return 0

        lib = mock.Mock()
        self.assertEqual(_invoke_mp_status(lib, _ok), K_MP_OK)

    def test_mp_audio_data_empty_file(self) -> None:
        from aurora.runtime.native_audio_dispatcher import _mp_audio_data_from_file  # noqa: PLC0415

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        try:
            data, keep = _mp_audio_data_from_file(tmp_path)
            self.assertEqual(data.num_channels, 1)
            self.assertEqual(data.audio_data_size, 4)
            self.assertEqual(len(keep), 1)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_aurora_audio_from_file_with_native_dispatcher(self) -> None:
        from aurora.runtime.audio import AuroraAudio  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"\x00" * 4)
            audio_path = tmp.name
        try:
            disp = NativeAudioDispatcher(model_asset_path="model.tflite")
            loader = mock.Mock()
            loader.shared_library.return_value = _make_fake_lib()
            aud = AuroraAudio.from_file(audio_path, disp, loader)
            self.assertEqual(aud.native_handle["results_count"], 3)
        finally:
            Path(audio_path).unlink(missing_ok=True)

    def test_close_skipped_when_classifier_handle_is_null(self) -> None:
        """Create returns OK but leaves the out-pointer unset — Close must not run."""
        from aurora.runtime.audio_native_bindings import MpAudioClassifierResultC  # noqa: PLC0415
        from aurora.runtime.dispatch_tokens import AUDIO_FROM_FILE  # noqa: PLC0415
        from aurora.runtime.native_audio_dispatcher import NativeAudioDispatcher  # noqa: PLC0415

        lib = mock.Mock()
        close_calls = 0

        def _create_ok_no_handle(opts: Any, out: Any, err: Any) -> int:
            return 0

        def _classify_ok(cls: Any, data: Any, res: Any, err: Any) -> int:
            res_ptr = ctypes.cast(res, ctypes.POINTER(MpAudioClassifierResultC))
            res_ptr.contents.results_count = 0
            return 0

        def _close_result(res: Any) -> None:
            return None

        def _close_track(cls: Any, err: Any) -> int:
            nonlocal close_calls
            close_calls += 1
            return 0

        lib.MpAudioClassifierCreate = _create_ok_no_handle
        lib.MpAudioClassifierClassify = _classify_ok
        lib.MpAudioClassifierCloseResult = _close_result
        lib.MpAudioClassifierClose = _close_track
        lib.MpErrorFree = mock.Mock()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"\x00\x00\x00\x00")
            tmp_path = tmp.name
        try:
            disp = NativeAudioDispatcher(model_asset_path="m.tflite")
            disp.dispatch(AUDIO_FROM_FILE, tmp_path, lib)
            self.assertEqual(close_calls, 0)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_aurora_audio_from_bytes_still_deferred(self) -> None:
        from aurora.runtime.audio import (  # noqa: PLC0415
            AudioCreationError,
            AuroraAudio,
        )
        from aurora.runtime.native_audio_dispatcher import (  # noqa: PLC0415
            AudioNativeBytesDeferredError,
            NativeAudioDispatcher,
        )

        disp = NativeAudioDispatcher(model_asset_path="m.tflite")
        loader = mock.Mock()
        loader.shared_library.return_value = _make_fake_lib()
        with self.assertRaises(AudioCreationError) as ctx:
            AuroraAudio.from_bytes(b"\x00\x01", disp, loader)
        self.assertIsInstance(ctx.exception.__cause__, AudioNativeBytesDeferredError)


if __name__ == "__main__":
    unittest.main()
