"""CLI entry point for ARB v0.1 validation: ``python -m aurora.arb <bundle-root>``.

Thin wrapper over :func:`aurora.arb.validator.validate_arb` — no inspect/read subcommands.
"""

from __future__ import annotations

import sys

from aurora.arb.validator import ArbValidationError, validate_arb

_USAGE = "usage: python -m aurora.arb <bundle-root>\n"
_OK = "OK: ARB v0.1 bundle is valid.\n"
_FAIL_PREFIX = "ARB_VALIDATION_FAILED: "


def main(argv: list[str] | None = None) -> None:
    """Run CLI validation. Uses ``sys.argv`` when *argv* is ``None``.

    For a normal ``python -m aurora.arb <bundle-root>`` run, Python sets ``sys.argv``
    to two elements: ``argv[0]`` is the path to this ``__main__.py`` (or similar, as
    the interpreter assigns it); ``argv[1]`` is the bundle root. The strings ``-m``
    and ``aurora.arb`` do **not** appear in ``sys.argv``.

    Exit codes: ``0`` success, ``1`` validation failure, ``2`` usage error.
    """
    args = argv if argv is not None else sys.argv
    if len(args) != 2:
        sys.stderr.write(_USAGE)
        sys.exit(2)
    try:
        validate_arb(args[1])
    except ArbValidationError as exc:
        sys.stderr.write(f"{_FAIL_PREFIX}{exc}\n")
        sys.exit(1)
    sys.stdout.write(_OK)
    sys.exit(0)


if __name__ == "__main__":
    main()
