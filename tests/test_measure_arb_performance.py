"""Tests for ``scripts/measure_arb_performance.py`` (stdlib unittest)."""

from __future__ import annotations

import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_FORBIDDEN_NAME_FRAGMENTS = (
    "native",
    "decode",
    "graph",
    "tflite",
    "mediapipe",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestMeasureArbPerformance(unittest.TestCase):
    def test_cli_writes_json_with_expected_operations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "baseline.json"
            env = os.environ.copy()
            env.setdefault("PYTHONPATH", str(_repo_root() / "src"))
            proc = subprocess.run(
                [
                    sys.executable,
                    str(_repo_root() / "scripts" / "measure_arb_performance.py"),
                    "--iterations",
                    "2",
                    "--repeat",
                    "2",
                    "--output",
                    str(out),
                ],
                cwd=_repo_root(),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))

        required_keys = {
            "schema_version",
            "python_version",
            "platform",
            "iterations",
            "repeat",
            "units",
            "non_sla",
            "operations",
        }
        self.assertEqual(set(data.keys()), required_keys)
        self.assertTrue(data["non_sla"])
        self.assertEqual(data["units"], "nanoseconds")
        self.assertEqual(data["iterations"], 2)
        self.assertEqual(data["repeat"], 2)

        names = [op["name"] for op in data["operations"]]
        for expected in (
            "canonicalize_small_manifest",
            "sha256_hex_small_payload",
            "compute_root_hash_small_manifest_bytes",
            "write_arb_spec8_fixture",
            "read_arb_spec8_fixture",
            "validate_arb_spec8_fixture",
        ):
            self.assertIn(expected, names)

        for op in data["operations"]:
            for frag in _FORBIDDEN_NAME_FRAGMENTS:
                self.assertNotIn(frag, op["name"])
            samples = op["samples_ns"]
            self.assertIsInstance(samples, list)
            self.assertEqual(len(samples), 4)  # 2 * 2
            self.assertTrue(all(isinstance(x, int) for x in samples))
            self.assertEqual(op["min_ns"], min(samples))
            self.assertEqual(op["max_ns"], max(samples))
            self.assertEqual(
                op["median_ns"], int(round(statistics.median(samples)))
            )
            sorted_s = sorted(samples)
            idx = int(math.ceil(0.95 * len(sorted_s))) - 1
            self.assertEqual(
                op["p95_ns"], sorted_s[max(0, min(idx, len(sorted_s) - 1))]
            )

    def test_invalid_iterations_exit_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "baseline.json"
            env = os.environ.copy()
            env.setdefault("PYTHONPATH", str(_repo_root() / "src"))
            proc = subprocess.run(
                [
                    sys.executable,
                    str(_repo_root() / "scripts" / "measure_arb_performance.py"),
                    "--iterations",
                    "0",
                    "--repeat",
                    "1",
                    "--output",
                    str(out),
                ],
                cwd=_repo_root(),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
