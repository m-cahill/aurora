# AURORA — Runtime seam framing (Phase B, M06–M09)

**Status:** Canonical committed framing (M06 contracts; M07 concrete loader; M08 bounded image seam; M09 composed runtime smoke tests; M19 audio seam; M21 **`NativeAudioDispatcher`** for bounded D1; **M23** — **Phase D** **closed** in **`docs/aurora.md`** — structural seams + explicit non-proofs, **not** local-native execution proof)  
**Role:** Explain what the first-party **Dispatcher** and **LibraryLoader** contracts mean, what **`SharedLibraryLoader`** proves in M07, what **`AuroraImage`** proves in M08 (first-party bounded image surface — **not** upstream Tasks `image.py` migration), what **M09 smoke tests** prove at the composed seam layer, **M21**/**M22**’s concrete audio dispatcher (**structural** only), and **honest LIVE_STREAM / async** semantics — without claiming upstream runtime parity. **Phase D closure** narrative: **`docs/aurora.md`** (**M23**).

**Last updated:** 2026-04-01

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

## 1b. What M08 proves

M08 adds a **bounded** first-party image seam in `src/aurora/runtime/image.py`:

- **`AuroraImage`** — small class with `from_file` and `from_bytes` class methods; both obtain the shared-library handle via **`LibraryLoader.shared_library()`** and route work through **`Dispatcher.dispatch(...)`** using operation tokens `aurora_image_from_file` and `aurora_image_from_bytes` (no change to the **`Dispatcher`** Protocol shape).
- **No `ctypes` / `CDLL` in `image.py`** — this module does not load native libraries directly; **`SharedLibraryLoader`** remains the only first-party module that calls `ctypes.CDLL` (M07).
- **`ImageCreationError`** — single failure type for loader/dispatch failures, with exception chaining preserved.
- **Verifier** tracks `image.py` structurally; **tests** use fakes (no real host libraries).

**What M08 does not prove:** Upstream MediaPipe `vision` / Tasks **`image.py`** parity, correct decoding of any file format, native graph correctness, domain smoke coverage, task bases, or kernel work.

---

## 1c. What M09 proves (composed runtime smoke)

M09 adds **`tests/test_runtime_smoke.py`**: a **smoke-style** layer **above** M07/M08 unit tests. It exercises the **composed** first-party chain:

- Real **`SharedLibraryLoader`** with **`ctypes.CDLL` patched** (no real host libraries, deterministic).
- Real **`AuroraImage`** (`from_file` / `from_bytes`).
- A **recording fake `Dispatcher`** (not a real upstream or native dispatcher).

Together this demonstrates **`AuroraImage` → `SharedLibraryLoader` → patched `CDLL`** and **`AuroraImage` → `Dispatcher.dispatch(...)`** end-to-end for bounded happy paths, plus **loader** and **dispatch** failure paths surfaced as **`ImageCreationError`** with exception chaining preserved.

**What M09 does not prove:** MediaPipe parity, decode correctness, real native execution on CI, that operation tokens map to any real implementation, upstream Tasks **`image.py`** migration, task bases, kernel work, or placeholder coverage for domains without a first-party surface (for example audio/text).

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

## 4. Bounded image seam vs upstream `image.py` outlier

Audits treat upstream MediaPipe **`image.py`** as the **bounded outlier** that bypasses `SerialDispatcher` for raw native access. **M08 does not modify upstream** — the workspace `mediapipe/` clone stays untouched.

Inside **`aurora/`**, M08 introduces **`src/aurora/runtime/image.py`** so the **first-party** image-shaped seam routes through the same **Dispatcher** and **LibraryLoader** abstractions as the rest of the Phase B story: no `CDLL` calls in `image.py`, fake-backed tests, honest non-claims.

Migrating **upstream** Tasks `image.py` onto a dispatcher (in a fork) remains **out of scope** for this repository’s tracked work; this milestone only establishes the **in-repo** bounded surface and proof pattern.

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
- perform **`image.py`**-style migration (M08 addresses the **first-party** bounded surface only).

## 6a. Explicit non-claims (M07)

M07 does **not**:

- add the first-party **`AuroraImage`** surface (that is M08) or change upstream Tasks API modules;
- add domain smoke tests, task bases, or kernel work;
- claim that `SharedLibraryLoader` matches MediaPipe’s real loading graph or that a given path is valid on any host;
- introduce discovery beyond the explicit constructor path (no env/config/package-resource search).

## 6b. Explicit non-claims (M08)

M08 does **not**:

- modify or import upstream MediaPipe **`image.py`** / `mediapipe/` sources;
- claim decode correctness, MediaPipe parity, or real native execution on CI;
- add domain smoke tests, task bases, kernel extraction, or **`Dispatcher`** Protocol changes beyond the existing `dispatch` signature;
- prove that operation tokens `aurora_image_from_file` / `aurora_image_from_bytes` map to any real native implementation.

## 6c. Explicit non-claims (M09)

M09 does **not**:

- claim MediaPipe parity, decode correctness, or real native execution on CI;
- modify upstream Tasks **`image.py`** or workspace **`mediapipe/`**;
- wire dispatch tokens to real native implementations;
- add task bases, kernel extraction, or placeholder smoke tests for domains without a current first-party surface.

## 6d. M21 / M22 — **`NativeAudioDispatcher`** (bounded D1)

**M21** adds an **optional** concrete **`Dispatcher`** implementation — **`NativeAudioDispatcher`** — that uses **`audio_native_bindings`** to call the Tasks **AudioClassifier** C API symbols (**`MpAudioClassifier*`**) with a **model path** supplied at dispatcher construction time. **`dispatch(AUDIO_FROM_FILE, …)`** uses the **audio file path** from **`AuroraAudio.from_file`**. **`audio_dispatch.py`** remains unchanged as the seam-level caller.

**M22** extends the same dispatcher: **`dispatch(AUDIO_FROM_BYTES, …)`** uses **raw `bytes`** with the same **structural** float32-lane mapping as the file-backed path (not codec decode), and the same **create → classify → close-result → close** lifecycle as **`AUDIO_FROM_FILE`**.

**What M21 / M22 do not prove:** decode correctness, graph or model correctness, or that CI runs a real MediaPipe graph — see **`DEVELOPMENT.md`**.

---

## References

- `docs/aurora.md` — phase boundaries and milestone ledger.
- `docs/runtime_surface_strategy.md` — Phase B seam set and entry contract.
- `docs/runtime_substrate.md` — first-party package layout and provenance.
- Workspace `docs/context/AURORA_VISION.md` — vision (not committed in `aurora/`).
