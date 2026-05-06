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

## Release tag (**M39** — **`v0.1.0`**)

- **Tag:** **`v0.1.0`** (annotated) — tag object **`11d4bb1e7f9d24700deddbfb0833e44e227c1888`**, target commit **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`** (merge of **PR** **#51** — release-lock), tagger timestamp **2026-05-06T23:32:35Z** UTC.
- **Release-lock PR** **#51** — final PR head **`b0b5643913dd3b803ef0be5a25579eaf973b7b7b`**; **`ci` / `repo-safety`:** **`25466621338`** (push, job **`74721250439`**), **`25466623128`** (pull_request, job **`74721255546`**).
- **Post-merge `main` after release-lock:** **`ci` / `repo-safety`:** **`25467001467`** (job **`74722427884`**, head **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`**) — authoritative clean-environment signal including **`pip-audit`**.
- **Tag-push CI:** **`25467044831`** (job **`74722561540`**, **success**, ref **`v0.1.0`**, same tree as **`97edcdb`**).
- **Closeout-record PR** (branch **`m39-closeout-record`**): merge commit and **post-closeout** **`main` `ci` / `repo-safety`** run/job IDs **recorded in [`docs/aurora.md`](aurora.md)** after that PR merges — **ensure all documentation is updated as necessary**.

**Formal statement:** **[`docs/release_statement_v0.1.0.md`](release_statement_v0.1.0.md)**.

**Changelog:** **[`CHANGELOG.md`](../CHANGELOG.md)** — `v0.1.0` entry.

**M39 does not** add PyPI publication or a tag-driven release automation workflow unless separately authorized. **M38** evidence above remains unchanged in meaning (SBOM + ARB baseline are **not** full product lifecycle or SLA proof).

## See also

- **[`docs/aurora.md`](aurora.md)** — milestone ledger, maintenance posture, handoff surface.
- **[`docs/arb_performance_baseline.md`](arb_performance_baseline.md)** — methodology for ARB timing JSON.
- **[`DEVELOPMENT.md`](../DEVELOPMENT.md)** — install, **`make ci-local`**, and **`pip-audit`** caveats.
