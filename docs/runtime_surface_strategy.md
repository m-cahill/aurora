# AURORA — Tracked runtime surface strategy

**Status:** Canonical governance document (committed)  
**Role:** Defines how a legitimate implementation surface may enter `aurora/` and what must exist before Phase B (runtime seam normalization) is authorized.  
**Last updated:** 2026-03-26 (M04)

This document is the **committed gate** for future runtime work. It does not establish runtime code by itself; it records an auditable decision the repo can execute against.

---

## 1. Current problem statement

### 1.1 What exists in `aurora/` today

The tracked repository (`m-cahill/aurora`) currently contains:

- **Governance and safety tooling:** `scripts/verify_repo_state.py`, CI workflow (`ci` / `repo-safety`), Ruff configuration, support-tier tests under `tests/`.
- **Canonical project record:** `docs/aurora.md`, `README.md`, `DEVELOPMENT.md`.
- **Verification artifacts:** outputs under `artifacts/` produced by the verifier.

These surfaces are sufficient to prove **repo hygiene, workflow identity, and documentation continuity**. They are **not** a MediaPipe runtime, task API, or Python/native dispatch implementation.

### 1.2 What does not yet exist

- A **first-party Python package** (or equivalent) that owns runtime behavior for Tasks API seams.
- **Dispatcher / loader abstractions** or migrations off raw CDLL paths (Phase B scope).
- **Smoke, import, or build tripwires** that exercise application or native runtime correctness.
- Any **import or copy** of MediaPipe source from the workspace `mediapipe/` read-only clone into `aurora/`.

### 1.3 Why honest runtime work cannot start without a strategy

Phase B (see `docs/aurora.md`, *Execution Phase Boundaries*) assumes there is a **tracked place** to normalize seams (`Dispatcher`, `image.py`, loader semantics, documented async behavior). Today that place is **undefined**: package layout was explicitly **deferred**, and the only MediaPipe code lives outside the `aurora/` repo boundary.

Without a written, provenance-respecting **ingress strategy** and a **minimal layout** decision, “start Phase B” would mean either violating the clean-room rule (copying upstream code) or pretending the repo contains runtime surfaces it does not. M04 closes that gap by **deciding** how runtime code may appear in `aurora/` and what must happen **before** Phase B is authorized.

---

## 2. Hard constraints

| Constraint | Implication |
|------------|----------------|
| **`mediapipe/` is read-only** in the workspace | Study and evidence only; no edits; not a source of copied implementation into `aurora/`. |
| **No import, copy, or paste** of MediaPipe source from `mediapipe/` into `aurora/` | Architectural learning is allowed; **code transfer from that tree is not**. |
| **Behavior preservation is the default** | Future refactors are classified and evidenced; no silent semantic changes. |
| **TFLite is a core first-wave dependency** | Do not treat early milestones as decoupling the entire graph build from TFLite. |
| **`@com_google_audio_tools` is a real dependency** | Any audio DSP path must account for it explicitly when touched. |
| **Phase B is defined but gated** | Dispatcher / `image.py` / loader / async documentation work **only after** a tracked implementation surface exists and **Phase B is explicitly authorized** in the project record (after M05; see §6). |

---

## 3. Approved ingress strategy (standalone repo)

### 3.1 Decision

**`aurora/` remains a standalone git repository.** Runtime code enters `aurora/` only through **normal, reviewable commits** that preserve provenance and respect the clean-room boundary:

1. **Original implementation** — New code authored for AURORA (or licensed third-party deps declared in `requirements.txt` / `pyproject.toml` when introduced) with clear ownership and review history.
2. **No code from `mediapipe/`** — The read-only `mediapipe/` clone is **not** a copy source into `aurora/`. Equivalents may be **re-derived** in a clean-room way with explicit rationale and tests when runtime work begins.
3. **Explicit dependency pins** — External tools and libraries are pinned and documented as governance matures (M03 posture continues).

### 3.2 Options considered and not chosen (initial strategy)

| Approach | Why not chosen for initial ingress |
|----------|-----------------------------------|
| **Git submodule** of `mediapipe-aurora` (or similar) into `aurora/` | Would collapse the workspace boundary before package layout and substrate establishment are executed; couples repos prematurely; conflicts with “study surface only” for `mediapipe/` and deferred layout. **Rejected for M04–M05 entry strategy.** |
| **Git subtree** of a MediaPipe fork | Same coupling and provenance concerns; blurs “what is tracked in `aurora/`” vs upstream. **Rejected for initial strategy.** |
| **Vendoring MediaPipe sources** | Would violate the no-copy rule from `mediapipe/` into `aurora/`. **Rejected.** |

