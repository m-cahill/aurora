"""ARB v0.1 bundle integrity and minimal semantic validation.

Normative rules: ``docs/aurora_run_bundle_v0_spec.md`` §3–§6.

Separate from :func:`aurora.arb.reader.read_arb` — loading does **not** imply verification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aurora.arb.canonical_json import canonicalize
from aurora.arb.hasher import compute_root_hash, sha256_hex
from aurora.arb.reader import _REQUIRED_FILES, _parse_root_hash
from aurora.arb.writer import _PAYLOAD_PATHS_ORDERED, _validate_minimal_manifest


class ArbValidationError(Exception):
    """Raised when an ARB v0.1 bundle fails :func:`validate_arb` checks."""


def _raise(msg: str, *, cause: BaseException | None = None) -> None:
    if cause is not None:
        raise ArbValidationError(msg) from cause
    raise ArbValidationError(msg)


def _read_utf8_no_bom(path: Path, *, rel: str) -> bytes:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        _raise(f"cannot read {rel}: {exc}", cause=exc)
    if raw.startswith(b"\xef\xbb\xbf"):
        _raise(f"{rel} must be UTF-8 without BOM (spec §5.1)")
    return raw


def _json_object_from_bytes(data: bytes, *, rel: str) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        _raise(f"{rel} must be valid UTF-8 (spec §5.1)", cause=exc)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        _raise(f"{rel} is not valid JSON: {exc}", cause=exc)
    if not isinstance(obj, dict):
        _raise(f"{rel} must be a JSON object")
    return obj


def _assert_canonical_json_bytes(obj: dict[str, Any], raw: bytes, *, rel: str) -> None:
    try:
        canon = canonicalize(obj)
    except ValueError as exc:
        _raise(f"{rel} is not valid canonical JSON content: {exc}", cause=exc)
    if canon != raw:
        _raise(f"{rel} is not canonical JSON on disk (spec §5.2)")


def _validate_sha256_manifest_object(obj: dict[str, Any]) -> list[dict[str, str]]:
    if set(obj.keys()) != {"arb_version", "files"}:
        _raise(
            "hashes/sha256_manifest.json must contain exactly keys "
            "'arb_version' and 'files' (spec §6.4)"
        )
    if obj.get("arb_version") != "0.1":
        _raise('hashes/sha256_manifest.json "arb_version" must be "0.1" (spec §6.4)')
    files_raw = obj.get("files")
    if not isinstance(files_raw, list):
        _raise('hashes/sha256_manifest.json "files" must be an array (spec §6.4)')
    if len(files_raw) != len(_PAYLOAD_PATHS_ORDERED):
        _raise(
            "hashes/sha256_manifest.json must list exactly "
            f"{len(_PAYLOAD_PATHS_ORDERED)} payload paths for minimal v0.1 ARB (spec §6.4)"
        )
    out: list[dict[str, str]] = []
    for i, item in enumerate(files_raw):
        if not isinstance(item, dict):
            _raise(f'hashes/sha256_manifest.json "files"[{i}] must be an object')
        if set(item.keys()) != {"path", "sha256"}:
            _raise(
                f'hashes/sha256_manifest.json "files"[{i}] must have exactly '
                '"path" and "sha256" keys (spec §6.4)'
            )
        path = item.get("path")
        digest = item.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            _raise(f'hashes/sha256_manifest.json "files"[{i}] path and sha256 must be strings')
        if len(digest) != 64 or not all(c in "0123456789abcdef" for c in digest):
            _raise(
                f'hashes/sha256_manifest.json "files"[{i}] "sha256" must be 64 lowercase '
                "hex characters (spec §6.1)"
            )
        out.append({"path": path, "sha256": digest})
    paths = [e["path"] for e in out]
    if paths != list(_PAYLOAD_PATHS_ORDERED):
        _raise(
            "hashes/sha256_manifest.json files[] must be sorted by path ascending "
            f"and match the minimal v0.1 payload set (spec §6.4); expected "
            f"{list(_PAYLOAD_PATHS_ORDERED)}, got {paths}"
        )
    return out


def validate_arb(bundle_root: str | Path) -> None:
    """Verify ARB v0.1 bundle integrity and minimal semantic consistency.

    On success, returns ``None``. On any failure, raises :class:`ArbValidationError`.

    Proves:

    - Required on-disk layout for minimal v0.1 (spec §3).
    - ``manifest.json`` passes the same minimal checks as :func:`aurora.arb.writer.write_arb`
      and is canonical JSON (spec §5.2).
    - Other hashed JSON payloads are canonical JSON on disk (spec §5.2).
    - ``hashes/sha256_manifest.json`` matches the v0.1 structural contract (spec §6.4) and is
      canonical JSON on disk.
    - Per-file SHA-256 entries match recomputed digests from on-disk bytes (spec §6.3).
    - ``hashes/root_hash.txt`` equals SHA-256 of the on-disk bytes of
      ``hashes/sha256_manifest.json`` (spec §6.5).

    Does **not** change or replace :func:`aurora.arb.reader.read_arb` — callers that only load
    bundles do not implicitly validate.
    """
    root = Path(bundle_root).resolve()
    if not root.is_dir():
        _raise(f"bundle root is not a directory: {root}")

    for rel in _REQUIRED_FILES:
        if not (root / rel).is_file():
            _raise(f"missing required ARB file: {rel}")

    # --- manifest (§4, §5.2) ---
    rel_m = "manifest.json"
    manifest_raw = _read_utf8_no_bom(root / rel_m, rel=rel_m)
    manifest = _json_object_from_bytes(manifest_raw, rel=rel_m)
    try:
        _validate_minimal_manifest(manifest)
    except ValueError as exc:
        _raise(str(exc), cause=exc)
    _assert_canonical_json_bytes(manifest, manifest_raw, rel=rel_m)

    # --- graph.yaml (raw bytes hash; §5.3) ---
    rel_g = "graph.yaml"
    graph_raw = _read_utf8_no_bom(root / rel_g, rel=rel_g)

    # --- nested JSON payloads (§5.2) ---
    rel_in = "inputs/audio_index.json"
    inputs_raw = _read_utf8_no_bom(root / rel_in, rel=rel_in)
    inputs_obj = _json_object_from_bytes(inputs_raw, rel=rel_in)
    _assert_canonical_json_bytes(inputs_obj, inputs_raw, rel=rel_in)

    rel_seg = "segments/segments.json"
    seg_raw = _read_utf8_no_bom(root / rel_seg, rel=rel_seg)
    seg_obj = _json_object_from_bytes(seg_raw, rel=rel_seg)
    _assert_canonical_json_bytes(seg_obj, seg_raw, rel=rel_seg)

    rel_pred = "predictions/predictions.json"
    pred_raw = _read_utf8_no_bom(root / rel_pred, rel=rel_pred)
    pred_obj = _json_object_from_bytes(pred_raw, rel=rel_pred)
    _assert_canonical_json_bytes(pred_obj, pred_raw, rel=rel_pred)

    # --- sha256 manifest (§6.4) ---
    rel_h = "hashes/sha256_manifest.json"
    sha_raw = _read_utf8_no_bom(root / rel_h, rel=rel_h)
    sha_obj = _json_object_from_bytes(sha_raw, rel=rel_h)
    entries = _validate_sha256_manifest_object(sha_obj)
    _assert_canonical_json_bytes(sha_obj, sha_raw, rel=rel_h)

    # --- per-file digest agreement (§6.3) ---
    by_path: dict[str, bytes] = {
        "manifest.json": manifest_raw,
        "graph.yaml": graph_raw,
        "inputs/audio_index.json": inputs_raw,
        "segments/segments.json": seg_raw,
        "predictions/predictions.json": pred_raw,
    }
    for entry in entries:
        p = entry["path"]
        expected_hex = entry["sha256"]
        data = by_path[p]
        got = sha256_hex(data)
        if got != expected_hex:
            _raise(
                f"SHA-256 mismatch for {p}: manifest lists {expected_hex}, "
                f"recomputed {got} (spec §6.3)"
            )

    # --- root hash (§6.5) ---
    rel_r = "hashes/root_hash.txt"
    try:
        declared = _parse_root_hash(root / rel_r, rel=rel_r)
    except ValueError as exc:
        _raise(str(exc), cause=exc)
    computed = compute_root_hash(sha_raw)
    if declared != computed:
        _raise(
            f"root hash mismatch: {rel_r} declares {declared}, "
            f"SHA-256 of {rel_h} is {computed} (spec §6.5)"
        )
