"""Tests for ``aurora.arb.reader`` (stdlib unittest)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import test_arb_writer as spec8_fixtures

from aurora.arb import read_arb, write_arb


class TestArbReader(unittest.TestCase):
    def test_round_trip_spec8_equals_writer_output(self) -> None:
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
            bundle = read_arb(root)
            self.assertEqual(bundle.manifest, dict(spec8_fixtures.SPEC8_MANIFEST))
            self.assertEqual(bundle.graph_yaml, spec8_fixtures.SPEC8_GRAPH_YAML)
            self.assertEqual(bundle.audio_index, dict(spec8_fixtures.SPEC8_INPUTS))
            self.assertEqual(bundle.segments, dict(spec8_fixtures.SPEC8_SEGMENTS))
            self.assertEqual(bundle.predictions, dict(spec8_fixtures.SPEC8_PREDICTIONS))
            self.assertIsInstance(bundle.sha256_manifest, dict)
            self.assertEqual(bundle.sha256_manifest.get("arb_version"), "0.1")
            self.assertIn("files", bundle.sha256_manifest)
            self.assertEqual(len(bundle.root_hash), 64)

    def test_read_arb_bundle_root_not_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "nope.txt"
            p.write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_arb(p)
            self.assertIn("not a directory", str(ctx.exception).lower())

    def test_read_arb_missing_required_file(self) -> None:
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
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("segments/segments.json", str(ctx.exception))

    def test_read_arb_invalid_manifest_json(self) -> None:
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
            (root / "manifest.json").write_text("{", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("manifest.json", str(ctx.exception))

    def test_read_arb_manifest_not_json_object(self) -> None:
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
            (root / "manifest.json").write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("JSON object", str(ctx.exception))

    def test_read_arb_manifest_fails_writer_validation(self) -> None:
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
            bad = dict(spec8_fixtures.SPEC8_MANIFEST)
            bad["arb_version"] = "0.2"
            (root / "manifest.json").write_bytes(
                json.dumps(bad, sort_keys=True).encode("utf-8")
            )
            with self.assertRaises(ValueError):
                read_arb(root)

    def test_read_arb_manifest_utf8_bom_rejected(self) -> None:
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
            raw = (root / "manifest.json").read_bytes()
            (root / "manifest.json").write_bytes(b"\xef\xbb\xbf" + raw)
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("BOM", str(ctx.exception))

    def test_read_arb_graph_yaml_bom_rejected(self) -> None:
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
            raw = (root / "graph.yaml").read_bytes()
            (root / "graph.yaml").write_bytes(b"\xef\xbb\xbf" + raw)
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("BOM", str(ctx.exception))

    def test_read_arb_root_hash_wrong_length(self) -> None:
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
            (root / "hashes" / "root_hash.txt").write_text("abc\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("64", str(ctx.exception))

    def test_read_arb_root_hash_not_lowercase_hex(self) -> None:
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
            h = "a" * 63 + "b"  # 64 lowercase hex chars
            (root / "hashes" / "root_hash.txt").write_text(h.upper() + "\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("hexadecimal", str(ctx.exception).lower())

    def test_read_arb_root_hash_multiple_lines(self) -> None:
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
                "a" * 64 + "\n" + "b" * 64 + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("one line", str(ctx.exception).lower())

    def test_read_arb_nested_json_not_object(self) -> None:
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
            (root / "inputs" / "audio_index.json").write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_arb(root)
            self.assertIn("JSON object", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
