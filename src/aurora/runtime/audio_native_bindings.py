"""Internal ctypes binding surface for Tasks AudioClassifier C API (M21).

Defines struct layouts and symbol names aligned with the upstream C headers
described in ``docs/audio_classifier_graph_mapping.md``. This module does **not**
import ``mediapipe`` and does **not** copy upstream Python sources.

**Does not prove:** decode correctness, graph execution, or MediaPipe application
parity — only the in-repo binding surface used by
:class:`~aurora.runtime.native_audio_dispatcher.NativeAudioDispatcher`.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import Any

# MpStatus / running mode values — aligned with mediapipe/tasks/c/core/mp_status.h
# and mediapipe/tasks/c/audio/core/common.h (evidence via read-only clone).
K_MP_OK = 0
K_MP_AUDIO_RUNNING_MODE_AUDIO_CLIPS = 1

# Default host hints for Tasks Python (evidence: mediapipe BaseOptionsC usage).
K_HOST_ENVIRONMENT_PYTHON = 3


class BaseOptionsC(ctypes.Structure):
    """``struct BaseOptions`` — minimal layout for model path wiring."""

    _fields_ = [
        ("model_asset_buffer", ctypes.c_char_p),
        ("model_asset_buffer_count", ctypes.c_uint),
        ("model_asset_path", ctypes.c_char_p),
        ("delegate", ctypes.c_int),
        ("host_environment", ctypes.c_int),
        ("host_system", ctypes.c_int),
        ("host_version", ctypes.c_char_p),
    ]


class ClassifierOptionsC(ctypes.Structure):
    """``struct ClassifierOptions`` — defaults match unconfigured task options."""

    _fields_ = [
        ("display_names_locale", ctypes.c_char_p),
        ("max_results", ctypes.c_int),
        ("score_threshold", ctypes.c_float),
        ("category_allowlist", ctypes.POINTER(ctypes.c_char_p)),
        ("category_allowlist_count", ctypes.c_uint32),
        ("category_denylist", ctypes.POINTER(ctypes.c_char_p)),
        ("category_denylist_count", ctypes.c_uint32),
    ]


class MpAudioClassifierOptionsC(ctypes.Structure):
    """``struct MpAudioClassifierOptions`` — audio clips mode, no async callback."""

    _fields_ = [
        ("base_options", BaseOptionsC),
        ("classifier_options", ClassifierOptionsC),
        ("running_mode", ctypes.c_int),
        ("result_callback", ctypes.c_void_p),
    ]


class MpAudioDataC(ctypes.Structure):
    """``struct MpAudioData`` — row-major float samples."""

    _fields_ = [
        ("num_channels", ctypes.c_int),
        ("sample_rate", ctypes.c_double),
        ("audio_data", ctypes.POINTER(ctypes.c_float)),
        ("audio_data_size", ctypes.c_size_t),
    ]


class MpAudioClassifierResultC(ctypes.Structure):
    """``MpAudioClassifierResult`` — opaque ``results`` pointer at ctypes boundary."""

    _fields_ = [
        ("results", ctypes.c_void_p),
        ("results_count", ctypes.c_int),
    ]


@dataclass(frozen=True, slots=True)
class AudioClassifierCApi:
    """Resolved C API entry points and their ctypes signatures."""

    create: Any
    classify: Any
    close_result: Any
    close: Any


def free_error_message(lib: Any, error_msg: ctypes.c_char_p) -> None:
    """Release a C API error string using ``MpErrorFree`` when available."""
    if error_msg.value is None:
        return
    fn = getattr(lib, "MpErrorFree", None)
    if fn is None:
        return
    fn(error_msg)


def _apply_ctypes_signature(fn: Any, argtypes: list[Any], restype: Any) -> None:
    """Set ``argtypes`` / ``restype`` when ``fn`` is a loaded C function (e.g. ``CDLL``)."""
    if not hasattr(fn, "argtypes"):
        return
    fn.argtypes = argtypes
    fn.restype = restype


def bind_audio_classifier(lib: Any) -> AudioClassifierCApi:
    """Attach ``MpAudioClassifier*`` symbols to ``lib`` and return typed callables.

    ``lib`` is typically a ``ctypes.CDLL`` instance (``LibraryLoader.shared_library()``).
    Plain Python callables (used in tests) are returned unchanged so they are not mistaken
    for C functions with a ``.argtypes`` surface.
    """
    create = lib.MpAudioClassifierCreate
    _apply_ctypes_signature(
        create,
        [
            ctypes.POINTER(MpAudioClassifierOptionsC),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_char_p),
        ],
        ctypes.c_int,
    )

    classify = lib.MpAudioClassifierClassify
    _apply_ctypes_signature(
        classify,
        [
            ctypes.c_void_p,
            ctypes.POINTER(MpAudioDataC),
            ctypes.POINTER(MpAudioClassifierResultC),
            ctypes.POINTER(ctypes.c_char_p),
        ],
        ctypes.c_int,
    )

    close_result = lib.MpAudioClassifierCloseResult
    _apply_ctypes_signature(
        close_result,
        [ctypes.POINTER(MpAudioClassifierResultC)],
        None,
    )

    close = lib.MpAudioClassifierClose
    _apply_ctypes_signature(
        close,
        [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p)],
        ctypes.c_int,
    )

    return AudioClassifierCApi(
        create=create,
        classify=classify,
        close_result=close_result,
        close=close,
    )


__all__ = [
    "AudioClassifierCApi",
    "BaseOptionsC",
    "ClassifierOptionsC",
    "K_HOST_ENVIRONMENT_PYTHON",
    "K_MP_AUDIO_RUNNING_MODE_AUDIO_CLIPS",
    "K_MP_OK",
    "MpAudioClassifierOptionsC",
    "MpAudioClassifierResultC",
    "MpAudioDataC",
    "bind_audio_classifier",
    "free_error_message",
]
