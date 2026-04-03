"""Support-tier tests for scripts/verify_repo_state.py (stdlib unittest)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import verify_repo_state  # noqa: E402

# Full SHA pin used in real CI — valid for pin policy tests.
_PINNED_CHECKOUT = "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def _minimal_aurora_md() -> str:
    return """# A

## Execution Phase Boundaries (locked)

## Program Roadmap (proposed)

Governance: `docs/runtime_surface_strategy.md`.
Substrate: `docs/runtime_substrate.md`.
Seam framing: `docs/runtime_seam_framing.md`.
ARB boundary: `docs/aurora_run_bundle_boundary.md`.
ARB v0.1 spec: `docs/aurora_run_bundle_v0_spec.md`.

"""


def _minimal_runtime_substrate_md() -> str:
    return """# Runtime substrate

Placeholder for verifier fixtures.

"""


def _minimal_runtime_seam_framing_md() -> str:
    return """# Runtime seam framing

Placeholder for verifier fixtures.

"""


def _minimal_aurora_run_bundle_boundary_md() -> str:
    return """# ARB boundary

Placeholder for verifier fixtures.

"""


def _minimal_aurora_run_bundle_v0_spec_md() -> str:
    return """# ARB v0.1 spec

Placeholder for verifier fixtures.

"""


def _minimal_seam_contract_src_files() -> dict[str, str]:
    return {
        "src/aurora/runtime/dispatcher.py": (
            '"""D."""\n'
            "from __future__ import annotations\n"
            "from typing import Any, Protocol, runtime_checkable\n\n"
            "@runtime_checkable\n"
            "class Dispatcher(Protocol):\n"
            "    def dispatch(self, *args: Any, **kwargs: Any) -> Any: ...\n"
        ),
        "src/aurora/runtime/library_loader.py": (
            '"""L."""\n'
            "from __future__ import annotations\n"
            "from typing import Any, Protocol, runtime_checkable\n\n"
            "@runtime_checkable\n"
            "class LibraryLoader(Protocol):\n"
            "    def shared_library(self) -> Any: ...\n"
        ),
        "src/aurora/runtime/errors.py": (
            '"""E."""\n'
            "from __future__ import annotations\n\n"
            "class AuroraRuntimeError(Exception):\n"
            "    pass\n"
        ),
        "src/aurora/runtime/dispatch_tokens.py": (
            '"""T."""\n'
            "from __future__ import annotations\n\n"
            "IMAGE_FROM_FILE = \"aurora_image_from_file\"\n"
            "IMAGE_FROM_BYTES = \"aurora_image_from_bytes\"\n"
            "AUDIO_FROM_FILE = \"aurora_audio_from_file\"\n"
            "AUDIO_FROM_BYTES = \"aurora_audio_from_bytes\"\n"
        ),
        "src/aurora/runtime/image_dispatch.py": (
            '"""ID."""\n'
            "from __future__ import annotations\n"
            "from typing import Any\n"
            "from aurora.runtime.dispatch_tokens import IMAGE_FROM_BYTES, IMAGE_FROM_FILE\n"
            "from aurora.runtime.dispatcher import Dispatcher\n"
            "from aurora.runtime.library_loader import LibraryLoader\n"
            "def dispatch_image_from_file(\n"
            "    dispatcher: Dispatcher, library_loader: LibraryLoader, path: str\n"
            ") -> Any:\n"
            "    lib = library_loader.shared_library()\n"
            "    return dispatcher.dispatch(IMAGE_FROM_FILE, path, lib)\n"
            "def dispatch_image_from_bytes(\n"
            "    dispatcher: Dispatcher, library_loader: LibraryLoader, data: bytes\n"
            ") -> Any:\n"
            "    lib = library_loader.shared_library()\n"
            "    return dispatcher.dispatch(IMAGE_FROM_BYTES, data, lib)\n"
        ),
        "src/aurora/runtime/audio_dispatch.py": (
            '"""AD."""\n'
            "from __future__ import annotations\n"
            "from typing import Any\n"
            "from aurora.runtime.dispatch_tokens import AUDIO_FROM_BYTES, AUDIO_FROM_FILE\n"
            "from aurora.runtime.dispatcher import Dispatcher\n"
            "from aurora.runtime.library_loader import LibraryLoader\n"
            "def dispatch_audio_from_file(\n"
            "    dispatcher: Dispatcher, library_loader: LibraryLoader, path: str\n"
            ") -> Any:\n"
            "    lib = library_loader.shared_library()\n"
            "    return dispatcher.dispatch(AUDIO_FROM_FILE, path, lib)\n"
            "def dispatch_audio_from_bytes(\n"
            "    dispatcher: Dispatcher, library_loader: LibraryLoader, data: bytes\n"
            ") -> Any:\n"
            "    lib = library_loader.shared_library()\n"
            "    return dispatcher.dispatch(AUDIO_FROM_BYTES, data, lib)\n"
        ),
        "src/aurora/runtime/shared_library_loader.py": (
            '"""S."""\n'
            "from __future__ import annotations\n"
            "from aurora.runtime.errors import AuroraRuntimeError\n"
            "class SharedLibraryLoadError(AuroraRuntimeError):\n"
            "    pass\n"
            "class SharedLibraryLoader:\n"
            "    def __init__(self, path): ...\n"
            "    def shared_library(self): ...\n"
        ),
        "src/aurora/runtime/image.py": (
            '"""I."""\n'
            "from __future__ import annotations\n"
            "from dataclasses import dataclass\n"
            "from typing import Any\n"
            "from aurora.runtime.dispatcher import Dispatcher\n"
            "from aurora.runtime.errors import AuroraRuntimeError\n"
            "from aurora.runtime.library_loader import LibraryLoader\n"
            "class ImageCreationError(AuroraRuntimeError):\n"
            "    pass\n"
            "@dataclass(frozen=True, slots=True)\n"
            "class AuroraImage:\n"
            "    dispatcher: Dispatcher\n"
            "    library_loader: LibraryLoader\n"
            "    native_handle: Any\n"
            "    source_path: str | None = None\n"
        ),
        "src/aurora/runtime/audio.py": (
            '"""AU."""\n'
            "from __future__ import annotations\n"
            "from dataclasses import dataclass\n"
            "from typing import Any\n"
            "from aurora.runtime.dispatcher import Dispatcher\n"
            "from aurora.runtime.errors import AuroraRuntimeError\n"
            "from aurora.runtime.library_loader import LibraryLoader\n"
            "class AudioCreationError(AuroraRuntimeError):\n"
            "    pass\n"
            "@dataclass(frozen=True, slots=True)\n"
            "class AuroraAudio:\n"
            "    dispatcher: Dispatcher\n"
            "    library_loader: LibraryLoader\n"
            "    native_handle: Any\n"
            "    source_path: str | None = None\n"
        ),
        "src/aurora/runtime/audio_native_bindings.py": (
            '"""M21 bindings stub for verifier fixture."""\n'
            "X = 1\n"
        ),
        "src/aurora/runtime/native_audio_dispatcher.py": (
            '"""M21 dispatcher stub for verifier fixture."""\n'
            "Y = 1\n"
        ),
    }


def _minimal_arb_src_files() -> dict[str, str]:
    return {
        "src/aurora/arb/__init__.py": (
            '"""ARB package stub for verifier fixture."""\n'
            "from __future__ import annotations\n\n"
            "X = 1\n"
        ),
        "src/aurora/arb/canonical_json.py": '"""C."""\nX = 1\n',
        "src/aurora/arb/hasher.py": '"""H."""\nX = 1\n',
        "src/aurora/arb/reader.py": '"""R."""\nX = 1\n',
        "src/aurora/arb/validator.py": '"""V."""\nX = 1\n',
        "src/aurora/arb/writer.py": '"""W."""\nX = 1\n',
    }


def _minimal_substrate_src_files() -> dict[str, str]:
    return {
        "src/aurora/__init__.py": '"""A."""\n',
        "src/aurora/runtime/__init__.py": '"""R."""\n',
        "src/aurora/runtime/surface.py": (
            '"""S."""\n'
            "from dataclasses import dataclass\n\n"
            "@dataclass(frozen=True, slots=True)\n"
            "class _T:\n"
            "    v: int = 0\n"
        ),
    }


def _substrate_docs_and_src() -> dict[str, str]:
    return {
        "docs/runtime_substrate.md": _minimal_runtime_substrate_md(),
        "docs/runtime_seam_framing.md": _minimal_runtime_seam_framing_md(),
        "docs/aurora_run_bundle_boundary.md": _minimal_aurora_run_bundle_boundary_md(),
        "docs/aurora_run_bundle_v0_spec.md": _minimal_aurora_run_bundle_v0_spec_md(),
        **_minimal_substrate_src_files(),
        **_minimal_seam_contract_src_files(),
        **_minimal_arb_src_files(),
    }


def _minimal_readme() -> str:
    return """# T

