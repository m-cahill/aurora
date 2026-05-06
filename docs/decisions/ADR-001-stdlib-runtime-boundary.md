# ADR-001 — Stdlib runtime boundary

**Status:** Accepted  
**Date:** 2026-05-06  
**Milestone:** M36  
**Scope:** Documentation / governance

## Context

AURORA v0.1 positions the **tracked runtime and ARB implementation** under `src/aurora/` as **stdlib-only** for third-party **runtime** dependencies: the public handoff code does not require NumPy, MediaPipe wheels, or other application libraries at import time. Separately, **repository hygiene and quality gates** (CI, typing, linting, auditing) use **pinned** third-party tools in dev requirements, as authorized per milestone.

Downstream readers sometimes conflate “no third-party runtime deps” with “no tooling anywhere,” which misstates how the repo is verified today.

## Decision

1. **Runtime / library boundary:** The **v0.1 public Python surface** delivered in `src/aurora/` remains **stdlib-only** for **runtime** third-party package dependencies unless a future milestone explicitly authorizes and documents a change.
2. **Development and CI tooling:** **Dev/test/release automation** may use **explicitly authorized** third-party tools (e.g. Ruff, Mypy, coverage, pip-audit) with **pinned** versions in `requirements-dev.txt` / workflow wiring, as recorded in `DEVELOPMENT.md` and milestone history.
3. **M36 documentation:** This milestone adds **hand-curated Markdown** only. It does **not** add **pdoc**, **Sphinx**, **MkDocs**, or other **doc-build** dependencies or generators.

## Consequences

- The “stdlib story” applies to **what ships as the governed library** in `src/aurora/`, not to **every** process that touches the repository.
- Future **generated API documentation** (if any) is a **tooling** decision for a later milestone, not an implicit expansion of the runtime dependency set.

## Invariants

- ADR-001 does **not** change `src/aurora/` imports or packaging.
- Breaking the stdlib-only **runtime** bar requires an explicit milestone and ADR/update to this record.

## Non-goals

- Claiming that **stdlib-only runtime** means **zero** third-party tools **forever** in development, CI, or optional contributor workflows.
- Choosing or pinning specific doc generators beyond **hand-curated** Markdown in M36.

## Verification

- `pyproject.toml` / `src/aurora/` remain consistent with the committed stdlib-runtime posture.
- Cross-check with [`../aurora.md`](../aurora.md) **open core** and maintenance posture language.
