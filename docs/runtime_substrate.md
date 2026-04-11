# AURORA — Runtime substrate (M05)

**Status:** Canonical committed record of the first tracked runtime substrate  
**Role:** States what exists under `src/aurora/`, provenance rules, and explicit non-claims.  
**Last updated:** 2026-04-10 (M05 baseline; current phase and milestone posture in [`docs/aurora.md`](aurora.md)).

---

## 1. Package path and modules (M05)

| Path | Role |
|------|------|
| **`src/aurora/`** | First-party Python package root (`PYTHONPATH=src` for imports). |
| **`src/aurora/__init__.py`** | Package root marker. |
| **`src/aurora/runtime/__init__.py`** | Runtime subpackage; re-exports the minimal substrate API. |
| **`src/aurora/runtime/surface.py`** | Substrate metadata dataclass and `get_runtime_substrate_metadata()`. |

Layout ambiguity is **resolved** for M05: the **`src/aurora/`** layout is the chosen substrate root (not a second top-level package root under `aurora/` without `src/`).

---

## 2. Provenance

- **First-party AURORA-authored** code only for the modules above.
- **No** source copied from the workspace **`mediapipe/`** read-only clone into this tree.
- **No** `import mediapipe` or `from mediapipe` in `src/aurora/` (enforced by verifier and tests).

Architectural learning from MediaPipe is allowed elsewhere; **code transfer from that tree is not**.

---

## 3. What this substrate proves

- The tracked repository contains an **importable** first-party package at `aurora` (with `PYTHONPATH=src`).
- A **stable, reviewable** metadata contract exists (`RuntimeSubstrateMetadata` / `get_runtime_substrate_metadata()`).
- CI and tests can **truthfully** assert importability and metadata — not application or MediaPipe correctness.

---

## 4. What it does not yet prove

- **Dispatcher** formalization, **`image.py`** migration, **`LibraryLoader`**, or task-base/kernel work.
- **MediaPipe** or native runtime behavior, graphs, or models.
- Determinism, replay, or BirdCLEF rails — **deferred** per phase boundaries.

---

## 5. Phase B foundation (if M05 closes cleanly)

If M05 completes with the Phase B entry contract satisfied (`docs/runtime_surface_strategy.md` §6), Phase B may begin **normalizing runtime seams** against this **named package boundary** — still **without** copying upstream source into `aurora/`.

---

## References

- `docs/runtime_surface_strategy.md` — Ingress strategy and Phase B entry contract.
- `docs/aurora.md` — Project record, phases, milestone ledger.
