"""Concrete :class:`~aurora.runtime.dispatcher.Dispatcher` for bounded audio C API (M21–M22).

Routes ``AUDIO_FROM_FILE`` and ``AUDIO_FROM_BYTES`` through ``MpAudioClassifierCreate`` →
``MpAudioClassifierClassify`` → ``MpAudioClassifierCloseResult`` → ``MpAudioClassifierClose``
using ctypes signatures from :mod:`aurora.runtime.audio_native_bindings`.

**Does not prove:** WAV decode, graph correctness, or MediaPipe parity — see ``DEVELOPMENT.md``.
"""

from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Any

from .audio_native_bindings import (
    K_HOST_ENVIRONMENT_PYTHON,
    K_MP_AUDIO_RUNNING_MODE_AUDIO_CLIPS,
    K_MP_OK,
    AudioClassifierCApi,
    BaseOptionsC,
    ClassifierOptionsC,
    MpAudioClassifierOptionsC,
    MpAudioClassifierResultC,
    MpAudioDataC,
    bind_audio_classifier,
    free_error_message,
)
from .dispatch_tokens import AUDIO_FROM_BYTES, AUDIO_FROM_FILE


def _invoke_mp_status(lib: Any, fn: Any, *core_args: Any) -> int:
    """Call a C function that returns ``MpStatus`` and takes trailing ``char** error_msg``."""
    error_msg = ctypes.c_char_p()
    args = list(core_args) + [ctypes.byref(error_msg)]
    status = int(fn(*args))
    try:
        if status != K_MP_OK:
            detail = (
                error_msg.value.decode("utf-8", errors="replace")
                if error_msg.value
                else f"status {status}"
            )
            raise RuntimeError(detail)
        return status
    finally:
        free_error_message(lib, error_msg)


def _mp_audio_data_from_raw_octets(raw: bytes) -> tuple[MpAudioDataC, list[Any]]:
    """Build ``MpAudioData`` from raw octets (not a format decoder).

    Interprets leading octets as float32 lanes for structural binding tests only — same
    honesty posture as M21 file-backed path.
    """
    nbytes = len(raw)
    nfloats = nbytes // 4
    keepalive: list[Any] = []
    if nfloats == 0:
        buf = (ctypes.c_float * 1)(0.0)
        keepalive.append(buf)
        nfloats = 1
    else:
        buf = (ctypes.c_float * nfloats).from_buffer_copy(raw[: nfloats * 4])
        keepalive.append(buf)
    data = MpAudioDataC()
    data.num_channels = 1
    data.sample_rate = 16000.0
    data.audio_data = ctypes.cast(buf, ctypes.POINTER(ctypes.c_float))
    data.audio_data_size = nfloats * 4
    return data, keepalive


def _mp_audio_data_from_file(path: str) -> tuple[MpAudioDataC, list[Any]]:
    """Build ``MpAudioData`` from a file path (reads bytes then same raw-octet path)."""
    raw = Path(path).read_bytes()
    return _mp_audio_data_from_raw_octets(raw)


def _fill_classifier_options(
    model_asset_path: str,
    *,
    host_environment: int,
    host_system: int,
) -> tuple[MpAudioClassifierOptionsC, ctypes.c_char_p]:
    """Stack-allocated options struct with a stable model path pointer."""
    model_bytes = model_asset_path.encode("utf-8")
    path_ptr = ctypes.c_char_p(model_bytes)

    bo = BaseOptionsC()
    bo.model_asset_buffer = None
    bo.model_asset_buffer_count = 0
    bo.model_asset_path = path_ptr
    bo.delegate = 0
    bo.host_environment = host_environment
    bo.host_system = host_system
    bo.host_version = None

    co = ClassifierOptionsC()
    co.display_names_locale = None
    co.max_results = -1
    co.score_threshold = 0.0
    co.category_allowlist = None
    co.category_allowlist_count = 0
    co.category_denylist = None
    co.category_denylist_count = 0

    opts = MpAudioClassifierOptionsC()
    opts.base_options = bo
    opts.classifier_options = co
    opts.running_mode = K_MP_AUDIO_RUNNING_MODE_AUDIO_CLIPS
    opts.result_callback = None
    return opts, path_ptr


