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

    Exit codes: ``0`` success, ``1`` validation failure, ``2`` usage error.
    """
    args = argv if argv is not None else sys.argv
    if len(args) != 4 or args[1] != "-m" or args[2] != "aurora.arb":
        sys.stderr.write(_USAGE)
        sys.exit(2)
    try:
        validate_arb(args[3])
    except ArbValidationError as exc:
        sys.stderr.write(f"{_FAIL_PREFIX}{exc}\n")
        sys.exit(1)
    sys.stdout.write(_OK)
    sys.exit(0)


if __name__ == "__main__":
    main()
