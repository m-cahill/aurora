# AURORA — development workflow

This file describes **what exists today** in the `aurora/` repository: governance checks, the first-party runtime substrate under `src/aurora/`, lint, and tests. It is not a full roadmap for MediaPipe fork work (that lives in workspace context docs).

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

- repository layout and documentation anchors enforced by `scripts/verify_repo_state.py` (README link to `docs/aurora.md`, required headings, presence of `docs/runtime_surface_strategy.md`, `docs/runtime_substrate.md`, and `docs/runtime_seam_framing.md`, references in `docs/aurora.md` (including `runtime_seam_framing.md`), tracked substrate and **M06 seam contract** files plus **`src/aurora/runtime/shared_library_loader.py` (M07)** and **`src/aurora/runtime/image.py` (M08)** under `src/aurora/runtime/`, no `mediapipe` imports under `src/aurora/`, no tracked `.env`, workflow policy including full SHA pins for external Actions, no `*-latest` runners on enforcement workflows, and the stable `ci` / `repo-safety` identity);
- **Ruff** on `scripts/`, `tests/`, and `src/`;
- **stdlib `unittest`** for the verifier, **runtime substrate** import/metadata tests, **M09 composed runtime smoke tests** in `tests/test_runtime_smoke.py` (with **`PYTHONPATH=src`**);
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

### What M05 / M06 / M07 / M08 / M09 do not prove

- **MediaPipe** or native runtime correctness — CI does not exercise upstream graphs or tasks.
- **Decode correctness**, **MediaPipe parity**, or **real native execution** on the CI host — M09 smoke tests remain **fake-backed**; dispatch tokens are **conventions** until wired to a real implementation elsewhere.
- Upstream Tasks **`image.py`** migration inside a fork — M08 is the **in-repo** bounded surface only; see `docs/runtime_seam_framing.md` and `docs/aurora.md`.
- That any particular shared-library path is valid, safe, or compatible with MediaPipe — only that the **AURORA** loader wrapper behaves as documented when `CDLL` succeeds or fails.

## Protected `main` and pull requests

If branch protection is enabled on `main`, merges should go through **pull requests** that pass **`ci / repo-safety`**. Do not push unreviewed changes directly to `main` when protection is active.

## Boundaries

- Do not modify the workspace **`mediapipe/`** reference clone as part of this repo’s work.
- Do not copy or import MediaPipe source from `mediapipe/` into `aurora/`.
