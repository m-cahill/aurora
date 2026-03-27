"""Minimal runtime substrate contract (M05).

This module is **first-party AURORA code**. It is not copied from the workspace
``mediapipe/`` clone and does not import ``mediapipe``. It exists only to record
that a tracked, importable substrate is present and to expose a tiny metadata
surface for CI and docs.
"""

from __future__ import annotations

from dataclasses import dataclass

# Bump when the substrate metadata shape or semantics change.
SUBSTRATE_CONTRACT_VERSION = 1

# Stable tag for tests and the project record (not the execution-phase letter).
SUBSTRATE_ESTABLISHMENT_ID = "m05"


@dataclass(frozen=True, slots=True)
class RuntimeSubstrateMetadata:
    """Reviewable description of what the tracked substrate is *for* M05."""

    package_import_path: str
    contract_version: int
    establishment_id: str


def get_runtime_substrate_metadata() -> RuntimeSubstrateMetadata:
    """Return metadata for the current tracked runtime substrate.

    This does **not** assert MediaPipe correctness or application behavior; it
    only describes the repository-local Python package boundary introduced in M05.
    """
    return RuntimeSubstrateMetadata(
        package_import_path="aurora",
        contract_version=SUBSTRATE_CONTRACT_VERSION,
        establishment_id=SUBSTRATE_ESTABLISHMENT_ID,
    )
