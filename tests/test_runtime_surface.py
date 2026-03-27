"""Substrate import and metadata tests (M05; stdlib unittest).

Requires ``PYTHONPATH`` to include ``src`` (set in CI and documented in DEVELOPMENT.md).
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class TestRuntimeSurface(unittest.TestCase):
    def test_import_aurora_and_runtime(self) -> None:
        import aurora  # noqa: PLC0415 — exercised by test
        import aurora.runtime  # noqa: PLC0415

        self.assertIsNotNone(aurora)
        self.assertIsNotNone(aurora.runtime)

    def test_substrate_metadata_contract(self) -> None:
        from aurora.runtime.surface import (  # noqa: PLC0415
            SUBSTRATE_CONTRACT_VERSION,
            get_runtime_substrate_metadata,
        )

        meta = get_runtime_substrate_metadata()
        self.assertEqual(meta.package_import_path, "aurora")
        self.assertEqual(meta.contract_version, SUBSTRATE_CONTRACT_VERSION)
        self.assertEqual(meta.establishment_id, "m05")

    def test_no_mediapipe_imports_under_src_aurora(self) -> None:
        """Static scan: no mediapipe imports in tracked substrate sources."""
        aurora_pkg = REPO_ROOT / "src" / "aurora"
        for path in sorted(aurora_pkg.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        self.assertFalse(
                            name == "mediapipe" or name.startswith("mediapipe."),
                            msg=f"unexpected mediapipe import in {path}",
                        )
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module
                    if mod:
                        self.assertFalse(
                            mod == "mediapipe" or mod.startswith("mediapipe."),
                            msg=f"unexpected mediapipe import in {path}",
                        )

    def test_surface_py_is_stdlib_imports_only(self) -> None:
        """M05 ``surface.py`` must not add third-party dependencies."""
        path = REPO_ROOT / "src" / "aurora" / "runtime" / "surface.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        allowed_roots = frozenset({"dataclasses", "__future__"})
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.fail("surface.py must use only from-imports for M05 stdlib surface")
            if isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                self.assertIsNotNone(node.module)
                root = node.module.split(".", 1)[0]
                self.assertIn(
                    root,
                    allowed_roots,
                    msg=f"non-stdlib import in surface.py: from {node.module!r}",
                )


if __name__ == "__main__":
    unittest.main()
