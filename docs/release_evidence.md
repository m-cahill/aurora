# Release evidence (M38)

This document summarizes **what the repository’s automation and gates currently support** as **evidence toward** a public release. It is **not** a release statement, **not** a product warranty, and **not** a substitute for downstream compliance review. The **authoritative** project record remains **[`docs/aurora.md`](aurora.md)**.

## What CI proves today

- **Workflow:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — job id **`repo-safety`** (workflow name **`ci`**).
- **Required check (identity):** **`ci` / `repo-safety`** — branch protection should require this check **by that name**.
- **Steps (high level):** repository verifier (**`scripts/verify_repo_state.py`**), **Ruff**, **`compileall`**, **Mypy** (**strict**, **`src/aurora`** only), **`unittest`** with **Coverage** (line and branch thresholds enforced via **`scripts/check_coverage_thresholds.py`**), **`pip-audit`** on the **full** installed dev environment.
- **Supply-chain / SBOM evidence (M38):** after a successful vulnerability audit, CI emits **CycloneDX JSON** via **`pip-audit -f cyclonedx-json -o artifacts/sbom.cdx.json`** (dependency/vulnerability-oriented SBOM surface from the audited environment — **not** a complete product lifecycle SBOM).
- **ARB performance evidence (M38):** CI runs **`scripts/measure_arb_performance.py`** and uploads **`artifacts/arb_performance_baseline.json`** (see [`docs/arb_performance_baseline.md`](arb_performance_baseline.md)).

## Quality gates (posture)

| Area | Posture |
|------|---------|
| **Tests** | **`unittest`**; coverage **scoped** to **`src/aurora`** (see [`.coveragerc`](../.coveragerc)). |
| **Coverage** | **100%** line and **100%** branch **targets** on **`src/aurora`** where enforced (see **`DEVELOPMENT.md`** / **`check_coverage_thresholds.py`**). |
| **Typing** | **Mypy strict** on **`src/aurora`**. |
| **Lint** | **Ruff** on **`scripts`**, **`tests`**, **`src`**. |
| **Vulnerabilities** | **`pip-audit`** on CI (**pinned** in [`requirements-dev.txt`](../requirements-dev.txt)); weekly **Dependabot** on **pip** and **github-actions** ([`.github/dependabot.yml`](../.github/dependabot.yml)). |

## CI artifacts (evidence files)

Uploaded as workflow artifact **`ci-artifacts`** (directory **`artifacts/`**), including at minimum:

- **`artifacts/coverage.json`**
- **`artifacts/ruff.json`**, **`artifacts/unittest.txt`**, **`artifacts/compileall_ok.txt`** (supporting logs)
- **`artifacts/arb_performance_baseline.json`** (M38 — ARB API baseline timings; **non-SLA**)
- **`artifacts/sbom.cdx.json`** (M38 — CycloneDX JSON from **`pip-audit`**)

## Local reproduction

[`Makefile`](../Makefile) targets:

- **`make performance`** — ARB baseline JSON (requires editable install or `PYTHONPATH=src`; see [`docs/arb_performance_baseline.md`](arb_performance_baseline.md)).
- **`make sbom`** — CycloneDX JSON via **`pip-audit`** (same caveat as **`pip-audit`** locally: **polluted global environments** can differ from clean CI — **CI is authoritative**; see [`DEVELOPMENT.md`](../DEVELOPMENT.md)).
- **`make release-evidence`** — **`coverage`**, then **`performance`**, then **`sbom`** (optional aggregate).

## Explicit non-proofs (binding)

As in **[`aurora.md`](aurora.md)** and **[`docs/AURORA_OPERATING_MANUAL.md`](AURORA_OPERATING_MANUAL.md)**:

- **No** claim of **native** shared-library execution proof (including on CI).
- **No** **decode correctness** or **graph / TFLite** correctness.
- **No** **MediaPipe application parity**.
- **No** **BirdCLEF** or **PANTANAL-1** implementation in this repository.

SBOM and ARB baseline artifacts **do not** override these limits.

## Release tag

**M39 (v0.1.0 public release lock):** the **annotated** Git tag is **`v0.1.0`**. The tag is created **only after** the M39 release-lock pull request merges to **`main`** and **post-merge `main`** records green **`ci` / `repo-safety`** — see **`docs/aurora.md`** for authoritative PR/merge/tag/CI evidence (and any closeout-record PR).

**Formal statement:** **[`docs/release_statement_v0.1.0.md`](release_statement_v0.1.0.md)**.

**Changelog:** **[`CHANGELOG.md`](../CHANGELOG.md)** — `v0.1.0` entry.

**M39 does not** add PyPI publication or a tag-driven release automation workflow unless separately authorized. **M38** evidence above remains unchanged in meaning (SBOM + ARB baseline are **not** full product lifecycle or SLA proof).

## See also

- **[`docs/aurora.md`](aurora.md)** — milestone ledger, maintenance posture, handoff surface.
- **[`docs/arb_performance_baseline.md`](arb_performance_baseline.md)** — methodology for ARB timing JSON.
- **[`DEVELOPMENT.md`](../DEVELOPMENT.md)** — install, **`make ci-local`**, and **`pip-audit`** caveats.
