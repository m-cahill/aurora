"""Minimal ARB v0.1 offline/batch bundle reader (spec §3–§4).

Loads the minimal valid tree only. Does **not** verify hashes — use
:func:`aurora.arb.validator.validate_arb` separately.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aurora.arb.writer import _validate_minimal_manifest

# Paths relative to bundle root (spec §3).
_REQUIRED_FILES: tuple[str, ...] = (
    "manifest.json",
    "graph.yaml",
    "inputs/audio_index.json",
    "segments/segments.json",
    "predictions/predictions.json",
    "hashes/sha256_manifest.json",
    "hashes/root_hash.txt",
)


@dataclass(frozen=True, slots=True)
class ArbBundle:
    """Loaded minimal v0.1 ARB contents (eager; no hash verification)."""

    manifest: dict[str, Any]
    graph_yaml: str
    audio_index: dict[str, Any]
    segments: dict[str, Any]
    predictions: dict[str, Any]
    sha256_manifest: dict[str, Any]
    root_hash: str


def _read_json_object(path: Path, *, rel: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read {rel}: {exc}") from exc
    if text.startswith("\ufeff"):
        raise ValueError(f"{rel} must be UTF-8 without BOM (spec §5.1)")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{rel} is not valid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"{rel} must be a JSON object")
    return obj


def _parse_root_hash(path: Path, *, rel: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read {rel}: {exc}") from exc
    lines = text.splitlines()
    if len(lines) != 1:
        raise ValueError(f"{rel} must contain exactly one line (spec §6.5), got {len(lines)}")
    line = lines[0]
    if len(line) != 64:
        raise ValueError(f"{rel} must be 64 lowercase hex characters, got length {len(line)}")
    if not all(c in "0123456789abcdef" for c in line):
        raise ValueError(f"{rel} must be lowercase hexadecimal (spec §6.5)")
    return line


def read_arb(bundle_root: str | Path) -> ArbBundle:
    """Load a minimal valid ARB v0.1 directory tree from *bundle_root*.

    Parses JSON per :func:`json.loads` (UTF-8, no BOM). Validates ``manifest.json`` with the
    same rules as :func:`aurora.arb.writer.write_arb`. Does **not** verify ``sha256_manifest``
    or ``root_hash`` against file contents — use :func:`aurora.arb.validator.validate_arb` for
    integrity checks.
    """
    root = Path(bundle_root).resolve()
    if not root.is_dir():
        raise ValueError(f"bundle root is not a directory: {root}")

    for rel in _REQUIRED_FILES:
        p = root / rel
        if not p.is_file():
            raise ValueError(f"missing required ARB file: {rel}")

    manifest = _read_json_object(root / "manifest.json", rel="manifest.json")
    _validate_minimal_manifest(manifest)

    graph_yaml = (root / "graph.yaml").read_text(encoding="utf-8")
    if graph_yaml.startswith("\ufeff"):
        raise ValueError("graph.yaml must be UTF-8 without BOM (spec §5.1)")

    audio_index = _read_json_object(
        root / "inputs" / "audio_index.json",
        rel="inputs/audio_index.json",
    )
    segments = _read_json_object(root / "segments" / "segments.json", rel="segments/segments.json")
    predictions = _read_json_object(
        root / "predictions" / "predictions.json",
        rel="predictions/predictions.json",
    )
    sha256_manifest = _read_json_object(
        root / "hashes" / "sha256_manifest.json",
        rel="hashes/sha256_manifest.json",
    )
    root_hash = _parse_root_hash(root / "hashes" / "root_hash.txt", rel="hashes/root_hash.txt")

    return ArbBundle(
        manifest=dict(manifest),
        graph_yaml=graph_yaml,
        audio_index=dict(audio_index),
        segments=dict(segments),
        predictions=dict(predictions),
        sha256_manifest=dict(sha256_manifest),
        root_hash=root_hash,
    )
