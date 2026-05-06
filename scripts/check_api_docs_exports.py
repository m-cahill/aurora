#!/usr/bin/env python3
"""Ensure hand-curated API docs mention every name in public ``__all__`` lists (M37).

Parses ``src/aurora/runtime/__init__.py`` and ``src/aurora/arb/__init__.py`` for ``__all__``,
then requires a matching ``## `Name` `` heading in ``docs/api/runtime.md`` resp. ``arb.md``.
Extra doc sections (e.g. validate-only CLI) are allowed without a matching export.

stdlib-only; use ``make api-doc-check``. Not run in GitHub Actions for M37.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_HEADING_RE = re.compile(r"^## `([^`]+)`\s*$", re.MULTILINE)


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def parse_all_from_init(init_path: Path) -> list[str]:
    text = init_path.read_text(encoding="utf-8")
    match = re.search(r"__all__\s*=\s*\[([\s\S]*?)\]\s*", text)
    if not match:
        raise ValueError(f"no __all__ assignment list found in {init_path}")
    body = match.group(1)
    names = re.findall(r'"([^"]+)"', body) + re.findall(r"'([^']+)'", body)
    # De-dupe preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    return ordered


def parse_doc_export_headings(md_path: Path) -> set[str]:
    return set(_HEADING_RE.findall(md_path.read_text(encoding="utf-8")))


def missing_exports(exports: list[str], headings: set[str]) -> list[str]:
    return [n for n in exports if n not in headings]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/).",
    )
    args = parser.parse_args(argv)
    root = args.repo_root if args.repo_root is not None else repo_root_from_script(Path(__file__))
    pairs: list[tuple[str, Path, Path]] = [
        (
            "aurora.runtime",
            root / "src/aurora/runtime/__init__.py",
            root / "docs/api/runtime.md",
        ),
        (
            "aurora.arb",
            root / "src/aurora/arb/__init__.py",
            root / "docs/api/arb.md",
        ),
    ]
    errors: list[str] = []
    for label, init_p, md_p in pairs:
        if not init_p.is_file():
            errors.append(f"{label}: missing package init: {init_p}")
            continue
        if not md_p.is_file():
            errors.append(f"{label}: missing API doc: {md_p}")
            continue
        try:
            exports = parse_all_from_init(init_p)
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue
        headings = parse_doc_export_headings(md_p)
        missing = missing_exports(exports, headings)
        if missing:
            errors.append(
                f"{label}: exported in __all__ but no '## `name`' heading in {md_p.name}: "
                f"{', '.join(sorted(missing))}"
            )
    if errors:
        for msg in errors:
            print(msg, file=sys.stderr)
        return 1
    print("API doc export headings: OK (aurora.runtime + aurora.arb).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

