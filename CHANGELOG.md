# Changelog

## v0.1.0 — 2026-05-07

### Release status

**AURORA v0.1.0** documents the **bounded, governed runtime and ARB v0.1 artifact substrate** delivered through milestone **M31** (runtime closeout) and the **M32–M39** public-release hardening tranche. **Runtime code** under `src/aurora/` remains **maintenance-only by default** after **M31** unless a downstream-driven milestone explicitly authorizes otherwise.

**M39 release-lock** — **PR** **#51** merged **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`** (**2026-05-06T23:31:25Z** UTC). **PR head** **`b0b5643913dd3b803ef0be5a25579eaf973b7b7b`**. **`ci` / `repo-safety`:** **`25466621338`**, **`25466623128`**. **Post-merge `main`:** **`25467001467`**. **Annotated tag `v0.1.0`** — object **`11d4bb1e7f9d24700deddbfb0833e44e227c1888`**, target **`97edcdbfa334eec1c06231256ef5a2d27cf643a2`**, tagger **2026-05-06T23:32:35Z** UTC. **Tag-push CI:** **`25467044831`**. **M39 closeout-record PR** **#52** merged **`6c5fb8cbd5ab3c4494cbabeb92654b345776e29a`** (**2026-05-06T23:36:38Z** UTC); PR head **`6d6087d509ca2f7c724fa32ec15f2860c1fa2186`**; **`ci` / `repo-safety`:** **`25467131432`**, **`25467133735`**; final **`main`:** **`25467184587`** (job **`74722979968`**). **M39 completion (UTC):** **2026-05-06T23:37:04Z**.

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