class NativeAudioDispatcher:
    """Dispatcher that invokes the Tasks AudioClassifier C API for audio clip tokens.

    The caller supplies a **model** path at construction time; ``dispatch``'s payload is the
    **audio** file path (``AUDIO_FROM_FILE``) or raw **bytes** (``AUDIO_FROM_BYTES``) per
    the first-party ``AuroraAudio`` contract.
    """

    __slots__ = (
        "_host_environment",
        "_host_system",
        "_model_asset_path",
    )

    def __init__(
        self,
        *,
        model_asset_path: str,
        host_environment: int = K_HOST_ENVIRONMENT_PYTHON,
        host_system: int = 0,
    ) -> None:
        self._model_asset_path = model_asset_path
        self._host_environment = host_environment
        self._host_system = host_system

    def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        """``dispatch(token, payload, lib)`` — same arity as :class:`AuroraAudio` seam."""
        if kwargs:
            raise TypeError("NativeAudioDispatcher.dispatch does not accept keyword arguments")
        if len(args) != 3:
            raise TypeError(
                "NativeAudioDispatcher.dispatch expected exactly 3 positional arguments "
                f"(token, payload, lib), got {len(args)}"
            )
        token, payload, lib = args
        api = bind_audio_classifier(lib)
        if token == AUDIO_FROM_BYTES:
            if not isinstance(payload, bytes):
                raise TypeError("AUDIO_FROM_BYTES payload must be bytes")
            return self._dispatch_bytes(api, lib, payload)
        if token == AUDIO_FROM_FILE:
            if not isinstance(payload, str):
                raise TypeError("AUDIO_FROM_FILE payload must be a str path")
            return self._dispatch_file(api, lib, payload)
        raise ValueError(
            "unsupported audio dispatch token for " f"NativeAudioDispatcher: {token!r}"
        )

    def _dispatch_file(self, api: AudioClassifierCApi, lib: Any, audio_path: str) -> dict[str, Any]:
        audio_data, _audio_keep = _mp_audio_data_from_file(audio_path)
        return self._dispatch_classify(api, lib, audio_data, kind="native_audio_file")

    def _dispatch_bytes(self, api: AudioClassifierCApi, lib: Any, raw: bytes) -> dict[str, Any]:
        audio_data, _audio_keep = _mp_audio_data_from_raw_octets(raw)
        return self._dispatch_classify(api, lib, audio_data, kind="native_audio_bytes")

    def _dispatch_classify(
        self,
        api: AudioClassifierCApi,
        lib: Any,
        audio_data: MpAudioDataC,
        *,
        kind: str,
    ) -> dict[str, Any]:
        opts, _path_keepalive = _fill_classifier_options(
            self._model_asset_path,
            host_environment=self._host_environment,
            host_system=self._host_system,
        )

        classifier = ctypes.c_void_p()
        _invoke_mp_status(
            lib,
            api.create,
            ctypes.byref(opts),
            ctypes.byref(classifier),
        )
        try:
            result = MpAudioClassifierResultC()
            try:
                _invoke_mp_status(
                    lib,
                    api.classify,
                    classifier,
                    ctypes.byref(audio_data),
                    ctypes.byref(result),
                )
                results_count = int(result.results_count)
            finally:
                api.close_result(ctypes.byref(result))
        finally:
            # Skip Close when Create left a null handle (defensive; tests may exercise this path).
            if classifier.value:
                _invoke_mp_status(lib, api.close, classifier)

        return {
            "kind": kind,
            "mp_status": K_MP_OK,
            "results_count": results_count,
        }


__all__ = ["NativeAudioDispatcher"]