These may be **revisited only** by a future milestone that explicitly updates this document and the project record with new evidence and acceptance criteria.

### 3.3 Relationship to the MediaPipe fork

The workspace may retain a **sibling** clone (e.g. `mediapipe-aurora`) for **study, audits, and behavioral reference**. That relationship does **not** authorize copying files into `aurora/`. When runtime code is written, behavior may be **matched** using tests and artifacts, not pasted source.

---

## 4. First tracked runtime slice (planning level)

The following **first-wave seam set** is the intended scope of **Phase B** once authorized—not a commitment to implement all at once in a single milestone.

| Area | Intent |
|------|--------|
| **Python/native dispatch path** | Formalize `Dispatcher` (and related) boundaries consistent with audits. |
| **`image.py`** | Treat as a bounded outlier; migrate off raw CDLL in a behavior-preserving way when prerequisites exist. |
| **Loader / shared library** | Make `_shared_lib` / loading semantics explicit and testable (`LibraryLoader` direction per Phase B definition). |
| **LIVE_STREAM / async** | Document **honest** semantics (timestamps, recorded events); do not claim callback order as determinism. |
| **Domain smoke tests** | Once code exists, add smoke tests per domain appropriate to the surface. |

### 4.1 Minimum executable Phase B entry slice

The **smallest** set that must be in scope for the **first** Phase B runtime-seam milestone (when Phase B is authorized):

1. **Dispatcher boundary formalization** — Primary leverage point per audits.
2. **`image.py` migration precondition** — Clear precondition work (e.g. loader surface stable enough to migrate safely).
3. **Loader abstraction** — When justified by the same milestone, not as speculative churn.
4. **Explicit async/LIVE_STREAM documentation surface** — User- and maintainer-facing honesty about ordering.

Broader smoke-test coverage expands as the surface grows; M04 does **not** require tests against code that does not exist.

---

## 5. Minimum package/module layout (documented only)

**M04 does not create directories.** The following is the **planned** layout when `aurora/` gains a substrate (target: **M05**).

| Location | Purpose |
|----------|---------|
| **`aurora/src/aurora/`** (or `aurora/aurora/` as a single package root) | **Python package root** for first-party runtime code. Exact top-level name (`aurora` vs `aurora_runtime`) is fixed at substrate establishment with one import path. |
| **`aurora/tests/`** (existing) | **Extend** with tests colocated by feature (`tests/test_runtime_*.py` or subpackages) when runtime modules exist. |
| **`aurora/docs/`** | **Architecture and governance docs** for runtime (`aurora.md`, this file, future ADRs). |

**Rule:** Keep the tree **small**. No empty placeholder packages in M04; M05 creates the first real modules when substrate is established.

---

## 6. Phase B entry contract

Phase B is **not** authorized at M04 closeout. The following must **all** be true **before** `Phase B — Runtime Seam Normalization` is explicitly authorized in `docs/aurora.md`:

1. **M05 complete** — *Provenance-preserving runtime substrate establishment* (or equivalent milestone) has closed with recorded commit SHA and honest CI.
2. **Implementation surface present** — At least one importable Python package (or agreed equivalent) exists under `aurora/` with a defined scope, not only scripts and verifier tests.
3. **Provenance strategy executed** — Runtime code entered via §3 (standalone repo, no copy from `mediapipe/`), with dependencies pinned as appropriate.
4. **Minimal tripwires** — `unittest` (or agreed CI) checks that the new surface **imports** and passes **minimal smoke** checks appropriate to that surface; CI remains truthful (no false claims of MediaPipe correctness).
5. **First Phase B milestone scope locked** — e.g. dispatcher formalization + `image.py` precondition + loader/async doc slice as in §4.1.

**Authorization rule:** **Phase B is explicitly authorized only after M05 closes cleanly**, not merely because a strategy exists.

---

## 7. Explicit non-goals (still deferred)

- **Task-base extraction** (`VisionTaskBase` / `AudioTaskBase`) — Phase C territory.
- **Acoustic kernel extraction** — Phase D / later.
- **ARB format, ORNITHOS architecture, certification, observatory** — As in `docs/aurora.md`.
- **Competition rail layout** (C01–C05) — Deferred.
- **Model stack** — Deferred.

---

## 8. What this document does not prove

This strategy does **not** prove MediaPipe or application correctness. CI may still **only** cover governance scripts, verifier, and documented gates until runtime code and tests exist.

---

## References

- `docs/aurora.md` — Project record, phase boundaries, milestone ledger.
- Workspace `docs/context/AURORA_VISION.md` — Vision (not committed in `aurora/`).
- Workspace `docs/preflight/aurora_startup_lock/` — Startup locks and invariants.
