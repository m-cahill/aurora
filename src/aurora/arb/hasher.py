"""SHA-256 helpers for ARB v0.1 (``docs/aurora_run_bundle_v0_spec.md`` §6)."""

from __future__ import annotations

import hashlib


def sha256_hex(data: bytes) -> str:
    """Return lowercase hex SHA-256 digest of *data* (64 characters)."""
    return hashlib.sha256(data).hexdigest()


def compute_root_hash(sha256_manifest_json_bytes: bytes) -> str:
    """Bundle root hash: SHA-256 hex of canonical ``hashes/sha256_manifest.json`` (§6.5)."""
    return sha256_hex(sha256_manifest_json_bytes)
