# Changelog

## v0.1.0 — 2026-05-07

### Release status

**AURORA v0.1.0** documents the **bounded, governed runtime and ARB v0.1 artifact substrate** delivered through milestone **M31** (runtime closeout) and the **M32–M39** public-release hardening tranche. **Runtime code** under `src/aurora/` remains **maintenance-only by default** after **M31** unless a downstream-driven milestone explicitly authorizes otherwise.

The **annotated Git tag `v0.1.0`** is created **after** the M39 release-lock pull request merges and **post-merge `main`** records green **`ci` / `repo-safety`** (see **[`docs/aurora.md`](docs/aurora.md)** for PR/SHA/CI/tag evidence after closeout).

### Delivered

- **Governed runtime seams** — `Dispatcher`, `LibraryLoader`, `SharedLibraryLoader`, bounded `AuroraImage` / `AuroraAudio`, and **structural** `NativeAudioDispatcher` + ctypes bindings (**fake-backed / patched** in CI — see **[`DEVELOPMENT.md`](DEVELOPMENT.md)**).
- **ARB v0.1** — normative docs; stdlib **`write_arb`**, **`read_arb`**, **`validate_arb`**, **`python -m aurora.arb`** (validate-only); canonical JSON and hashing per **[`docs/aurora_run_bundle_v0_spec.md`](docs/aurora_run_bundle_v0_spec.md)**.
- **Documentation and governance** — **[`docs/aurora.md`](docs/aurora.md)** (canonical record), ADRs (**[`docs/decisions/README.md`](docs/decisions/README.md)**), hand-curated public API (**[`docs/api/README.md`](docs/api/README.md)**), milestone summaries, operating manual, release evidence.
- **Local workflow parity (M37)** — **`Makefile`** targets and **[`DEVELOPMENT.md`](DEVELOPMENT.md)** *Local CI parity* (authoritative gate remains GitHub **`ci` / `repo-safety`**).
- **M38 evidence** — **[`docs/release_evidence.md`](docs/release_evidence.md)**, **[`docs/arb_performance_baseline.md`](docs/arb_performance_baseline.md)**; CI artifacts include **`arb_performance_baseline.json`** (**non-SLA**) and CycloneDX JSON from pinned **`pip-audit`** (**not** a full product lifecycle SBOM).

### Evidence

- Required check **`ci` / `repo-safety`** on **[`.github/workflows/ci.yml`](.github/workflows/ci.yml)** — verifier, Ruff, Mypy (strict), `unittest` + coverage thresholds, **`pip-audit`**, SBOM step, ARB performance script (see **[`docs/release_evidence.md`](docs/release_evidence.md)**).

### Explicit non-proofs

This release **does not** establish:

- **Native** shared-library execution proof (real Tasks/MediaPipe binary on CI or host).
- **Decode correctness** (audio bytes → validated samples for real codecs).
- **Graph / TFLite** correctness or **MediaPipe application parity**.
- **BirdCLEF**, **Kaggle-only** packaging, or **ORNITHOS** / **PANTANAL-1** implementation **inside** this repository.

See **[`docs/release_statement_v0.1.0.md`](docs/release_statement_v0.1.0.md)** and **[`docs/aurora.md`](docs/aurora.md)**.

### Deferred

- Post-v0.1.0 **maintenance** items (e.g. optional CI caching, branch retention, pre-commit) identified in audits — **not** M39 release blockers.
- **PyPI publication** and **release automation workflows** — **not** part of v0.1.0 unless separately authorized.

### References

- **[`docs/release_statement_v0.1.0.md`](docs/release_statement_v0.1.0.md)** — formal release statement.
- **[`docs/release_evidence.md`](docs/release_evidence.md)** — CI and artifact summary.
- **[`docs/aurora.md`](docs/aurora.md)** — authoritative project record and milestone evidence.
