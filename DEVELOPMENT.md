# AURORA — development workflow

This file describes **what exists today** in the `aurora/` repository: governance checks, the first-party runtime substrate under `src/aurora/`, lint, and tests. For orientation and boundaries (mental model, non-proofs, doc map), see [`docs/AURORA_OPERATING_MANUAL.md`](docs/AURORA_OPERATING_MANUAL.md). It is not a full roadmap for MediaPipe fork work (that lives in workspace context docs).

## Prerequisites

- **Python 3.11** (matches CI).
- **Git** (the verifier uses `git ls-files`).

## Install dev tools

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Run the repository verifier locally

From the repository root (`aurora/`):

```bash
mkdir -p artifacts
python scripts/verify_repo_state.py
```

Results are written under `artifacts/` (`repo_verification.json`, `verification_summary.txt`). The `artifacts/` directory is gitignored.

## Run Ruff locally

```bash
ruff check scripts tests src
```

## Run tests locally (including runtime substrate)

Substrate tests import the `aurora` package from `src/`. Set **`PYTHONPATH=src`** (or the Windows equivalent) so imports resolve the same way as in CI.

**Linux / macOS:**

```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
```

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Coverage (first-party `src/aurora` only; M11 line + M12 branch)

From the repository root, with dev tools installed (`pip install -r requirements-dev.txt`):

**Linux / macOS:**

