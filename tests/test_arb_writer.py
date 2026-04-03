"""Tests for ``aurora.arb.writer`` and spec §8 reference fixture (stdlib unittest)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aurora.arb import write_arb
from aurora.arb.hasher import sha256_hex

# --- ARB v0.1 spec §8 illustrative example (``docs/aurora_run_bundle_v0_spec.md``) ---

SPEC8_GRAPH_YAML = """# Example graph stub — content is hashed as raw bytes in v0.1
version: 0
pipeline: audio_classifier_stub
"""

SPEC8_MANIFEST: dict[str, str] = {
    "arb_version": "0.1",
    "bundle_id": "example-arb-0001",
    "created_utc": "2026-04-02T12:00:00Z",
    "graph_spec_path": "graph.yaml",
    "hash_manifest_path": "hashes/sha256_manifest.json",
    "input_manifest_path": "inputs/audio_index.json",
    "root_hash_path": "hashes/root_hash.txt",
    "runtime_mode": "offline_batch",
}

SPEC8_INPUTS: dict[str, object] = {
    "entries": [
        {
            "duration_ms": "5000",
            "path": "inputs/example.wav",
            "sample_rate_hz": "16000",
        }
    ]
}

SPEC8_SEGMENTS: dict[str, object] = {
    "segments": [
        {
            "end_ms": "5000",
            "id": "seg-001",
            "input_path": "inputs/example.wav",
            "start_ms": "0",
        }
    ]
}

SPEC8_PREDICTIONS: dict[str, object] = {
    "predictions": [
        {
            "label": "species_a",
            "score": "0.91",
            "segment_id": "seg-001",
        }
    ]
}

# Pinned SHA-256 digests for the §8 example (canonical JSON + graph raw bytes per spec §6).
SPEC8_DIGEST_MANIFEST_JSON = (
    "5aa16205f514f09fb71c818e3795f60c2c898cab09c9d31c0b3c60c7b6770f69"
)
SPEC8_DIGEST_GRAPH_YAML = (
    "5f2ff103499c891c980b2eb900bbd465e3c2d37cfa8be88d280702f07f975664"
)
SPEC8_DIGEST_INPUTS_JSON = (
    "c692bdbe68b6a9aebf773f85e4b965ddc4c1c2863b7c1203137486de47e3b694"
)
SPEC8_DIGEST_SEGMENTS_JSON = (
    "b5baab24d3b1867645f8608a1b469b42c14c8f5ed161ca5e15060a530ad9452b"
)
SPEC8_DIGEST_PREDICTIONS_JSON = (
    "e696e257d9afbf865ca62c3d4f732d0ba98a287d7ead463a45981133360264ba"
)
SPEC8_ROOT_HASH = "64fab811b97d21595e611b197d322dba6f0ed9901317e984e595f43de1bf9199"


class TestArbWriter(unittest.TestCase):
    def test_spec8_pinned_digests_and_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = write_arb(
                root,
                manifest=dict(SPEC8_MANIFEST),
                graph_yaml=SPEC8_GRAPH_YAML,
                inputs=dict(SPEC8_INPUTS),
                segments=dict(SPEC8_SEGMENTS),
                predictions=dict(SPEC8_PREDICTIONS),
            )
            self.assertEqual(out, SPEC8_ROOT_HASH)

            self.assertEqual(
                sha256_hex((root / "manifest.json").read_bytes()),
                SPEC8_DIGEST_MANIFEST_JSON,
            )
            self.assertEqual(
                sha256_hex((root / "graph.yaml").read_bytes()),
                SPEC8_DIGEST_GRAPH_YAML,
            )
            self.assertEqual(
                sha256_hex((root / "inputs" / "audio_index.json").read_bytes()),
                SPEC8_DIGEST_INPUTS_JSON,
            )
            self.assertEqual(
                sha256_hex((root / "segments" / "segments.json").read_bytes()),
                SPEC8_DIGEST_SEGMENTS_JSON,
            )
            self.assertEqual(
                sha256_hex((root / "predictions" / "predictions.json").read_bytes()),
                SPEC8_DIGEST_PREDICTIONS_JSON,
            )
            self.assertEqual(
                sha256_hex((root / "hashes" / "sha256_manifest.json").read_bytes()),
                SPEC8_ROOT_HASH,
            )
            rh = (root / "hashes" / "root_hash.txt").read_text(encoding="utf-8")
            self.assertEqual(rh, SPEC8_ROOT_HASH + "\n")

    def test_write_arb_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            a = write_arb(
                Path(t1),
                manifest=dict(SPEC8_MANIFEST),
                graph_yaml=SPEC8_GRAPH_YAML,
                inputs=dict(SPEC8_INPUTS),
                segments=dict(SPEC8_SEGMENTS),
                predictions=dict(SPEC8_PREDICTIONS),
            )
            b = write_arb(
                Path(t2),
                manifest=dict(SPEC8_MANIFEST),
                graph_yaml=SPEC8_GRAPH_YAML,
                inputs=dict(SPEC8_INPUTS),
                segments=dict(SPEC8_SEGMENTS),
                predictions=dict(SPEC8_PREDICTIONS),
            )
            self.assertEqual(a, b)

    def test_manifest_missing_required_key(self) -> None:
        bad = dict(SPEC8_MANIFEST)
        del bad["bundle_id"]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_arb(
                    Path(tmp),
                    manifest=bad,
                    graph_yaml=SPEC8_GRAPH_YAML,
                    inputs=dict(SPEC8_INPUTS),
                    segments=dict(SPEC8_SEGMENTS),
                    predictions=dict(SPEC8_PREDICTIONS),
                )

    def test_manifest_extra_key(self) -> None:
        bad = {**SPEC8_MANIFEST, "extra": "nope"}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_arb(
                    Path(tmp),
                    manifest=bad,
                    graph_yaml=SPEC8_GRAPH_YAML,
                    inputs=dict(SPEC8_INPUTS),
                    segments=dict(SPEC8_SEGMENTS),
                    predictions=dict(SPEC8_PREDICTIONS),
                )

    def test_manifest_wrong_arb_version(self) -> None:
        bad = dict(SPEC8_MANIFEST)
        bad["arb_version"] = "0.2"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_arb(
                    Path(tmp),
                    manifest=bad,
                    graph_yaml=SPEC8_GRAPH_YAML,
                    inputs=dict(SPEC8_INPUTS),
                    segments=dict(SPEC8_SEGMENTS),
                    predictions=dict(SPEC8_PREDICTIONS),
                )

    def test_manifest_wrong_runtime_mode(self) -> None:
        bad = dict(SPEC8_MANIFEST)
        bad["runtime_mode"] = "live"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_arb(
                    Path(tmp),
                    manifest=bad,
                    graph_yaml=SPEC8_GRAPH_YAML,
                    inputs=dict(SPEC8_INPUTS),
                    segments=dict(SPEC8_SEGMENTS),
                    predictions=dict(SPEC8_PREDICTIONS),
                )

    def test_manifest_wrong_graph_spec_path(self) -> None:
        bad = dict(SPEC8_MANIFEST)
        bad["graph_spec_path"] = "other.yaml"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_arb(
                    Path(tmp),
                    manifest=bad,
                    graph_yaml=SPEC8_GRAPH_YAML,
                    inputs=dict(SPEC8_INPUTS),
                    segments=dict(SPEC8_SEGMENTS),
                    predictions=dict(SPEC8_PREDICTIONS),
                )


if __name__ == "__main__":
    unittest.main()
