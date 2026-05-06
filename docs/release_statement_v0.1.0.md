# AURORA v0.1.0 Release Statement

## Status

**AURORA v0.1.0** is a **bounded governed acoustic runtime and artifact substrate** release: governed Python/native **seams**, **ARB v0.1** on-disk bundle read/write/validate, truthful **CI**, and explicit **non-proofs**. It is **not** a full MediaPipe application, competition harness, or native correctness certification.

**Maintenance posture:** **Maintenance-only by default** for **`src/aurora/`** after **M31**; **M32–M39** were an authorized **public-release hardening** tranche without reopening runtime expansion by default.

**Release lock:** Documentation in this milestone finalizes the **v0.1.0** public record. The **annotated tag `v0.1.0`** is applied only after the M39 release-lock change merges to **`main`** and **post-merge `main`** shows green **`ci` / `repo-safety`** (see **[`docs/aurora.md`](aurora.md)** for exact PR/SHA/CI/tag evidence after closeout).

## Release artifact

- **Git tag:** **`v0.1.0`** (annotated), target commit recorded in **`docs/aurora.md`** after tagging.
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