```bash
export PYTHONPATH=src
coverage erase
coverage run -m unittest discover -s tests -v
coverage report
coverage json -o artifacts/coverage.json
python scripts/check_coverage_thresholds.py
```

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH = "src"
coverage erase
coverage run -m unittest discover -s tests -v
coverage report
coverage json -o artifacts/coverage.json
python scripts/check_coverage_thresholds.py
```

Configuration is in **`.coveragerc`**: measurement is limited to **`src/aurora/`** (the first-party runtime package), with **`branch = True`** so branch arcs are recorded. Governance scripts such as `scripts/verify_repo_state.py` are **not** part of this coverage surface.

**Gates (M11 + M12):** Do not rely on **`report:fail_under`** in `.coveragerc` when branch coverage is enabled — coverage’s built-in fail-under uses a *combined* line+branch total. Instead, **`scripts/check_coverage_thresholds.py`** enforces **separate** floors: **line** (statement) coverage and **branch** (measured arcs) coverage, using totals from **`coverage json`**. Defaults are **100%** line and **100%** branch on the measured surface (see script constants).

## What CI proves (and what it does not)

The required GitHub status check is **`ci / repo-safety`** (workflow `ci`, job `repo-safety`).

When green, CI indicates:

- repository layout and documentation anchors enforced by `scripts/verify_repo_state.py` (README link to `docs/aurora.md`, required headings, presence of `docs/runtime_surface_strategy.md`, `docs/runtime_substrate.md`, `docs/runtime_seam_framing.md`, `docs/aurora_run_bundle_boundary.md` (M25), and `docs/aurora_run_bundle_v0_spec.md` (M26), references in `docs/aurora.md` (including `runtime_seam_framing.md`, `aurora_run_bundle_boundary.md`, and `aurora_run_bundle_v0_spec.md`), tracked substrate and **M06 seam contract** files plus **`src/aurora/runtime/errors.py` (M13)**, **`src/aurora/runtime/dispatch_tokens.py` (M14/M19)**, **`src/aurora/runtime/image_dispatch.py` (M15)**, **`src/aurora/runtime/audio_dispatch.py` (M19)**, **`src/aurora/runtime/audio_native_bindings.py` (M21)**, **`src/aurora/runtime/native_audio_dispatcher.py` (M21/M22)**, **`src/aurora/runtime/shared_library_loader.py` (M07)**, **`src/aurora/runtime/image.py` (M08)**, **`src/aurora/runtime/audio.py` (M19)** under `src/aurora/runtime/`, and **M27**/**M29** **`src/aurora/arb/`** package files (`__init__.py`, `canonical_json.py`, `hasher.py`, `reader.py`, `validator.py`, `writer.py`), no `mediapipe` imports under `src/aurora/`, no tracked `.env`, workflow policy including full SHA pins for external Actions, no `*-latest` runners on enforcement workflows, and the stable `ci` / `repo-safety` identity);
- **Ruff** on `scripts/`, `tests/`, and `src/`;
- **stdlib `unittest`** for the verifier, **runtime substrate** import/metadata tests, **M09 composed runtime smoke tests** (image) and **M19 audio smoke tests** in `tests/test_runtime_smoke.py`, and **M27/M28/M29 ARB** tests in `tests/test_arb_*.py` (with **`PYTHONPATH=src`**);
- **line and branch coverage** for **`src/aurora/`** via **`coverage run`** (with **`branch = True`**) + **`coverage report`** + **`coverage json`**, then **`scripts/check_coverage_thresholds.py`** for **separate** line and branch regression floors (JSON under **`artifacts/coverage.json`** on CI);
- **bytecode compile** sanity for `scripts/`, `tests/`, and `src/`.

### M05 substrate (what it proves)

- A **first-party** package exists at `src/aurora/` and is **importable** in CI.
- **`docs/runtime_substrate.md`** records provenance and explicit non-claims.
- Tests assert **metadata contract** and **no `mediapipe` imports** in the new tree.

### M06 seam contracts (what they prove)

- **`Dispatcher`** and **`LibraryLoader`** are available as minimal `typing.Protocol` definitions under `src/aurora/runtime/` (see `docs/runtime_seam_framing.md`).
- CI and the verifier check **structural presence** and documentation cross-links — **not** native loading correctness, MediaPipe parity, or `image.py` migration (migration is explicitly out of scope for M06).

### M07 concrete loader (what it proves)

- **`SharedLibraryLoader`** (`src/aurora/runtime/shared_library_loader.py`) implements **`LibraryLoader`**: explicit constructor path, `ctypes.CDLL`-backed load, per-instance memoization of the handle (and of load failure), and **`SharedLibraryLoadError`** on `OSError`.
- Unit tests patch **`ctypes.CDLL`** — they do **not** prove a real native library loads on the CI host.
- The **bounded first-party image seam** is **M08**, not M07 (see below).

### M08 bounded image seam (what it proves)

- **`AuroraImage`** / **`ImageCreationError`** in `src/aurora/runtime/image.py`: `from_file` / `from_bytes` route through injected **`Dispatcher`** and **`LibraryLoader`**; **`image.py` does not call `ctypes` or `CDLL`** (only the loader seam loads native code).
- Unit tests use **fakes** — they do **not** prove decode correctness, MediaPipe parity, or real native execution.

### M09 composed runtime smoke (what it proves)

- **`tests/test_runtime_smoke.py`** exercises the **composed** first-party seam chain: real **`SharedLibraryLoader`** with **`ctypes.CDLL` patched** (no real host libraries), real **`AuroraImage`**, and a **recording fake `Dispatcher`** — happy paths (`from_file` / `from_bytes`) plus loader and dispatch failure paths surfaced as **`ImageCreationError`** with chaining preserved.
- This is **not** duplicate M08 unit coverage: smoke tests prove **`AuroraImage` → `SharedLibraryLoader` → patched `CDLL`** together with **`Dispatcher.dispatch`**, not isolated fakes alone.

### M13 runtime surface coherence (what it proves)

- **`src/aurora/runtime/errors.py`** defines **`AuroraRuntimeError`**, a **shared internal base** for first-party seam exceptions. **`SharedLibraryLoadError`**, **`ImageCreationError`**, and **`AudioCreationError`** (M19) subclass it; **public exception names, messages, and `raise … from …` chaining** match M07/M08/M19 behavior.
- **`AuroraImage`** uses a **private** `_from_dispatch` helper so `from_file` / `from_bytes` share one implementation path; **no new public API** was added for that helper.
- **`AuroraRuntimeError`** is **internal** to the runtime package (not re-exported from `aurora.runtime.__all__`); callers continue to catch **`ImageCreationError`** / **`AudioCreationError`** / **`SharedLibraryLoadError`** as before.

### M13 non-goals (explicit)

- **No shared lifecycle or resource-management abstraction** was introduced: M13 **inspected** the current seam modules for reusable lifecycle/cleanup patterns and found **insufficient real duplication** to justify extraction at this time.
- **No** `VisionTaskBase` / `AudioTaskBase`, upstream Tasks wrappers, kernel work, or artifact/runtime behavior.

### M14 dispatch operation tokens (what it proves)

- **`src/aurora/runtime/dispatch_tokens.py`** holds the **string tokens** passed as the first argument to **`Dispatcher.dispatch`** for **`AuroraImage.from_file`** / **`from_bytes`** (`IMAGE_FROM_FILE`, `IMAGE_FROM_BYTES`). **`image.py`** and tests import these constants so the seam vocabulary has a **single source of truth**; values match the pre-M14 literals byte-for-byte.
- Tokens are **internal** runtime vocabulary (not re-exported from `aurora.runtime.__all__`). A **value-stability** unittest pins the exact strings against drift.

### M14 non-goals (explicit)

- **No** new operations, domains, or **`Dispatcher`** / **`LibraryLoader`** protocol changes.
- **No** `VisionTaskBase` / `AudioTaskBase`, lifecycle extraction, logging migration, or upstream Tasks migration.

### M15 AuroraImage dispatch invocation contract (what it proves)

- **`src/aurora/runtime/image_dispatch.py`** is the **single source of truth** for how **`AuroraImage`** acquires the shared-library handle and invokes **`Dispatcher.dispatch`** with the M14 tokens and frozen positional order **(token, payload, library handle)**. Helpers **`dispatch_image_from_file`** / **`dispatch_image_from_bytes`** return the opaque native handle only; **`ImageCreationError`** wrapping and **`AuroraImage`** construction remain in **`image.py`** (private **`_from_dispatch`** unchanged in role).
- The module is **internal** (not re-exported from `aurora.runtime.__all__`). **`scripts/verify_repo_state.py`** requires the file as part of the tracked seam set. Unittests pin token values (M14) and dispatch argument ordering (M08/M14/M15).

### M15 non-goals (explicit)

- **No** new public runtime API, **`Dispatcher`** / **`LibraryLoader`** protocol changes, or token value changes.
- **No** `VisionTaskBase` / `AudioTaskBase`, lifecycle extraction, logging migration, kernel work, or upstream Tasks migration.

### M19 bounded audio seam (what it proves)

- **First code-bearing Phase D slice (Candidate A):** **`AuroraAudio`** / **`AudioCreationError`** in **`src/aurora/runtime/audio.py`**, parallel in shape to **`AuroraImage`**, routing **`from_file`** / **`from_bytes`** through injected **`Dispatcher`** and **`LibraryLoader`**; **`audio.py`** does not call **`ctypes`** or **`CDLL`**.
- **`src/aurora/runtime/dispatch_tokens.py`** includes **`AUDIO_FROM_FILE`** and **`AUDIO_FROM_BYTES`** (single shared vocabulary with image tokens). **`src/aurora/runtime/audio_dispatch.py`** owns the frozen **`Dispatcher.dispatch`** invocation contract **`(token, payload, lib)`** for audio. Helpers and tokens are **not** re-exported from **`aurora.runtime.__all__`**; **`AuroraAudio`** and **`AudioCreationError`** are exported like the image seam.
- **`tests/test_audio_runtime.py`** (fakes) and **`tests/test_runtime_smoke.py`** (composed audio smoke with patched **`CDLL`**) exercise the seam — **structural** proof only.

### M19 non-goals (explicit)

- **No** acoustic kernel extraction, C++ calculators, BUILD/graph/TFLite work, or MediaPipe code copy into **`aurora/`**.
- **No** decode correctness, native correctness, MediaPipe Tasks parity, **`@com_google_audio_tools`** integration in-repo, sample-rate/duration metadata, or segment-oriented APIs — offline/deterministic **Python seam** vocabulary only.
- **No** `VisionTaskBase` / `AudioTaskBase`, ARB, ORNITHOS, or BirdCLEF harness.

### M21 bounded D1 native audio file ingress (what it proves)

- **First explicit D1 slice (structural):** internal **`src/aurora/runtime/audio_native_bindings.py`** holds ctypes layouts and **`bind_audio_classifier`** for upstream **`MpAudioClassifierCreate`**, **`MpAudioClassifierClassify`**, **`MpAudioClassifierCloseResult`**, and **`MpAudioClassifierClose`** (plus optional **`MpErrorFree`**) — names aligned with **`docs/audio_classifier_graph_mapping.md`**, **no** `mediapipe/` import or source copy.
- **`NativeAudioDispatcher`** (**`src/aurora/runtime/native_audio_dispatcher.py`**) implements **`Dispatcher`**: **`dispatch(AUDIO_FROM_FILE, audio_path, lib)`** runs the minimal create → classify → close-result → close sequence using **`LibraryLoader.shared_library()`** as the **`CDLL`** handle; constructor takes a **model asset path** (TFLite) separate from the **audio file path** in **`AuroraAudio.from_file`**. **`audio_dispatch.py`** remains the frozen seam-level caller — **not** bypassed.
- **Tests** (`tests/test_native_audio_dispatcher.py`) use **in-process fakes** with the same arity as the C API — they prove **binding surface, ordering, and error translation**, **not** real graph execution on CI.

### M21 non-goals (explicit)

- **No** claim of WAV or codec decode correctness — file bytes are interpreted as raw float32 lanes for structural tests only (documented in **`native_audio_dispatcher`**).
- **No** claim of MediaPipe graph correctness, TFLite outputs, **`AudioClassifierGraph`** internals, or **`AudioToTensorCalculator`** behavior — CI does not execute a real upstream graph.
- **No** **`VisionTaskBase` / `AudioTaskBase`**, C++/BUILD work in **`aurora/`**, or workspace **`mediapipe/`** modification.
- **No** documentation that **`time_series_framer_calculator`** appears as a dedicated node in **`audio_classifier_graph.cc`** — M20’s BUILD-vs-graph nuance remains authoritative.

### M22 bounded D1 native **`AUDIO_FROM_BYTES`** on **`NativeAudioDispatcher`** (what it proves)

- **`NativeAudioDispatcher.dispatch(AUDIO_FROM_BYTES, raw_bytes, lib)`** runs the same **create → classify → close-result → close** sequence as **`AUDIO_FROM_FILE`**; **`MpAudioData`** is built from **`bytes`** with the same **structural** float32-lane interpretation as the file-backed path (**not** codec decode).
- **`AuroraAudio.from_bytes`** can succeed with **`NativeAudioDispatcher`** when fakes succeed — same **`AudioCreationError`** wrapping as other dispatch failures.
- **Tests** extend **`tests/test_native_audio_dispatcher.py`** — **structural** proof only.

### M22 non-goals (explicit)

- **No** new claims vs M21: decode correctness, graph/TFLite correctness, MediaPipe parity, or real native execution on CI.
- **No** `VisionTaskBase` / `AudioTaskBase`, ARB, or BirdCLEF harness.

### M27 ARB v0.1 minimal writer and hash (what it proves)

- **First-party** **`src/aurora/arb/`** package (**stdlib-only**): **`canonicalize`** (canonical JSON bytes per **`docs/aurora_run_bundle_v0_spec.md`** §5.2), **`sha256_hex`** / **`compute_root_hash`** (§6), **`write_arb`** (minimal valid **offline/batch** directory tree).
- **`tests/test_arb_*.py`** pins **SHA-256** digests for the spec §8 illustrative example as a **reference fixture**.

### M27 non-goals (explicit)

- **No** semantic CI gate on ARB contents beyond structural **`verify_repo_state.py`** checks; **no** change to **`src/aurora/runtime/`** seams.

### M28 ARB v0.1 minimal reader (what it proves)

- **`reader.py`** — **`read_arb`**, **`ArbBundle`** (frozen dataclass): eager load of the **minimal valid** v0.1 tree; **`manifest.json`** validated with the same rules as **`write_arb`**; **no** implicit hash verification in the reader API.
- **Public exports** from **`aurora.arb`** (see **M29** for **`validate_arb`**): **`ArbBundle`**, **`read_arb`**, **`write_arb`**, **`canonicalize`**, **`sha256_hex`**, **`compute_root_hash`**.
- **`tests/test_arb_reader.py`** — round-trip against **`write_arb`**, error paths, spec §8 fixture.

### M28 non-goals (explicit)

- **No** implicit hash verification inside **`read_arb`** (**M29** adds a separate **`validate_arb`**); **no** **replay** tooling, **CLI**, or **transport** wrapper handling.
- **No** semantic CI gate on ARB contents beyond structural **`verify_repo_state.py`** checks; **no** change to **`src/aurora/runtime/`** seams.

### M29 ARB v0.1 standalone validator (what it proves)

- **`validator.py`** — **`validate_arb(bundle_root)`** returns **`None`** on success and raises **`ArbValidationError`** on failure; recomputes per-file SHA-256 from on-disk bytes, checks **`hashes/sha256_manifest.json`** structure (§6.4) and canonical JSON on disk, and verifies **`hashes/root_hash.txt`** against **`hashes/sha256_manifest.json`** bytes (§6.5). **`manifest.json`** uses the same minimal validation as **`write_arb`** via **`_validate_minimal_manifest`** (imported from **`writer.py`** — no new shared module).
- **`read_arb`** is **unchanged** — **load** and **verify** are separate surfaces; **`tests/test_arb_validator.py`** includes an explicit case where **`read_arb`** succeeds and **`validate_arb`** fails.
- **Public exports** from **`aurora.arb`**: **`validate_arb`**, **`ArbValidationError`** (plus **M27**/**M28** symbols).
- **`scripts/verify_repo_state.py`** tracks **`validator.py`** in **`ARB_V0_REQUIRED_FILES`**.

### M29 non-goals (explicit)

- **No** **replay** tooling, **ARB CLI**, implicit validation in **`read_arb`**, **`src/aurora/runtime/`** changes, or ARB format redesign.
- **No** `pytest` migration or third-party runtime dependencies.

### M30 ARB v0.1 minimal CLI validator (what it proves)

- **`src/aurora/arb/__main__.py`** — **`python -m aurora.arb <bundle-root>`** invokes **`validate_arb`** only. **`sys.argv`** has **two** elements (**`argv[1]`** = bundle root); **`-m`** / module name are **not** in **`sys.argv`**. **Exit codes:** **0** valid, **1** validation failure (**`ArbValidationError`**), **2** usage error (not exactly one bundle argument). Deterministic messages: success on **stdout**; failure prefix + exception text on **stderr**; usage on **stderr**.
- **`scripts/verify_repo_state.py`** — **`__main__.py`** in **`ARB_V0_REQUIRED_FILES`**.
- **`tests/test_arb_cli.py`** — in-process **`main(argv)`** tests (no subprocess); **100%** line/branch on **`__main__.py`**.

### M30 non-goals (explicit)

- **No** inspect/read subcommand, **no** subcommands, **no** **`scripts/`** wrapper, **no** **`setuptools`** entry points, **no** replay, **no** **`src/aurora/runtime/`** changes, **no** change to **`validate_arb`** / **`read_arb`** behavior (**`read_arb`** remains library-only and non-validating).

### What M05 / M06 / M07 / M08 / M09 / M19 / M21 / M22 do not prove

- **MediaPipe** or native runtime correctness — CI does not exercise upstream graphs or tasks.
- **Decode correctness**, **MediaPipe parity**, or **real native execution** on the CI host — M09 / M19 smoke tests remain **fake-backed**; **M21** / **M22** add **structural** ctypes proof for **`AUDIO_FROM_FILE`** / **`AUDIO_FROM_BYTES`** when using **`NativeAudioDispatcher`**, **not** application-level correctness of the full upstream task.
- Upstream Tasks **`image.py`** migration inside a fork — M08 is the **in-repo** bounded surface only; see `docs/runtime_seam_framing.md` and `docs/aurora.md`.
- That any particular shared-library path is valid, safe, or compatible with MediaPipe — only that the **AURORA** loader wrapper behaves as documented when `CDLL` succeeds or fails.

## Protected `main` and pull requests

If branch protection is enabled on `main`, merges should go through **pull requests** that pass **`ci / repo-safety`**. Do not push unreviewed changes directly to `main` when protection is active.

## Boundaries

- Do not modify the workspace **`mediapipe/`** reference clone as part of this repo’s work.
- Do not copy or import MediaPipe source from `mediapipe/` into `aurora/`.
