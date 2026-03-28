"""Tests for ``scripts/check_coverage_thresholds.py`` (M12)."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_coverage_thresholds as cct  # noqa: E402


class TestCheckCoverageThresholds(unittest.TestCase):
    def test_passes_at_100_100(self) -> None:
        totals = {
            "covered_lines": 94,
            "num_statements": 94,
            "num_branches": 4,
            "covered_branches": 4,
            "num_partial_branches": 0,
        }
        self.assertEqual(cct.check_totals(totals), [])

    def test_fails_low_line(self) -> None:
        totals = {
            "covered_lines": 90,
            "num_statements": 94,
            "num_branches": 4,
            "covered_branches": 4,
            "num_partial_branches": 0,
        }
        err = cct.check_totals(totals)
        self.assertEqual(len(err), 1)
        self.assertIn("Line coverage", err[0])

    def test_fails_low_branch(self) -> None:
        totals = {
            "covered_lines": 94,
            "num_statements": 94,
            "num_branches": 4,
            "covered_branches": 3,
            "num_partial_branches": 0,
        }
        err = cct.check_totals(totals)
        self.assertEqual(len(err), 1)
        self.assertIn("Branch coverage", err[0])

    def test_fails_partial_branches(self) -> None:
        totals = {
            "covered_lines": 94,
            "num_statements": 94,
            "num_branches": 4,
            "covered_branches": 4,
            "num_partial_branches": 1,
        }
        err = cct.check_totals(totals)
        self.assertEqual(len(err), 1)
        self.assertIn("Partial branch", err[0])

    def test_main_missing_file_returns_1(self) -> None:
        buf = io.StringIO()
        with mock.patch.object(sys, "stderr", buf):
            rc = cct.main(["--json-path", str(REPO_ROOT / "artifacts" / "no_such_file.json")])
        self.assertEqual(rc, 1)
        self.assertIn("not found", buf.getvalue())

    def test_main_passes_with_fixture_file(self) -> None:
        fixture = {
            "totals": {
                "covered_lines": 10,
                "num_statements": 10,
                "num_branches": 2,
                "covered_branches": 2,
                "num_partial_branches": 0,
            }
        }
        p = REPO_ROOT / "artifacts" / "_test_coverage_gate_fixture.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            p.write_text(json.dumps(fixture), encoding="utf-8")
            rc = cct.main(["--json-path", str(p)])
            self.assertEqual(rc, 0)
        finally:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
