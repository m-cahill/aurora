"""Minimal ARB v0.1 offline/batch bundle writer (spec §3–§6)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aurora.arb.canonical_json import canonicalize
from aurora.arb.hasher import compute_root_hash, sha256_hex

# Relative paths included in hashes/sha256_manifest.json for minimal valid ARBs (§6.2, §6.4).
_PAYLOAD_PATHS_ORDERED = (
    "graph.yaml",
    "inputs/audio_index.json",
    "manifest.json",
    "predictions/predictions.json",
    "segments/segments.json",
)

_REQUIRED_MANIFEST_KEYS: frozenset[str] = frozenset(
    (
        "arb_version",
        "bundle_id",
        "created_utc",
        "graph_spec_path",
        "hash_manifest_path",
        "input_manifest_path",
        "root_hash_path",
        "runtime_mode",
    )
)

_MINIMAL_PATH_VALUES: dict[str, str] = {
    "graph_spec_path": "graph.yaml",
    "input_manifest_path": "inputs/audio_index.json",
    "hash_manifest_path": "hashes/sha256_manifest.json",
    "root_hash_path": "hashes/root_hash.txt",
}


def _normalize_graph_yaml_to_bytes(graph_yaml: str) -> bytes:
    """UTF-8, LF only (§5.1, §5.3)."""
    text = graph_yaml.replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("utf-8")


def _validate_minimal_manifest(manifest: dict[str, Any]) -> None:
    missing = _REQUIRED_MANIFEST_KEYS - manifest.keys()
    if missing:
        raise ValueError(f"manifest.json missing required keys: {sorted(missing)}")
    extra = set(manifest.keys()) - _REQUIRED_MANIFEST_KEYS
    if extra:
        raise ValueError(f"manifest.json has unexpected keys for minimal ARB: {sorted(extra)}")
    if manifest.get("arb_version") != "0.1":
        raise ValueError('manifest "arb_version" must be "0.1" for ARB v0.1')
    if manifest.get("runtime_mode") != "offline_batch":
        raise ValueError(
            'manifest "runtime_mode" must be "offline_batch" for normative v0.1 offline/batch'
        )
    for key, expected in _MINIMAL_PATH_VALUES.items():
        if manifest.get(key) != expected:
            raise ValueError(f'manifest "{key}" must be "{expected}" for minimal valid ARB v0.1')


def write_arb(
    dest: Path,
    *,
    manifest: dict[str, Any],
    graph_yaml: str,
    inputs: dict[str, Any],
    segments: dict[str, Any],
    predictions: dict[str, Any],
) -> str:
    """Write a minimal valid ARB v0.1 directory tree under *dest*; return bundle root hash (hex).

    Does not read existing files. Overwrites paths under *dest* as needed.
    """
    _validate_minimal_manifest(manifest)

    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "inputs").mkdir(parents=True, exist_ok=True)
    (dest / "segments").mkdir(parents=True, exist_ok=True)
    (dest / "predictions").mkdir(parents=True, exist_ok=True)
    (dest / "hashes").mkdir(parents=True, exist_ok=True)

    manifest_bytes = canonicalize(manifest)
    graph_bytes = _normalize_graph_yaml_to_bytes(graph_yaml)
    inputs_bytes = canonicalize(inputs)
    segments_bytes = canonicalize(segments)
    predictions_bytes = canonicalize(predictions)

    (dest / "manifest.json").write_bytes(manifest_bytes)
    (dest / "graph.yaml").write_bytes(graph_bytes)
    (dest / "inputs" / "audio_index.json").write_bytes(inputs_bytes)
    (dest / "segments" / "segments.json").write_bytes(segments_bytes)
    (dest / "predictions" / "predictions.json").write_bytes(predictions_bytes)

    digests: dict[str, str] = {
        "manifest.json": sha256_hex(manifest_bytes),
        "graph.yaml": sha256_hex(graph_bytes),
        "inputs/audio_index.json": sha256_hex(inputs_bytes),
        "segments/segments.json": sha256_hex(segments_bytes),
        "predictions/predictions.json": sha256_hex(predictions_bytes),
    }

    files_arr = [{"path": p, "sha256": digests[p]} for p in _PAYLOAD_PATHS_ORDERED]
    sha256_manifest_obj = {"arb_version": "0.1", "files": files_arr}
    sha256_manifest_bytes = canonicalize(sha256_manifest_obj)
    (dest / "hashes" / "sha256_manifest.json").write_bytes(sha256_manifest_bytes)

    root = compute_root_hash(sha256_manifest_bytes)
    (dest / "hashes" / "root_hash.txt").write_bytes((root + "\n").encode("utf-8"))
    return root
