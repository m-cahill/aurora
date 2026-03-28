#!/usr/bin/env python3
"""Enforce separate line- and branch-coverage floors from ``coverage.json`` (M12).

``coverage report`` with ``branch = True`` uses a *combined* line+branch
percentage for ``fail_under``. This script applies **two** explicit checks:

* **Line floor** — statement coverage only (M11 regression guard).
* **Branch floor** — measured branch arcs only (M12 regression guard).

Reads ``artifacts/coverage.json`` (``totals`` from ``coverage json``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Regression floors for ``src/aurora/`` (see ``.coveragerc`` ``source``).
LINE_FAIL_UNDER = 100.0
BRANCH_FAIL_UNDER = 100.0


def _line_percent(totals: dict[str, int | float]) -> float:
    stmts = int(totals["num_statements"])
    if stmts == 0:
        return 100.0
    return 100.0 * float(totals["covered_lines"]) / float(stmts)


def _branch_percent(totals: dict[str, int | float]) -> float | None:
    nb = int(totals["num_branches"])
    if nb == 0:
        return None
    return 100.0 * float(totals["covered_branches"]) / float(nb)


def check_totals(totals: dict[str, int | float]) -> list[str]:
    """Return a list of error messages (empty if all gates pass)."""
    errors: list[str] = []

    line_pct = _line_percent(totals)
    if line_pct + 1e-9 < LINE_FAIL_UNDER:
        errors.append(
            f"Line coverage {line_pct:.{1}f}% is below fail-under {LINE_FAIL_UNDER:g}% "
            f"({totals['covered_lines']}/{totals['num_statements']} statements)."
        )

    br_pct = _branch_percent(totals)
    if br_pct is not None and br_pct + 1e-9 < BRANCH_FAIL_UNDER:
        errors.append(
            f"Branch coverage {br_pct:.{1}f}% is below fail-under {BRANCH_FAIL_UNDER:g}% "
            f"({totals['covered_branches']}/{totals['num_branches']} branches)."
        )

    if int(totals.get("num_partial_branches", 0)) > 0:
        errors.append(
            "Partial branch coverage detected (see ``coverage report`` / HTML for arcs)."
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-path",
        type=Path,
        default=Path("artifacts/coverage.json"),
        help="Path to coverage JSON (default: artifacts/coverage.json)",
    )
    args = parser.parse_args(argv)

    path: Path = args.json_path
    if not path.is_file():
        print(f"error: coverage JSON not found: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    totals = data.get("totals")
    if not isinstance(totals, dict):
        print("error: coverage JSON missing 'totals'", file=sys.stderr)
        return 1

    line_pct = _line_percent(totals)
    br_pct = _branch_percent(totals)
    br_note = f"{br_pct:.1f}%" if br_pct is not None else "n/a (no branch arcs)"

    print(
        f"Coverage gates: line {line_pct:.1f}% (floor {LINE_FAIL_UNDER:g}%), "
        f"branch {br_note} (floor {BRANCH_FAIL_UNDER:g}%)."
    )

    errors = check_totals(totals)
    if errors:
        for msg in errors:
            print(f"Coverage gate failure: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
