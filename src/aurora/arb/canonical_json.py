"""Canonical JSON serialization for ARB v0.1 (``docs/aurora_run_bundle_v0_spec.md`` §5.2).

stdlib only; deterministic UTF-8 bytes with compact separators and sorted object keys.
"""

from __future__ import annotations

import json
from typing import Any


def _reject_floats(obj: object) -> None:
    """Reject Python ``float`` anywhere in the structure (spec §5.2 — no JSON floats for scores)."""
    if isinstance(obj, float):
        raise ValueError("ARB v0.1 JSON must not contain float values; use int, str, bool, or null")
    if isinstance(obj, dict):
        for v in obj.values():
            _reject_floats(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _reject_floats(v)


def canonicalize(obj: Any) -> bytes:
    """Serialize *obj* to canonical JSON bytes (UTF-8, LF, compact, sorted keys).

    Raises ``ValueError`` if the structure contains ``float`` values or non-finite numbers.
    """
    _reject_floats(obj)
    text = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return text.encode("utf-8")
