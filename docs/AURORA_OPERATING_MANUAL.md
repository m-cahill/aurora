# AURORA — Operating Manual

**Purpose:** Practical guide for contributors and downstream consumers working in this repository.  
**Authority:** Proof claims, phase state, and milestone history are defined in [`aurora.md`](aurora.md). This manual does not strengthen or weaken those claims.

**Last updated:** 2026-04-10 (M32)

---

## 1. Purpose and identity

AURORA is the **governed acoustic runtime** refactor program implemented in this repo: explicit **Python/native seams**, **artifact-bound** offline batch semantics (ARB v0.1), and **truthful CI**. It is a **Foundry case study** surface, not Foundry core code.

Use this manual when you need to **run tools**, **import the package**, or **explain boundaries** without rereading the full project record.

---

## 2. What AURORA is / is not

**AURORA is:**

- A **first-party** Python package under `src/aurora/` with **stdlib-only** runtime dependencies.
- A **refactor program** record: milestones, verifier, and docs that keep claims aligned with tests.
- A **substrate** for downstream bioacoustic systems (ORNITHOS, PANTANAL-1) via **released** APIs and artifacts.

**AURORA is not:**

- A guarantee of MediaPipe fork parity, decode correctness, or graph correctness.
- A competition submission repo or training notebook stack by default.
- A place to land **competition-only** or **private product** dependencies that pull ORNITHOS/PANTANAL-1 concerns back into the runtime.

---

## 3. Core mental model

```text
Upstream study context (workspace mediapipe/ — read-only, not in this repo)
        ↓
Governed seams in aurora/ (Dispatcher, LibraryLoader, bounded Aurora* surfaces)
        ↓
ARB v0.1 bundles (optional artifact boundary — write / read / validate)
        ↓
Downstream repos (ORNITHOS, PANTANAL-1 — outside this repository by default)
```

**Seams** mean: callers inject a `Dispatcher` and `LibraryLoader`; domain types (`AuroraImage`, `AuroraAudio`) do not load `CDLL` directly.

**ARB** means: a **minimal valid** on-disk tree per [`aurora_run_bundle_v0_spec.md`](aurora_run_bundle_v0_spec.md), with canonical JSON and SHA-256 manifests — not a full observatory pipeline.

---

## 4. Current implemented surface

### 4.1 Runtime (`aurora.runtime`)

Public exports (see `src/aurora/runtime/__init__.py`):

- **Protocols:** `Dispatcher`, `LibraryLoader`
- **Loader:** `SharedLibraryLoader`, `SharedLibraryLoadError`
- **Domains:** `AuroraImage`, `ImageCreationError`, `AuroraAudio`, `AudioCreationError`
- **Metadata:** `RuntimeSubstrateMetadata`, `get_runtime_substrate_metadata`, `SUBSTRATE_CONTRACT_VERSION`

**Not** re-exported at package root (use submodules): `NativeAudioDispatcher`, `audio_native_bindings`, `dispatch_tokens`, `image_dispatch`, `audio_dispatch`.

### 4.2 ARB (`aurora.arb`)

- **Write / read:** `write_arb`, `read_arb`, `ArbBundle`
- **Integrity:** `validate_arb`, `ArbValidationError`
- **Utilities:** `canonicalize`, `sha256_hex`, `compute_root_hash`
- **CLI:** `python -m aurora.arb <bundle-root>` (validate only; exit codes 0 / 1 / 2)

Loading with `read_arb` does **not** imply cryptographic validation; call `validate_arb` when you need integrity checks.

---

## 5. Determinism and non-proof rules

**Offline / batch** modes are the strong **contractual** core for determinism narratives in this repo. **LIVE_STREAM** callback order is **not** treated as the determinism contract (see vision and seam framing docs).

**Explicit non-proofs (binding):**

