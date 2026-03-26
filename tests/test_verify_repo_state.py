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

"""


def _minimal_readme() -> str:
    return """# T

[x](docs/aurora.md)
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
                ".github/workflows/ci.yml": wf,
            }
            _init_git_repo(root, files)
            rc = verify_repo_state.verify_repository(root)
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
