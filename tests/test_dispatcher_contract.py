"""Contract tests for ``Dispatcher`` (M06; stdlib unittest).

Requires ``PYTHONPATH`` to include ``src`` (set in CI and documented in DEVELOPMENT.md).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Protocol

REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class _StubDispatcher:
    """Minimal fake satisfying :class:`Dispatcher` for structural tests."""

    def dispatch(self, *args: Any, **kwargs: Any) -> tuple[Any, ...]:
        return ("stub", args, kwargs)


class TestDispatcherContract(unittest.TestCase):
    def test_module_imports(self) -> None:
        from aurora.runtime.dispatcher import Dispatcher  # noqa: PLC0415

        self.assertTrue(callable(Dispatcher))

    def test_stub_satisfies_protocol(self) -> None:
        from aurora.runtime.dispatcher import Dispatcher  # noqa: PLC0415

        stub = _StubDispatcher()
        self.assertIsInstance(stub, Dispatcher)

    def test_dispatcher_is_protocol_subclass(self) -> None:
        from aurora.runtime.dispatcher import Dispatcher  # noqa: PLC0415

        self.assertTrue(issubclass(Dispatcher, Protocol))


if __name__ == "__main__":
    unittest.main()