- No **decode correctness** (bytes → validated samples for real codecs) claimed by this repo’s CI.
- No **graph / TFLite** correctness or MediaPipe **application** parity.
- No proof of **real native** Tasks shared library execution in CI; structural ctypes tests use fakes or patched `CDLL` as documented in [`DEVELOPMENT.md`](../DEVELOPMENT.md).

If a document or README implies stronger guarantees, **`docs/aurora.md`** wins.

---

## 6. Downstream boundary model

- **AURORA** must not import ORNITHOS or PANTANAL-1.
- Downstream projects may depend on **released** AURORA surfaces.
- Competition-specific tuning, submission packaging, and benchmark-only orchestration **default** to PANTANAL-1 unless a change also improves the **generic** runtime.

See [`aurora.md`](aurora.md) — *Proposed downstream repo layout and dependency directionality*.

---

## 7. How to use AURORA today

1. **Clone** this repository; use Python **3.11**.
2. **`pip install -r requirements-dev.txt`** from the repo root.
3. Set **`PYTHONPATH=src`** (see [`DEVELOPMENT.md`](../DEVELOPMENT.md) for Windows/macOS/Linux).
4. **Verifier:** `python scripts/verify_repo_state.py` (writes under `artifacts/`).
5. **Tests:** `python -m unittest discover -s tests -v`
6. **Coverage:** follow the exact sequence in [`DEVELOPMENT.md`](../DEVELOPMENT.md) so gates match CI.

**Import examples:**

```python
from aurora.runtime import AuroraImage, SharedLibraryLoader, Dispatcher
from aurora.arb import write_arb, read_arb, validate_arb
```

(You must still provide real or fake `Dispatcher` / `LibraryLoader` instances appropriate to your environment; the repo does not ship a production MediaPipe binary.)

---

## 8. Debugging and verification

- **CI truth:** The required check is **`ci` / `repo-safety`**. Artifacts uploaded include Ruff JSON, coverage JSON, and unittest output when workflows are configured to upload them.
- **Local failures:** Compare your commands to [`DEVELOPMENT.md`](../DEVELOPMENT.md); most import errors are **`PYTHONPATH`** not set to `src`.
- **Seam behavior:** Read the “What M0x proves / does not prove” sections in [`DEVELOPMENT.md`](../DEVELOPMENT.md) for the relevant milestone — they are the contract for what tests exercise.

---

## 9. Extension guidance

- **Prefer** new seams and small moves over broad rewrites.
- **Classify** work (governance, seam, API, kernel, artifact boundary) before coding; see [`aurora.md`](aurora.md) *Working rules for maintenance and future work*.
- **Do not** expand proof claims without tests and record updates in `docs/aurora.md`.
- **Kernel / native** work beyond structural seams requires explicit milestone authorization and remains bounded by Phase D closure criteria unless a new phase is recorded.

---

## 10. Frozen and bounded public surfaces

Treat as **stable for downstream** when taking a dependency on this repo (see also [`aurora.md`](aurora.md) — *Public AURORA handoff surface*):

- `src/aurora/runtime/` — seam types and bounded `Aurora*` types **as documented and tested**.
- `src/aurora/arb/` — ARB v0.1 APIs **as specified** in [`aurora_run_bundle_v0_spec.md`](aurora_run_bundle_v0_spec.md).
- Committed **`docs/`** linked from the project record — for boundaries and proof bars, not for implied runtime guarantees beyond what `aurora.md` states.

**Internal** modules (dispatch helpers, native dispatcher, bindings) are **implementation details** unless re-exported; prefer the public exports and the spec.

---

## 11. Where to read next

| Need | Document |
|------|----------|
| Full history and ledger | [`aurora.md`](aurora.md) |
| Vision and program framing | [`AURORA_VISION.md`](AURORA_VISION.md) |
| Milestone narratives (M01–M31) | [`milestone_summaries/README.md`](milestone_summaries/README.md) |
| CI and tools | [`../DEVELOPMENT.md`](../DEVELOPMENT.md) |
