"""Tests for ``aurora.arb.validator`` (stdlib unittest)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import test_arb_writer as spec8_fixtures

from aurora.arb import ArbValidationError, read_arb, validate_arb, write_arb


class TestArbValidator(unittest.TestCase):
    def test_validate_arb_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            validate_arb(root)

    def test_validate_arb_tampered_payload_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            # graph.yaml: raw-byte hash (§5.3); tamper without breaking JSON payloads.
            g = root / "graph.yaml"
            g.write_bytes(g.read_bytes() + b"\n# tampered\n")
            with self.assertRaises(ArbValidationError) as ctx:
                validate_arb(root)
            self.assertIn("SHA-256 mismatch", str(ctx.exception))

    def test_validate_arb_tampered_root_hash_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            (root / "hashes" / "root_hash.txt").write_text(
                "a" * 64 + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ArbValidationError) as ctx:
                validate_arb(root)
            self.assertIn("root hash mismatch", str(ctx.exception).lower())

    def test_validate_arb_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            (root / "segments" / "segments.json").unlink()
            with self.assertRaises(ArbValidationError) as ctx:
                validate_arb(root)
            self.assertIn("segments/segments.json", str(ctx.exception))

    def test_validate_arb_malformed_root_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            (root / "hashes" / "root_hash.txt").write_text("not-hex\n", encoding="utf-8")
            with self.assertRaises(ArbValidationError) as ctx:
                validate_arb(root)
            self.assertIn("64", str(ctx.exception))

    def test_validate_arb_non_canonical_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            (root / "manifest.json").write_text(
                json.dumps(m, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ArbValidationError) as ctx:
                validate_arb(root)
            self.assertIn("canonical JSON", str(ctx.exception))

    def test_validate_arb_sha256_manifest_extra_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            hpath = root / "hashes" / "sha256_manifest.json"
            h = json.loads(hpath.read_text(encoding="utf-8"))
            h["extra"] = "nope"
            hpath.write_bytes(json.dumps(h, sort_keys=True).encode("utf-8"))
            with self.assertRaises(ArbValidationError) as ctx:
                validate_arb(root)
            self.assertIn("exactly keys", str(ctx.exception))

    def test_read_arb_succeeds_where_validate_arb_fails(self) -> None:
        """Load does not imply verify — reader accepts tampered payload; validator rejects."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            p = root / "predictions" / "predictions.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            obj["predictions"][0]["score"] = "0.50"
            p.write_bytes(json.dumps(obj, sort_keys=True).encode("utf-8"))
            bundle = read_arb(root)
            self.assertEqual(bundle.predictions["predictions"][0]["score"], "0.50")
            with self.assertRaises(ArbValidationError):
                validate_arb(root)


if __name__ == "__main__":
    unittest.main()
