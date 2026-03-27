# AURORA — development workflow

This file describes **what exists today** in the `aurora/` repository: governance checks, lint, and tests for the support tooling. It is not a roadmap for runtime or MediaPipe work.

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
ruff check scripts tests
```

## Run governance support tests locally

```bash
python -m unittest discover -s tests -v
```

## What CI proves (and what it does not)

The required GitHub status check is **`ci / repo-safety`** (workflow `ci`, job `repo-safety`).

When green, CI indicates:

- repository layout and documentation anchors enforced by `scripts/verify_repo_state.py` (README link to `docs/aurora.md`, required headings, presence of `docs/runtime_surface_strategy.md` and a reference to it in `docs/aurora.md`, no tracked `.env`, workflow policy including full SHA pins for external Actions, no `*-latest` runners on enforcement workflows, and the stable `ci` / `repo-safety` identity);
- **Ruff** on `scripts/` and `tests/`;
- **stdlib `unittest`** for the governance verifier;
- **bytecode compile** sanity for `scripts/` and `tests/`.

It does **not** prove MediaPipe correctness, application behavior, or a Python package import surface that does not exist yet.

## Protected `main` and pull requests

If branch protection is enabled on `main`, merges should go through **pull requests** that pass **`ci / repo-safety`**. Do not push unreviewed changes directly to `main` when protection is active.

## Boundaries

- Do not modify the workspace **`mediapipe/`** reference clone as part of this repo’s work.
- Do not copy or import MediaPipe source from `mediapipe/` into `aurora/`.
