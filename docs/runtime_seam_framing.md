# AURORA — Runtime seam framing (Phase B, M06–M07)

**Status:** Canonical committed framing (M06 contracts; M07 concrete loader)  
**Role:** Explain what the first-party **Dispatcher** and **LibraryLoader** contracts mean, what **`SharedLibraryLoader`** proves in M07, what **`image.py`** still needs for migration, and **honest LIVE_STREAM / async** semantics — without claiming upstream runtime parity.

**Last updated:** 2026-03-27

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

## 1a. What M07 proves

M07 adds a **minimal concrete** `SharedLibraryLoader` in `src/aurora/runtime/shared_library_loader.py` that implements the **`LibraryLoader`** protocol:

- **Explicit path only** — the constructor takes `str | PathLike[str]`; no environment-variable lookup, package-resource search, or other discovery logic in M07.
- **Per-instance memoization** — the first successful `shared_library()` call loads via `ctypes.CDLL` and caches the handle; subsequent calls on the **same instance** return the same object without calling `CDLL` again. Failed loads are also memoized so failure is deterministic.
- **Documented failure surface** — `SharedLibraryLoadError` when `CDLL` raises `OSError`, with exception chaining preserved.

**Tests** (with patched `ctypes.CDLL`, not real host libraries) cover protocol conformance, memoization, deterministic failure, and `aurora.runtime` exports.

**What M07 does not prove:** MediaPipe compatibility, correct symbols for Tasks API, thread safety, `image.py` migration, or that any particular path is loadable on a given machine.

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

Upstream, **`image.py`** is treated as a **bounded outlier** for raw `CDLL` / loading paths relative to other Tasks API modules. **Neither M06 nor M07 migrates `image.py`.** Preconditions for a future, behavior-preserving migration now include:

- A stable **loader** contract and documented singleton semantics (M06 **contract**; M07 **concrete** `SharedLibraryLoader` with explicit path and per-instance memoization — **not** upstream wiring).
- A **Dispatcher** boundary that call sites can target without entangling raw CDLL details in every module.
- Tests and evidence that a migration does not break import or dispatch assumptions (still **future** work).

**M07** satisfies the “stable loader semantics” slice **inside** `aurora/`; **`image.py` migration** remains a **separate** milestone.

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

## 6a. Explicit non-claims (M07)

M07 does **not**:

- migrate **`image.py`** or change upstream Tasks API modules;
- add domain smoke tests, task bases, or kernel work;
- claim that `SharedLibraryLoader` matches MediaPipe’s real loading graph or that a given path is valid on any host;
- introduce discovery beyond the explicit constructor path (no env/config/package-resource search).

---

## References

- `docs/aurora.md` — phase boundaries and milestone ledger.
- `docs/runtime_surface_strategy.md` — Phase B seam set and entry contract.
- `docs/runtime_substrate.md` — first-party package layout and provenance.
- Workspace `docs/context/AURORA_VISION.md` — vision (not committed in `aurora/`).
