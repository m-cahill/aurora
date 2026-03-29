#!/usr/bin/env python3
"""Governance verifier for the aurora/ repository (stdlib only).

Writes machine-readable results under artifacts/ and exits non-zero on failure.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

# M05: tracked first-party package paths (must be git-tracked).
SUBSTRATE_REQUIRED_FILES = (
    "src/aurora/__init__.py",
    "src/aurora/runtime/__init__.py",
    "src/aurora/runtime/surface.py",
)

# M06: seam contract modules (structural presence only; not runtime validation).
# M07: concrete shared-library loader (implementation file; tracked for governance).
SEAM_CONTRACT_REQUIRED_FILES = (
    "src/aurora/runtime/dispatcher.py",
    "src/aurora/runtime/library_loader.py",
    "src/aurora/runtime/errors.py",  # M13 — internal runtime error base (structural presence)
    "src/aurora/runtime/shared_library_loader.py",
    "src/aurora/runtime/image.py",  # M08 — bounded image seam (structural presence only)
)

# Headings that M01 established as required continuity signals.
REQUIRED_HEADING_SUBSTRINGS = (
    "Execution Phase Boundaries (locked)",
    "Program Roadmap (proposed)",
)

# Markdown link target: [text](url)
MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")

# Floating runner labels (forbidden in .github/workflows).
FLOATING_RUNNER_RE = re.compile(r"^\s*runs-on:\s*.*-latest\s*$", re.IGNORECASE)

# Soft-fail on enforcement (forbidden in workflows).
CONTINUE_ON_ERROR_RE = re.compile(
    r"^\s*continue-on-error:\s*true\s*$", re.IGNORECASE | re.MULTILINE
)

# `uses:` step lines: list form (`- uses:`) or nested under `name:` (`uses:` only).
USES_LINE_RE = re.compile(
    r"^\s*(?:-\s+)?uses:\s*(.+?)(?:\s+#.*)?$"
)

# Full 40-char Git commit SHA (GitHub Actions pin rule).
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)

# Workflow-level `name:` must appear before `jobs:` so we do not match step names.
JOBS_START_RE = re.compile(r"^jobs:\s*$", re.MULTILINE)


def _git_ls_files(repo_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git ls-files failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def _safe_tracked_path(path: str) -> tuple[bool, str | None]:
    """Return (ok, reason_if_not)."""
    if path.startswith("/") or path.startswith("\\"):
        return False, "absolute_path"
    norm = path.replace("\\", "/")
    parts = norm.split("/")
    if ".." in parts:
        return False, "parent_traversal"
    if norm.startswith("../") or norm == "..":
        return False, "parent_traversal"
    return True, None


def _readme_links_to_canonical_doc(readme_text: str) -> bool:
    return bool(re.search(r"\]\(\s*docs/aurora\.md\s*\)", readme_text))


def _mediapipe_import_issues(repo_root: Path, tracked: list[str]) -> list[dict]:
    """Disallow `import mediapipe` / `from mediapipe` under src/aurora/."""
    issues: list[dict] = []
    for rel in tracked:
        if not rel.startswith("src/aurora/") or not rel.endswith(".py"):
            continue
        fpath = repo_root / rel
        if not fpath.is_file():
            continue
        text = fpath.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as exc:
            issues.append(
                {
                    "file": rel,
                    "problem": "syntax_error",
                    "detail": str(exc),
                }
            )
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name == "mediapipe" or name.startswith("mediapipe."):
                        issues.append(
                            {
                                "file": rel,
                                "problem": "mediapipe_import",
                                "detail": name,
                            }
                        )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module
                if mod and (mod == "mediapipe" or mod.startswith("mediapipe.")):
                    issues.append(
                        {
                            "file": rel,
                            "problem": "mediapipe_import",
                            "detail": mod,
                        }
                    )
    return issues


def _missing_substrate_files(tracked: list[str]) -> list[str]:
    tracked_set = set(tracked)
    return [f for f in SUBSTRATE_REQUIRED_FILES if f not in tracked_set]


def _missing_seam_contract_files(tracked: list[str]) -> list[str]:
    tracked_set = set(tracked)
    return [f for f in SEAM_CONTRACT_REQUIRED_FILES if f not in tracked_set]


def _scan_markdown_links(repo_root: Path, tracked: list[str]) -> list[dict]:
    """Ensure relative markdown links do not resolve outside the repo."""
    issues: list[dict] = []
    md_files = [p for p in tracked if p.endswith(".md")]
    for rel in md_files:
        fpath = repo_root / rel
        if not fpath.is_file():
            continue
        text = fpath.read_text(encoding="utf-8")
        parent = fpath.parent
        for raw in MD_LINK_RE.findall(text):
            target = raw.strip().strip("<>").split()[0]
            if '"' in target:
                target = target.split('"', 1)[0].strip()
            if "'" in target:
                target = target.split("'", 1)[0].strip()
            if not target or target.startswith("#"):
                continue
            scheme = target.split(":", 1)[0].lower()
            if scheme in {"http", "https", "mailto"}:
                continue
            if target.startswith("//"):
                continue
            resolved = (parent / target).resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                issues.append(
                    {
                        "file": rel,
                        "target": target,
                        "problem": "link_resolves_outside_repo",
                    }
                )
                continue
            if not resolved.is_file():
                issues.append(
                    {
                        "file": rel,
                        "target": target,
                        "problem": "missing_target",
                    }
                )
    return issues


def _split_workflow_header_and_jobs(text: str) -> tuple[str, str]:
    """Return (text_before_jobs, text_from_jobs_onward)."""
    m = JOBS_START_RE.search(text)
    if not m:
        return text, ""
    return text[: m.start()], text[m.start() :]


def _workflow_name_is_ci(header: str) -> bool:
    """True if workflow-level name is exactly `ci` (quoted or not)."""
    return bool(
        re.search(
            r"^\s*name:\s*[\"']?ci[\"']?\s*(?:#.*)?$",
            header,
            re.MULTILINE,
        )
    )


def _workflow_has_repo_safety_job(jobs_section: str) -> bool:
    """True if a job key `repo-safety` exists under jobs:."""
    return bool(re.search(r"^\s+repo-safety:\s*$", jobs_section, re.MULTILINE))


def _check_ci_workflow_identity(repo_root: Path) -> list[dict]:
    """Ensure a workflow exposes the stable check identity `ci` / `repo-safety`."""
    issues: list[dict] = []
    wf_dir = repo_root / ".github" / "workflows"
    if not wf_dir.is_dir():
        issues.append(
            {
                "problem": "missing_workflows_dir",
            }
        )
        return issues

    found = False
    for yml in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
        text = yml.read_text(encoding="utf-8")
        header, jobs_sec = _split_workflow_header_and_jobs(text)
        if _workflow_name_is_ci(header) and _workflow_has_repo_safety_job(jobs_sec):
            found = True
            break

    if not found:
        issues.append(
            {
                "problem": "missing_ci_repo_safety_identity",
                "detail": "expected workflow name: ci and job key: repo-safety",
            }
        )
    return issues


def _check_uses_external_pin(uses_value: str) -> list[dict]:
    """Validate external `uses:` strings use a full 40-char SHA after the last @."""
    issues: list[dict] = []
    val = uses_value.strip()
    if val.startswith(("./", ".\\")):
        return issues
    if val.startswith("docker://"):
        return issues
    if "@" not in val:
        issues.append(
            {
                "problem": "uses_missing_at_ref",
                "detail": val,
            }
        )
        return issues
    _spec, ref = val.rsplit("@", 1)
    ref = ref.strip()
    if not FULL_SHA_RE.match(ref):
        issues.append(
            {
                "problem": "uses_not_full_sha",
                "detail": val,
                "ref": ref,
            }
        )
    return issues


def _scan_workflows(repo_root: Path) -> list[dict]:
    """Workflow truthfulness: soft-fail, floating runners, full SHA pins on uses."""
    issues: list[dict] = []
    wf_dir = repo_root / ".github" / "workflows"
    if not wf_dir.is_dir():
        return issues
    for yml in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
        text = yml.read_text(encoding="utf-8")
        rel = str(yml.relative_to(repo_root)).replace("\\", "/")
        if CONTINUE_ON_ERROR_RE.search(text):
            issues.append(
                {
                    "file": rel,
                    "problem": "continue_on_error_true",
                }
            )
        for line in text.splitlines():
            if FLOATING_RUNNER_RE.match(line):
                issues.append(
                    {
                        "file": rel,
                        "problem": "floating_runner_latest",
                        "detail": line.strip(),
                    }
                )
            m = USES_LINE_RE.match(line)
            if not m:
                continue
            raw_val = m.group(1).strip().strip('"').strip("'")
            for pin_issue in _check_uses_external_pin(raw_val):
                issues.append({"file": rel, **pin_issue})
    return issues


def verify_repository(repo_root: Path) -> int:
    """Run all governance checks; write artifacts under repo_root/artifacts. Return exit code."""
    repo_root = repo_root.resolve()
    artifacts_dir = repo_root / "artifacts"
    checks: list[dict] = []
    ok = True

    try:
        tracked = _git_ls_files(repo_root)
    except RuntimeError as exc:
        checks.append(
            {
                "id": "git_ls_files",
                "ok": False,
                "detail": str(exc),
            }
        )
        ok = False
        tracked = []

    readme = repo_root / "README.md"
    canon = repo_root / "docs" / "aurora.md"

    readme_ok = readme.is_file()
    checks.append({"id": "readme_exists", "ok": readme_ok})
    ok &= readme_ok

    canon_ok = canon.is_file()
    checks.append({"id": "canonical_doc_exists", "ok": canon_ok})
    ok &= canon_ok

    runtime_strategy = repo_root / "docs" / "runtime_surface_strategy.md"
    rs_doc_ok = runtime_strategy.is_file()
    checks.append({"id": "runtime_surface_strategy_doc_exists", "ok": rs_doc_ok})
    ok &= rs_doc_ok

    runtime_substrate = repo_root / "docs" / "runtime_substrate.md"
    rsub_doc_ok = runtime_substrate.is_file()
    checks.append({"id": "runtime_substrate_doc_exists", "ok": rsub_doc_ok})
    ok &= rsub_doc_ok

    runtime_seam_framing = repo_root / "docs" / "runtime_seam_framing.md"
    rsf_doc_ok = runtime_seam_framing.is_file()
    checks.append({"id": "runtime_seam_framing_doc_exists", "ok": rsf_doc_ok})
    ok &= rsf_doc_ok

    if readme_ok:
        readme_text = readme.read_text(encoding="utf-8")
        link_ok = _readme_links_to_canonical_doc(readme_text)
        checks.append({"id": "readme_relative_link_to_docs_aurora", "ok": link_ok})
        ok &= link_ok

    if canon_ok:
        body = canon.read_text(encoding="utf-8")
        missing = [h for h in REQUIRED_HEADING_SUBSTRINGS if h not in body]
        heading_ok = not missing
        checks.append(
            {
                "id": "canonical_doc_required_sections",
                "ok": heading_ok,
                "missing": missing,
            }
        )
        ok &= heading_ok

        ref_rs = "runtime_surface_strategy.md" in body
        checks.append(
            {
                "id": "canonical_doc_references_runtime_surface_strategy",
                "ok": ref_rs,
            }
        )
        ok &= ref_rs

        ref_sub = "runtime_substrate.md" in body
        checks.append(
            {
                "id": "canonical_doc_references_runtime_substrate",
                "ok": ref_sub,
            }
        )
        ok &= ref_sub

        ref_seam = "runtime_seam_framing.md" in body
        checks.append(
            {
                "id": "canonical_doc_references_runtime_seam_framing",
                "ok": ref_seam,
            }
        )
        ok &= ref_seam

    env_hits = [
        p
        for p in tracked
        if p == ".env" or p.startswith(".env.") or p.endswith("/.env") or "/.env." in p
    ]
    env_ok = not env_hits
    checks.append({"id": "no_tracked_dotenv", "ok": env_ok, "paths": env_hits})
    ok &= env_ok

    bad_paths: list[dict] = []
    mediapipe_hits: list[str] = []
    for p in tracked:
        safe, reason = _safe_tracked_path(p)
        if not safe:
            bad_paths.append({"path": p, "reason": reason})
        norm = p.replace("\\", "/")
        if norm == "mediapipe" or norm.startswith("mediapipe/"):
            mediapipe_hits.append(p)
    path_ok = not bad_paths
    checks.append({"id": "tracked_paths_safe", "ok": path_ok, "violations": bad_paths})
    ok &= path_ok

    mp_ok = not mediapipe_hits
    checks.append(
        {
            "id": "no_tracked_mediapipe_tree",
            "ok": mp_ok,
            "paths": mediapipe_hits,
        }
    )
    ok &= mp_ok

    missing_sub = _missing_substrate_files(tracked)
    sub_files_ok = not missing_sub
    checks.append(
        {
            "id": "substrate_package_files_tracked",
            "ok": sub_files_ok,
            "missing": missing_sub,
        }
    )
    ok &= sub_files_ok

    missing_seam = _missing_seam_contract_files(tracked)
    seam_files_ok = not missing_seam
    checks.append(
        {
            "id": "seam_contract_files_tracked",
            "ok": seam_files_ok,
            "missing": missing_seam,
        }
    )
    ok &= seam_files_ok

    mp_import_issues = _mediapipe_import_issues(repo_root, tracked)
    mp_import_ok = not mp_import_issues
    checks.append(
        {
            "id": "no_mediapipe_imports_under_src_aurora",
            "ok": mp_import_ok,
            "issues": mp_import_issues,
        }
    )
    ok &= mp_import_ok

    link_issues = _scan_markdown_links(repo_root, tracked)
    link_ok = not link_issues
    checks.append({"id": "markdown_relative_links", "ok": link_ok, "issues": link_issues})
    ok &= link_ok

    ci_id_issues = _check_ci_workflow_identity(repo_root)
    ci_id_ok = not ci_id_issues
    checks.append(
        {
            "id": "ci_workflow_identity",
            "ok": ci_id_ok,
            "issues": ci_id_issues,
        }
    )
    ok &= ci_id_ok

    wf_issues = _scan_workflows(repo_root)
    wf_ok = not wf_issues
    checks.append({"id": "workflow_policy", "ok": wf_ok, "issues": wf_issues})
    ok &= wf_ok

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "ok": ok,
        "repo_root": str(repo_root),
        "checks": checks,
    }
    out_json = artifacts_dir / "repo_verification.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary_lines = [
        f"repo_verification: {'PASS' if ok else 'FAIL'}",
        f"checks: {len(checks)}",
    ]
    if not ok:
        failed = [c["id"] for c in checks if not c.get("ok")]
        summary_lines.append("failed: " + ", ".join(failed))
    (artifacts_dir / "verification_summary.txt").write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )

    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify aurora/ governance state.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/).",
    )
    args = parser.parse_args()
    root = (
        args.repo_root.resolve()
        if args.repo_root is not None
        else Path(__file__).resolve().parent.parent
    )
    return verify_repository(root)


if __name__ == "__main__":
    raise SystemExit(main())
