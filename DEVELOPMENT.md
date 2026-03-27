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

## What CI proves (and what it does not)

The required GitHub status check is **`ci / repo-safety`** (workflow `ci`, job `repo-safety`).

When green, CI indicates:

- repository layout and documentation anchors enforced by `scripts/verify_repo_state.py` (README link to `docs/aurora.md`, required headings, presence of `docs/runtime_surface_strategy.md`, `docs/runtime_substrate.md`, and `docs/runtime_seam_framing.md`, references in `docs/aurora.md` (including `runtime_seam_framing.md`), tracked substrate and **M06 seam contract** files plus **`src/aurora/runtime/shared_library_loader.py` (M07)** under `src/aurora/runtime/`, no `mediapipe` imports under `src/aurora/`, no tracked `.env`, workflow policy including full SHA pins for external Actions, no `*-latest` runners on enforcement workflows, and the stable `ci` / `repo-safety` identity);
- **Ruff** on `scripts/`, `tests/`, and `src/`;
- **stdlib `unittest`** for the verifier and **runtime substrate** import/metadata tests (with **`PYTHONPATH=src`**);
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
- **`image.py` migration** is still **out of scope**; M07 only provides the in-repo loader seam (see `docs/runtime_seam_framing.md`).

### What M05 / M06 / M07 do not prove

- **MediaPipe** or native runtime correctness — CI does not exercise upstream graphs or tasks.
- Full **Dispatcher** implementations or **`image.py`** migration — see `docs/runtime_surface_strategy.md`, `docs/runtime_seam_framing.md`, and `docs/aurora.md`.
- That any particular shared-library path is valid, safe, or compatible with MediaPipe — only that the **AURORA** loader wrapper behaves as documented when `CDLL` succeeds or fails.

## Protected `main` and pull requests

If branch protection is enabled on `main`, merges should go through **pull requests** that pass **`ci / repo-safety`**. Do not push unreviewed changes directly to `main` when protection is active.

## Boundaries

- Do not modify the workspace **`mediapipe/`** reference clone as part of this repo’s work.
- Do not copy or import MediaPipe source from `mediapipe/` into `aurora/`.