[x](docs/aurora.md)
"""


def _minimal_runtime_surface_md() -> str:
    return """# Runtime surface strategy

Placeholder content for verifier fixtures.

"""


def _minimal_ci_workflow(*, uses_line: str | None = None) -> str:
    use = uses_line if uses_line is not None else f"      - uses: {_PINNED_CHECKOUT}"
    return f"""name: ci
on: push
jobs:
  repo-safety:
    runs-on: ubuntu-24.04
    steps:
{use}
"""


def _init_git_repo(root: Path, files: dict[str, str]) -> None:
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(
        ["git", "add", "-A"],
        cwd=root,
        check=True,
        capture_output=True,
        env=_GIT_ENV,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
        env=_GIT_ENV,
    )


class TestVerifyRepoState(unittest.TestCase):
    def test_valid_minimal_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 0)

    def test_missing_canonical_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_runtime_surface_strategy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_reference_to_runtime_surface_in_aurora_md_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_aurora = """# A

## Execution Phase Boundaries (locked)

## Program Roadmap (proposed)

Substrate: `docs/runtime_substrate.md`.
Seam framing: `docs/runtime_seam_framing.md`.
ARB boundary: `docs/aurora_run_bundle_boundary.md`.
ARB v0.1 spec: `docs/aurora_run_bundle_v0_spec.md`.

