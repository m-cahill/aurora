"""Tests for scripts/check_api_docs_exports.py (M37)."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_check_module():
    path = REPO_ROOT / "scripts" / "check_api_docs_exports.py"
    spec = importlib.util.spec_from_file_location("check_api_docs_exports", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_check_module()


class TestParseAllFromInit(unittest.TestCase):
    def test_runtime_init_lists_exports(self) -> None:
        init = REPO_ROOT / "src/aurora/runtime/__init__.py"
        names = _mod.parse_all_from_init(init)
        self.assertIn("Dispatcher", names)
        self.assertIn("AuroraImage", names)

    def test_raises_when_no_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.py"
            p.write_text("x = 1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                _mod.parse_all_from_init(p)


class TestDocHeadings(unittest.TestCase):
    def test_runtime_doc_covers_all_exports(self) -> None:
        init = REPO_ROOT / "src/aurora/runtime/__init__.py"
        md = REPO_ROOT / "docs/api/runtime.md"
        exports = _mod.parse_all_from_init(init)
        headings = _mod.parse_doc_export_headings(md)
        missing = _mod.missing_exports(exports, headings)
        self.assertEqual(missing, [], msg=f"missing doc headings: {missing}")

    def test_detects_missing_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            init = Path(tmp) / "__init__.py"
            init.write_text('__all__ = ["OnlyOne"]\n', encoding="utf-8")
            md = Path(tmp) / "api.md"
            md.write_text("## `Other`\n", encoding="utf-8")
            exports = _mod.parse_all_from_init(init)
            headings = _mod.parse_doc_export_headings(md)
            self.assertEqual(_mod.missing_exports(exports, headings), ["OnlyOne"])


class TestMainIntegration(unittest.TestCase):
    def test_main_zero_on_real_repo(self) -> None:
        self.assertEqual(_mod.main(["--repo-root", str(REPO_ROOT)]), 0)

    def test_main_fails_on_bad_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src/aurora/runtime").mkdir(parents=True)
            (root / "src/aurora/arb").mkdir(parents=True)
            (root / "docs/api").mkdir(parents=True)
            (root / "src/aurora/runtime/__init__.py").write_text(
                '__all__ = ["X"]\n', encoding="utf-8"
            )
            (root / "src/aurora/arb/__init__.py").write_text(
                '__all__ = ["Y"]\n', encoding="utf-8"
            )
            (root / "docs/api/runtime.md").write_text("## `Z`\n", encoding="utf-8")
            (root / "docs/api/arb.md").write_text("## `Y`\n", encoding="utf-8")
            self.assertEqual(_mod.main(["--repo-root", str(root)]), 1)


if __name__ == "__main__":
    unittest.main()
