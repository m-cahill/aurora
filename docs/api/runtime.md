# `aurora.runtime` — public API

Exports below are listed in **`aurora.runtime.__all__`** (see `src/aurora/runtime/__init__.py`). **Dispatch tokens** and **dispatch helper** modules are **not** re-exported here; they are internal seam details unless added to **`__all__`** in a future milestone.

**Non-proof posture:** CI exercises these surfaces with **structural** and **fake-backed** tests. It does **not** prove decode correctness, real native library execution, graph/TFLite behavior, or MediaPipe parity. See [`../decisions/ADR-002-fake-backed-testing-native-non-proof.md`](../decisions/ADR-002-fake-backed-testing-native-non-proof.md).

---

## `SUBSTRATE_CONTRACT_VERSION`

- **Kind:** constant (`int`)
- **Import path:** `from aurora.runtime import SUBSTRATE_CONTRACT_VERSION`
- **Purpose:** Monotonic **metadata contract** version for **M05** substrate description (bump when `RuntimeSubstrateMetadata` shape or semantics change).
- **Behavior guaranteed by current CI:** Constant value matches runtime package tests and [`get_runtime_substrate_metadata`](#get_runtime_substrate_metadata).
- **Not guaranteed:** Any particular **upstream** or **native** runtime version.
- **Notes:** Not an execution-phase or MediaPipe version label.

---

## `get_runtime_substrate_metadata`

- **Kind:** function
- **Import path:** `from aurora.runtime import get_runtime_substrate_metadata`
- **Signature:** `get_runtime_substrate_metadata() -> RuntimeSubstrateMetadata`
- **Purpose:** Return a **frozen** description of the tracked `aurora` package substrate boundary introduced in **M05**.
- **Behavior guaranteed by current CI:** Returns `RuntimeSubstrateMetadata` with `package_import_path="aurora"`, `contract_version=SUBSTRATE_CONTRACT_VERSION`, and establishment id **`m05`** (see implementation in `surface py`).
- **Not guaranteed:** MediaPipe correctness, deployability, or native library presence.
- **Notes:** Pure metadata — safe to call without loading native code.

---

## `RuntimeSubstrateMetadata`

- **Kind:** class (`dataclass`, frozen, slots)
- **Import path:** `from aurora.runtime import RuntimeSubstrateMetadata`
- **Purpose:** Carry **reviewable** fields describing the substrate record (`package_import_path`, `contract_version`, `establishment_id`).
- **Behavior guaranteed by current CI:** Instances are immutable; fields populated by [`get_runtime_substrate_metadata`](#get_runtime_substrate_metadata).
- **Not guaranteed:** Semantic meaning beyond documentation/CI expectations.
- **Notes:** Constructor is public dataclass API; typical construction is via `get_runtime_substrate_metadata()`.

---

## `Dispatcher`

- **Kind:** protocol (`typing.Protocol`, runtime checkable)
- **Import path:** `from aurora.runtime import Dispatcher`
- **Purpose:** Minimal **`dispatch`-shaped** contract for the Python/native seam (parameters intentionally `Any` in the stub).
- **Signature:** `def dispatch(self, *args: Any, **kwargs: Any) -> Any`
- **Behavior guaranteed by current CI:** Structural typing only; tests use **fake** dispatchers — **not** real Tasks dispatch.
- **Not guaranteed:** Correct binding to any C API, graph execution, determinism, or MediaPipe behavior.
- **Notes:** Mirrors upstream “serial dispatcher” *shape* without importing MediaPipe.

---

## `LibraryLoader`

- **Kind:** protocol (`typing.Protocol`, runtime checkable)
- **Import path:** `from aurora.runtime import LibraryLoader`
- **Purpose:** Contract for a **process-wide singleton-style** shared library handle (`shared_library()`).
- **Signature:** `def shared_library(self) -> Any`
- **Behavior guaranteed by current CI:** Protocol definition + documentation; concrete [`SharedLibraryLoader`](#sharedlibraryloader) implements it.
- **Not guaranteed:** Thread safety, correct symbol sets, or valid handles for any host path.
- **Notes:** “Singleton” semantics are **by design** per audit framing — see module docstring in `library_loader.py`.

---

## `SharedLibraryLoader`

- **Kind:** class
- **Import path:** `from aurora.runtime import SharedLibraryLoader`
- **Purpose:** **Concrete** [`LibraryLoader`](#libraryloader) using **`ctypes.CDLL`** for one **caller-supplied** path; memoizes success and failure per instance.
- **Signatures:**
  - `__init__(self, path: str | os.PathLike[str]) -> None`
  - `library_path` → `pathlib.Path` (resolved)
  - `shared_library(self) -> Any` → memoized **CDLL** (or raises [`SharedLibraryLoadError`](#sharedlibraryloaderror))
- **Behavior guaranteed by current CI:** Load path normalization, memoization, and error behavior are covered with **patched** `CDLL` — **not** real vendor `.so` / `.dll` on CI.
- **Not guaranteed:** That any given path loads a usable Tasks binary, symbol correctness, or OS-specific load rules in production.
- **Notes:** Per-instance memoization; not a global singleton unless the app uses one instance.

---

## `SharedLibraryLoadError`

- **Kind:** exception subclass (`AuroraRuntimeError`)
- **Import path:** `from aurora.runtime import SharedLibraryLoadError`
- **Purpose:** Raised when **`ctypes.CDLL`** fails for the configured path (`path` attribute set).
- **Behavior guaranteed by current CI:** Raised on simulated load failure when tests patch `CDLL` to fail.
- **Not guaranteed:** Matches every platform `OSError` / `WindowsError` nuance for real loads.
- **Notes:** Subclass of internal `AuroraRuntimeError` (not exported at package root).

---

## `AuroraImage`

- **Kind:** class (`dataclass`, frozen, slots)
- **Import path:** `from aurora.runtime import AuroraImage`
- **Purpose:** Bounded **image** creation through injected [`Dispatcher`](#dispatcher) and [`LibraryLoader`](#libraryloader) — **no** direct `ctypes` in this module.
- **Signatures (public constructors):**
  - `from_file(cls, path: str, dispatcher: Dispatcher, library_loader: LibraryLoader) -> AuroraImage`
  - `from_bytes(cls, data: bytes, dispatcher: Dispatcher, library_loader: LibraryLoader) -> AuroraImage`
- **Fields:** `dispatcher`, `library_loader`, `native_handle: Any`, optional `source_path`
- **Behavior guaranteed by current CI:** Routing through internal image dispatch helpers; failure wrapped as [`ImageCreationError`](#imagecreationerror); tests use fakes/patched loaders.
- **Not guaranteed:** Correct decode, pixel meaning, or MediaPipe image pipeline correctness.
- **Notes:** Operation tokens (`IMAGE_FROM_*`) are **not** public exports from `aurora.runtime`.

---

## `ImageCreationError`

- **Kind:** exception subclass (`AuroraRuntimeError`)
- **Import path:** `from aurora.runtime import ImageCreationError`
- **Purpose:** Raised when [`AuroraImage`](#auroraimage) creation fails; chains underlying exception when available.
- **Behavior guaranteed by current CI:** Construction paths tested with fake dispatcher / loader failures.
- **Not guaranteed:** Exhaustive mapping of all upstream failure modes.

---

## `AuroraAudio`

- **Kind:** class (`dataclass`, frozen, slots)
- **Import path:** `from aurora.runtime import AuroraAudio`
- **Purpose:** Bounded **audio** creation parallel to [`AuroraImage`](#auroraimage) — same injection pattern.
- **Signatures (public constructors):**
  - `from_file(cls, path: str, dispatcher: Dispatcher, library_loader: LibraryLoader) -> AuroraAudio`
  - `from_bytes(cls, data: bytes, dispatcher: Dispatcher, library_loader: LibraryLoader) -> AuroraAudio`
- **Behavior guaranteed by current CI:** Routing via `audio_dispatch` with `AUDIO_FROM_*` tokens internally; failure as [`AudioCreationError`](#audiocreationerror).
- **Not guaranteed:** Decode correctness, sample-rate truth, or native audio graph behavior.
- **Notes:** Optional **native-shaped** dispatch adapters exist in other modules but are **not** part of `__all__`; consumers relying on them take **non-public** coupling.

---

## `AudioCreationError`

- **Kind:** exception subclass (`AuroraRuntimeError`)
- **Import path:** `from aurora.runtime import AudioCreationError`
- **Purpose:** Raised when [`AuroraAudio`](#auroraaudio) creation fails; chains underlying exception when available.
- **Behavior guaranteed by current CI:** Same structural pattern as image creation errors.
- **Not guaranteed:** Codec-specific or platform-specific decode diagnostics.

---

## Export list (source of truth)

Alphabetical per **`aurora.runtime.__all__`**:

`AudioCreationError`, `AuroraAudio`, `AuroraImage`, `Dispatcher`, `ImageCreationError`, `LibraryLoader`, `RuntimeSubstrateMetadata`, `SUBSTRATE_CONTRACT_VERSION`, `SharedLibraryLoadError`, `SharedLibraryLoader`, `get_runtime_substrate_metadata`