"""
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": bad_aurora,
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_required_headings_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": "# no headings\n",
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_tracked_dotenv_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
                ".env": "SECRET=1\n",
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_continue_on_error_on_enforcement_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wf = (
                _minimal_ci_workflow()
                + "\n"
                + "      - name: bad\n"
                + "        continue-on-error: true\n"
                + "        run: echo hi\n"
            )
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": wf,
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_ubuntu_latest_runner_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wf = """name: ci
on: push
jobs:
  repo-safety:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
"""
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": wf,
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_unpinned_external_action_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(
                    uses_line="      - uses: actions/checkout@v4.2.2"
                ),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_short_sha_ref_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            short_sha = "11bd71901bbe5b1630ceea73d27597364c9af683"[:7]
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(
                    uses_line=f"      - uses: actions/checkout@{short_sha}"
                ),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_wrong_workflow_name_fails_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wf = """name: not-ci
on: push
jobs:
  repo-safety:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
"""
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": wf,
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_runtime_substrate_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                "docs/runtime_seam_framing.md": _minimal_runtime_seam_framing_md(),
                "docs/aurora_run_bundle_boundary.md": _minimal_aurora_run_bundle_boundary_md(),
                "docs/aurora_run_bundle_v0_spec.md": _minimal_aurora_run_bundle_v0_spec_md(),
                **_minimal_substrate_src_files(),
                **_minimal_seam_contract_src_files(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_runtime_seam_framing_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                "docs/runtime_substrate.md": _minimal_runtime_substrate_md(),
                "docs/aurora_run_bundle_boundary.md": _minimal_aurora_run_bundle_boundary_md(),
                "docs/aurora_run_bundle_v0_spec.md": _minimal_aurora_run_bundle_v0_spec_md(),
                **_minimal_substrate_src_files(),
                **_minimal_seam_contract_src_files(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_aurora_run_bundle_boundary_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                "docs/runtime_substrate.md": _minimal_runtime_substrate_md(),
                "docs/runtime_seam_framing.md": _minimal_runtime_seam_framing_md(),
                "docs/aurora_run_bundle_v0_spec.md": _minimal_aurora_run_bundle_v0_spec_md(),
                **_minimal_substrate_src_files(),
                **_minimal_seam_contract_src_files(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_aurora_run_bundle_v0_spec_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                "docs/runtime_substrate.md": _minimal_runtime_substrate_md(),
                "docs/runtime_seam_framing.md": _minimal_runtime_seam_framing_md(),
                "docs/aurora_run_bundle_boundary.md": _minimal_aurora_run_bundle_boundary_md(),
                **_minimal_substrate_src_files(),
                **_minimal_seam_contract_src_files(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_reference_to_aurora_run_bundle_v0_spec_in_aurora_md_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_aurora = """# A

## Execution Phase Boundaries (locked)

## Program Roadmap (proposed)

Governance: `docs/runtime_surface_strategy.md`.
Substrate: `docs/runtime_substrate.md`.
Seam framing: `docs/runtime_seam_framing.md`.
ARB boundary: `docs/aurora_run_bundle_boundary.md`.

"""
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": bad_aurora,
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_substrate_package_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                "docs/runtime_substrate.md": _minimal_runtime_substrate_md(),
                "docs/runtime_seam_framing.md": _minimal_runtime_seam_framing_md(),
                "docs/aurora_run_bundle_boundary.md": _minimal_aurora_run_bundle_boundary_md(),
                "src/aurora/__init__.py": '"""A."""\n',
                "src/aurora/runtime/__init__.py": '"""R."""\n',
                **_minimal_seam_contract_src_files(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_seam_contract_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            del files["src/aurora/runtime/dispatcher.py"]
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)

    def test_missing_arb_v0_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": _minimal_readme(),
                "docs/aurora.md": _minimal_aurora_md(),
                "docs/runtime_surface_strategy.md": _minimal_runtime_surface_md(),
                **_substrate_docs_and_src(),
                ".github/workflows/ci.yml": _minimal_ci_workflow(),
            }
            del files["src/aurora/arb/writer.py"]
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
