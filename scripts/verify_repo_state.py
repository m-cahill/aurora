#!/usr/bin/env python3
"""Governance verifier for the aurora/ repository (stdlib only).

Writes machine-readable results under artifacts/ and exits non-zero on failure.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = REPO_ROOT / "artifacts"

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


def _git_ls_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
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


def _scan_workflows(repo_root: Path) -> list[dict]:
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
    return issues


def main() -> int:
    checks: list[dict] = []
    ok = True

    try:
        tracked = _git_ls_files()
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

    readme = REPO_ROOT / "README.md"
    canon = REPO_ROOT / "docs" / "aurora.md"

    readme_ok = readme.is_file()
    checks.append({"id": "readme_exists", "ok": readme_ok})
    ok &= readme_ok

    canon_ok = canon.is_file()
    checks.append({"id": "canonical_doc_exists", "ok": canon_ok})
    ok &= canon_ok

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

    link_issues = _scan_markdown_links(REPO_ROOT, tracked)
    link_ok = not link_issues
    checks.append({"id": "markdown_relative_links", "ok": link_ok, "issues": link_issues})
    ok &= link_ok

    wf_issues = _scan_workflows(REPO_ROOT)
    wf_ok = not wf_issues
    checks.append({"id": "workflow_policy", "ok": wf_ok, "issues": wf_issues})
    ok &= wf_ok

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "ok": ok,
        "repo_root": str(REPO_ROOT),
        "checks": checks,
    }
    out_json = ARTIFACTS_DIR / "repo_verification.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary_lines = [
        f"repo_verification: {'PASS' if ok else 'FAIL'}",
        f"checks: {len(checks)}",
    ]
    if not ok:
        failed = [c["id"] for c in checks if not c.get("ok")]
        summary_lines.append("failed: " + ", ".join(failed))
    (ARTIFACTS_DIR / "verification_summary.txt").write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
