"""Tests for ``python -m aurora.arb`` (stdlib unittest; in-process ``main()``)."""

from __future__ import annotations

import io
import runpy
import sys
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch

import test_arb_writer as spec8_fixtures

from aurora.arb import __main__ as arb_main
from aurora.arb import write_arb


class _ExitCalled(Exception):
    """Raised when patched ``sys.exit`` runs (captures exit code)."""

    def __init__(self, code: int | None) -> None:
        self.code = 0 if code is None else code


def _argv_two(bundle_root: str) -> list[str]:
    """Shape Python uses for ``python -m aurora.arb <bundle-root>``: ``[argv0, bundle]``."""
    return [sys.executable, bundle_root]


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    """Invoke ``main(argv)``; return (exit_code, stdout, stderr)."""
    out = io.StringIO()
    err = io.StringIO()

    def fake_exit(code: int | None = None) -> None:
        raise _ExitCalled(code)

    with patch.object(arb_main.sys, "stdout", out), patch.object(arb_main.sys, "stderr", err):
        with patch.object(arb_main.sys, "exit", fake_exit):
            try:
                arb_main.main(argv)
            except _ExitCalled as exc:
                return exc.code, out.getvalue(), err.getvalue()
    raise AssertionError("main() did not call sys.exit")


class TestArbCli(unittest.TestCase):
    def test_valid_bundle_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            code, out, err = _run_main(_argv_two(str(root)))
            self.assertEqual(code, 0)
            self.assertEqual(out, arb_main._OK)
            self.assertEqual(err, "")

    def test_invalid_bundle_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            (root / "manifest.json").write_bytes(b"not canonical json")
            code, out, err = _run_main(_argv_two(str(root)))
            self.assertEqual(code, 1)
            self.assertEqual(out, "")
            self.assertTrue(err.startswith(arb_main._FAIL_PREFIX), err)

    def test_missing_bundle_arg_exits_two(self) -> None:
        code, out, err = _run_main([sys.executable])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertEqual(err, arb_main._USAGE)

    def test_too_many_args_exits_two(self) -> None:
        code, out, err = _run_main([sys.executable, "/tmp/a", "extra"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertEqual(err, arb_main._USAGE)

    def test_nonexistent_bundle_root_exits_one(self) -> None:
        code, out, err = _run_main(
            _argv_two("/nonexistent/path/arb-bundle-xyz"),
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("bundle root is not a directory", err)

    def test_run_module_as___main___invokes_guard_and_main(self) -> None:
        """Cover ``if __name__ == "__main__": main()`` (``runpy`` + ``run_name``)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bundle"
            write_arb(
                root,
                manifest=dict(spec8_fixtures.SPEC8_MANIFEST),
                graph_yaml=spec8_fixtures.SPEC8_GRAPH_YAML,
                inputs=dict(spec8_fixtures.SPEC8_INPUTS),
                segments=dict(spec8_fixtures.SPEC8_SEGMENTS),
                predictions=dict(spec8_fixtures.SPEC8_PREDICTIONS),
            )
            argv = ["/fake/path/to/__main__.py", str(root)]
            out = io.StringIO()
            err = io.StringIO()

            def fake_exit(code: int | None = None) -> None:
                raise _ExitCalled(code)

            with patch.object(sys, "argv", argv):
                with patch.object(sys, "stdout", out), patch.object(sys, "stderr", err):
                    with patch.object(sys, "exit", fake_exit):
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", RuntimeWarning)
                            try:
                                runpy.run_module(
                                    "aurora.arb.__main__",
                                    run_name="__main__",
                                )
                            except _ExitCalled as exc:
                                self.assertEqual(exc.code, 0)
            self.assertEqual(out.getvalue(), arb_main._OK)
            self.assertEqual(err.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
