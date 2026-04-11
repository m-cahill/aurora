# AURORA

**Acoustic Unified Runtime for Observable, Replayable Acoustics** — a governed acoustic runtime and MediaPipe refactor program, tracked as a Foundry-aligned case study.

## What AURORA is

AURORA turns a high-entropy, real-world perception stack into a **deterministic, artifact-bound, replayable** audio system with **explicit Python/native seams**, auditable outputs, and honest scope boundaries. It is **not** a casual whole-repo rewrite of MediaPipe and **not** a backdoor for copying upstream implementation into Foundry core.

This repository (`aurora/`) is the **only** tracked AURORA git repository in the workspace. The **canonical project record** is [`docs/aurora.md`](docs/aurora.md). For **practical day-to-day use** (imports, tests, verification), see [`docs/AURORA_OPERATING_MANUAL.md`](docs/AURORA_OPERATING_MANUAL.md).

## Current status

**v0.1 complete** (through milestone **M31**). Phases **A–D** are **closed** in the committed record. Default posture for **runtime code** under `src/aurora/` is **maintenance-only** unless a downstream-driven need explicitly authorizes new work.

An **explicit post-M31 public-release hardening tranche** (M32–M35) improves documentation, packaging readiness, and release hygiene **without** reopening runtime expansion or native proof by default. See [`docs/aurora.md`](docs/aurora.md).

## Why this project exists

- Prove **Foundry-style** discipline on a **real** codebase (not a toy demo).
- Preserve MediaPipe’s strengths while **governing** seams, dependencies, and proof claims.
- Provide a **stable handoff surface** for downstream bioacoustic work (ORNITHOS, PANTANAL-1) without coupling competition-only logic into the runtime repo.

## Public scope and explicit non-goals

**In scope for this repo (as delivered and bounded):**

- Governed **runtime substrate**: `Dispatcher`, `LibraryLoader`, `SharedLibraryLoader`, bounded `AuroraImage` / `AuroraAudio`, structural `NativeAudioDispatcher` and ctypes bindings (see [`DEVELOPMENT.md`](DEVELOPMENT.md) for what CI proves).
- **ARB v0.1** (AURORA Run Bundle): normative docs, stdlib **write / read / validate**, `python -m aurora.arb`, hashing and canonical JSON per spec.

**Not claimed by CI or docs:**

- Decode correctness for real audio codecs.
- Graph / TFLite / MediaPipe **application** parity.
- Real native Tasks library execution on CI or proof of correctness on a host binary.
- BirdCLEF submission harness, Kaggle-only packaging, or ORNITHOS/PANTANAL-1 implementation **inside** this repo (those belong downstream unless they also improve the **generic** runtime).

## Installation and local development

- **Python 3.11** (matches [`.python-version`](.python-version)).
- From the repository root: **`pip install -r requirements-dev.txt`** then **`pip install -e .`** so the **`aurora`** package is importable without setting **`PYTHONPATH`**. See **[`DEVELOPMENT.md`](DEVELOPMENT.md)** for verifier, Ruff, tests, and coverage commands.

**Compatibility:** you can still run with **`PYTHONPATH=src`** (as CI does) if you prefer not to install the package in editable mode.

Packaging metadata is declared in **[`pyproject.toml`](pyproject.toml)** (version **0.1.0**, setuptools, `src/` layout). There are **no** setuptools **console-script** entry points — use **`python -m aurora.arb`** for the ARB CLI.

## Documentation map

| Document | Role |
|----------|------|
| [`docs/aurora.md`](docs/aurora.md) | Canonical repo record: phases, milestones, boundaries, proof posture. |
| [`docs/AURORA_VISION.md`](docs/AURORA_VISION.md) | North-star vision and program framing. |
| [`docs/AURORA_OPERATING_MANUAL.md`](docs/AURORA_OPERATING_MANUAL.md) | How to use and verify the repo today. |
| [`docs/milestone_summaries/README.md`](docs/milestone_summaries/README.md) | Public narrative summaries for milestones **M01–M31** (index + one file per milestone). |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution expectations and boundaries. |
| [`SECURITY.md`](SECURITY.md) | Vulnerability reporting. |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Contributor Covenant code of conduct. |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | Tooling, CI behavior, and milestone-specific “what CI proves.” |
| [`docs/runtime_substrate.md`](docs/runtime_substrate.md) | First-party package layout and provenance. |
| [`docs/runtime_seam_framing.md`](docs/runtime_seam_framing.md) | Dispatcher / loader seams and async honesty. |
| [`docs/aurora_run_bundle_boundary.md`](docs/aurora_run_bundle_boundary.md) / [`docs/aurora_run_bundle_v0_spec.md`](docs/aurora_run_bundle_v0_spec.md) | ARB boundary and v0.1 on-disk spec. |

## Repository boundary rules

- **Only `aurora/` is a git repository** for AURORA work; do not initialize git at the workspace root.
- A sibling **`mediapipe/`** directory (when present) is a **read-only reference clone** — do not modify it as part of AURORA changes.
- **Do not** copy MediaPipe source from `mediapipe/` into `aurora/`. Architectural learning is allowed; code transfer is not.

## Downstream: ORNITHOS and PANTANAL-1

**ORNITHOS** is the intended **domain model stack** (training, scoring, representations) that **consumes** released AURORA surfaces.

**PANTANAL-1** is the intended **BirdCLEF / deployment** narrative that may depend on AURORA and ORNITHOS artifacts.

Dependency direction is **one-way**: AURORA does not depend on ORNITHOS or PANTANAL-1. See [`docs/aurora.md`](docs/aurora.md) for the full charter.

## Proof posture

Required GitHub check: **`ci` / `repo-safety`**. When green, CI reflects the **declared** bar in [`DEVELOPMENT.md`](DEVELOPMENT.md): verifier, Ruff, **Mypy** (strict on `src/aurora/`), `unittest` with coverage, **100% line / 100% branch** on `src/aurora/`, and **`pip-audit`** on the installed dev environment (**M34**). Green CI does **not** override the explicit non-proofs above.

## Contributing and governance

- Prefer **small, reversible** changes with milestone-style acceptance criteria; the project record in [`docs/aurora.md`](docs/aurora.md) is the source of truth for what was proved and what was not.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md); for tooling and CI, see [`DEVELOPMENT.md`](DEVELOPMENT.md) and the operating manual.

A separate **`docs/`** tree at the **workspace** root (outside this repo) may hold local governance; it must **not** be committed into `aurora/` unless you intentionally add public material here. The repository verifier rejects common **private workspace-style** path prefixes if they appear in the tracked tree (for example **`docs/prompts/`**, **`docs/manuals/`**, **`docs/milestones/`**).
