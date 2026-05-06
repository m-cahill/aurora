# AURORA v0.1.0 Release Statement

## Status

**AURORA v0.1.0** is a **bounded governed acoustic runtime and artifact substrate** release: governed Python/native **seams**, **ARB v0.1** on-disk bundle read/write/validate, truthful **CI**, and explicit **non-proofs**. It is **not** a full MediaPipe application, competition harness, or native correctness certification.

**Maintenance posture:** **Maintenance-only by default** for **`src/aurora/`** after **M31**; **M32–M39** were an authorized **public-release hardening** tranche without reopening runtime expansion by default.

**Release lock:** **M39** release-lock **PR** **#51** merged **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`** (**2026-05-06T23:31:25Z** UTC). **Post-merge `main` `ci` / `repo-safety`:** **`25467001467`** (**success**). **Annotated tag `v0.1.0`** — object **`11d4bb1e7f9d24700deddbfb0833e44e227c1888`**, target **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`**, tagger **2026-05-06T23:32:35Z** UTC; tag-push CI **`25467044831`**. **Closeout / ledger:** **PR** **#52**, **#53**, **#54** — canonical **[`docs/aurora.md`](aurora.md)**. **Final `main` HEAD (documentation parity):** **`2b1cd2ee835cd75a47ce360458e83727dd55cd62`**; final green **`ci` / `repo-safety` on `main`:** **`25467353106`** (job **`74723491561`**). **ensure all documentation is updated as necessary**

## Release artifact

- **Git tag:** **`v0.1.0`** (annotated), target **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`**, tag object **`11d4bb1e7f9d24700deddbfb0833e44e227c1888`** (see **[`docs/aurora.md`](aurora.md)**).
- **Python package (source layout):** version **0.1.0** in **`pyproject.toml`** — editable install documented in **`README.md`** / **`DEVELOPMENT.md`**. **No PyPI publication** is implied by this release statement.

## Public handoff surface

Downstream may treat as contractual **public** surface (categories — detail in **`docs/aurora.md`**):

- **`aurora.runtime`** — seam protocols, loader, bounded **`AuroraImage`** / **`AuroraAudio`**, substrate metadata (**as documented and tested**).
- **`aurora.arb`** — **ARB v0.1** APIs and validate-only CLI (**as specified** in **`docs/aurora_run_bundle_v0_spec.md`**).
- **`docs/api/README.md`** — hand-curated index aligned with **`__all__`**.
- **ADRs** — **`docs/decisions/`** (stdlib boundary, fake-backed CI, ARB versioning, downstream direction).

## What this release proves

- **Governance and CI honesty** — required **`ci` / `repo-safety`**: verifier, Ruff, Mypy strict on **`src/aurora/`**, `unittest` with **100%** line / **100%** branch coverage on that surface (see **`scripts/check_coverage_thresholds.py`**), **`pip-audit`** on the dev install, CycloneDX JSON via pinned **`pip-audit`**, ARB timing JSON from **`scripts/measure_arb_performance.py`** (**non-SLA** methodology in **`docs/arb_performance_baseline.md`**).
- **Structural seams** — injection-friendly **`Dispatcher`** / **`LibraryLoader`**; **`AuroraImage`** / **`AuroraAudio`** routing; **`NativeAudioDispatcher`** binding surface **tested with fakes / patched `CDLL`** as documented.
- **ARB v0.1** — write, read, separate validate, CLI validator; canonical JSON and root hash workflow per normative spec docs.

## What this release does not prove

- **Native execution** of a real upstream Tasks / MediaPipe shared library on CI or any host.
- **Decode correctness** for real audio codecs.
- **Graph / TFLite** correctness or **MediaPipe application parity**.
- **BirdCLEF**, **PANTANAL-1**, or competition-only packaging **as implemented in this repo** (downstream repos are out of scope here).

## CI and evidence

- Summary: **[`docs/release_evidence.md`](release_evidence.md)**.
- **M38** ARB performance JSON is **baseline / non-SLA** evidence only — not a performance SLO or product SLA.
- **M38** SBOM (`pip-audit` CycloneDX) reflects the **audited CI environment** — **not** a complete enterprise product SBOM lifecycle.

## Security and supply-chain evidence

- Pinned dev tooling (**`requirements-dev.txt`**); **`pip-audit`** on CI; weekly Dependabot for **pip** and **github-actions**; external Actions pinned to **full SHAs** in **`ci.yml`**. Details: **`docs/release_evidence.md`**, **`DEVELOPMENT.md`**.

## Performance evidence

- **[`docs/arb_performance_baseline.md`](arb_performance_baseline.md)** — methodology; CI artifact **`arb_performance_baseline.json`** — **non-SLA**.

## Downstream boundary

- **One-way** dependency: **AURORA** does not depend on **ORNITHOS** or **PANTANAL-1**; downstream may consume **released** surfaces. See **`docs/aurora.md`** — *Proposed downstream repo layout and dependency directionality*.

## Deferred work

- Optional **maintenance** improvements (CI cache, branch cleanup, etc.) from audits — **post-v0.1.0**, not release blockers.
- **PyPI / release automation** — only if explicitly authorized in a future milestone.

## References

- **`docs/aurora.md`** — canonical record; **ensure all documentation is updated as necessary** at milestone boundaries.
- **`CHANGELOG.md`** (repository root) — v0.1.0 changelog entry.
- **`docs/release_evidence.md`** — CI artifact and gate summary.
