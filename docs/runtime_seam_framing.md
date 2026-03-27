# AURORA — Runtime seam framing (Phase B, M06)

**Status:** Canonical committed framing (M06)  
**Role:** Explain what the first-party **Dispatcher** and **LibraryLoader** contracts mean, what **`image.py`** is as a precondition for later work, and **honest LIVE_STREAM / async** semantics — without claiming upstream runtime parity.

**Last updated:** 2026-03-26

See also: `docs/runtime_surface_strategy.md` (ingress and Phase B entry contract), `docs/runtime_substrate.md` (package boundary), `docs/aurora.md` (project record).

---

## 1. What M06 proves

M06 delivers **contract-level** seam formalization in the tracked `aurora/` repo:

- A minimal **`Dispatcher`** `typing.Protocol` (single `dispatch`-shaped boundary) in `src/aurora/runtime/dispatcher.py`.
- A minimal **`LibraryLoader`** `typing.Protocol` that documents the **singleton** shared-library / `CDLL` assumption in `src/aurora/runtime/library_loader.py`.
- Tests that a stub can satisfy each protocol and that the contracts import cleanly.
- Verifier and doc cross-links so this surface stays **governed and auditable**.

CI and tests remain **truthful**: green means **repo layout, substrate importability, seam contracts, and governance tripwires** — **not** MediaPipe correctness, native graph behavior, or full dispatch implementation.

---

## 2. `Dispatcher` contract

**Intent:** Make the Python/native **dispatch seam** explicit at the type level first.

**Scope:** One method — `dispatch(*args, **kwargs)`. No lifecycle (`create`, `close`, `shutdown`), no context-manager behavior, no task ownership semantics in M06.

**What it does not prove:** That any concrete dispatcher matches MediaPipe’s `SerialDispatcher` or that native calls succeed.

---

## 3. `LibraryLoader` contract

**Intent:** Make the **singleton shared-library** assumption explicit and testable at the contract level.

Audits identify a real constraint: a **single** `_shared_lib`-style handle (not multiple independent `CDLL` instances) unless a later change explicitly proves otherwise. The Protocol’s `shared_library()` method and docstring encode that assumption **without** implementing loading, path resolution, or platform-specific behavior in M06.

---

## 4. `image.py` as a bounded outlier (preconditions only)

Upstream, **`image.py`** is treated as a **bounded outlier** for raw `CDLL` / loading paths relative to other Tasks API modules. **M06 does not migrate `image.py`.** It only frames **preconditions** for a future, behavior-preserving migration:

- A stable **loader** contract and documented singleton semantics (this milestone introduces the **contract** only).
- A **Dispatcher** boundary that call sites can target without entangling raw CDLL details in every module.
- Tests and evidence that a migration does not break import or dispatch assumptions.

Until those preconditions are met in a **later** milestone, migration remains **out of scope** for M06.

---

## 5. LIVE_STREAM and async / live semantics

**Honest rule:** In **LIVE_STREAM** (and similar async/live modes), **callback arrival order is not the determinism contract.**

What **is** the stable surface for replay and audit:

- **Timestamps** and **recorded events** (and any explicitly documented sequence identifiers the runtime provides for offline use).

What must **not** be overclaimed:

- That Python callback order alone defines a deterministic replay order in live/async settings.

Offline batch modes remain the stronger determinism core, as described in `docs/aurora.md` (*Audit-established starting facts*).

---

## 6. Explicit non-claims (M06)

M06 does **not**:

- introduce `VisionTaskBase` / `AudioTaskBase`, kernel extraction, or C API signature changes;
- copy or import MediaPipe source from the workspace clone;
- claim MediaPipe or native-runtime correctness;
- perform the actual **`image.py`** migration.

---

## References

- `docs/aurora.md` — phase boundaries and milestone ledger.
- `docs/runtime_surface_strategy.md` — Phase B seam set and entry contract.
- `docs/runtime_substrate.md` — first-party package layout and provenance.
- Workspace `docs/context/AURORA_VISION.md` — vision (not committed in `aurora/`).
