# `aurora.arb` — public API

Symbols below match **`aurora.arb.__all__`** (`src/aurora/arb/__init__.py`). **Submodules** (e.g. `reader.py`, `validator.py`) are implementation detail unless re-exported here.

**Versioning:** **ARB v0.1** only — see [`../decisions/ADR-003-arb-v0-versioning-compatibility.md`](../decisions/ADR-003-arb-v0-versioning-compatibility.md) and [`../aurora_run_bundle_v0_spec.md`](../aurora_run_bundle_v0_spec.md).

**Non-proof posture:** Validation proves **on-disk layout + canonical JSON + hash contracts** per spec — **not** replay of a full acoustic pipeline, transport security, certification, or semantic truth of model outputs. See [`README.md`](README.md) non-proof list.

---

## `ArbBundle`

- **Kind:** class (`dataclass`, frozen, slots)
- **Import path:** `from aurora.arb import ArbBundle`
- **Purpose:** **Eager** in-memory view of a minimal **v0.1** bundle: `manifest`, `graph_yaml`, `audio_index`, `segments`, `predictions`, `sha256_manifest`, `root_hash`.
- **Behavior guaranteed by current CI:** Constructed only via [`read_arb`](#read_arb); field types match reader tests.
- **Compatibility notes:** **`root_hash` and per-file digests are not verified** inside `read_arb` — call [`validate_arb`](#validate_arb) separately per ADR-003 / spec.
- **Not guaranteed:** Semantic consistency of JSON payload *beyond* structural parse + manifest keys required for minimal trees.

---

## `ArbValidationError`

- **Kind:** exception (`Exception` subclass)
- **Import path:** `from aurora.arb import ArbValidationError`
- **Purpose:** Raised exclusively by [`validate_arb`](#validate_arb) and the **[`validate-only CLI`](#validate-only-cli-python--m-auroraarb)** for bundle failures.
- **Behavior guaranteed by current CI:** Distinguishes validation failures from generic `ValueError` paths in reader/writer tests.
- **Compatibility notes:** Message strings are for humans; **do not** parse as stable API. Prefer success vs exception.
- **Not guaranteed:** Stable wording across versions for the same failure class.

---

## `canonicalize`

- **Kind:** function
- **Import path:** `from aurora.arb import canonicalize`
- **Signature:** `canonicalize(obj: Any) -> bytes`
- **Purpose:** Serialize a JSON-serializable object to **canonical** UTF-8 JSON bytes (sorted keys, compact separators, `ensure_ascii=False`, `allow_nan=False`, no floats — see implementation).
- **Behavior guaranteed by current CI:** Deterministic bytes for pinned fixtures; rejects `float` and non-finite numbers with `ValueError`.
- **Compatibility notes:** Must match **`§5.2`** rules in [`../aurora_run_bundle_v0_spec.md`](../aurora_run_bundle_v0_spec.md).
- **Not guaranteed:** Round-trip through third-party serializers; validation of *semantic* scoring rules inside JSON objects.

---

## `sha256_hex`

- **Kind:** function
- **Import path:** `from aurora.arb import sha256_hex`
- **Signature:** `sha256_hex(data: bytes) -> str`
- **Purpose:** Lowercase hex SHA-256 digest (**64** chars) of raw bytes.
- **Behavior guaranteed by current CI:** Matches stdlib `hashlib` behavior on test vectors.
- **Compatibility notes:** Used for per-file digests and manifest hashing per spec **§6**.
- **Not guaranteed:** Hardware acceleration, streaming APIs, or non-SHA-256 algorithms.

---

## `compute_root_hash`

- **Kind:** function
- **Import path:** `from aurora.arb import compute_root_hash`
- **Signature:** `compute_root_hash(sha256_manifest_json_bytes: bytes) -> str`
- **Purpose:** **Bundle root hash** — SHA-256 hex of the **on-disk bytes** of **`hashes/sha256_manifest.json`** (canonical JSON bytes per **§6.5**).
- **Behavior guaranteed by current CI:** Agreement with `write_arb` / `validate_arb` on golden bundles.
- **Compatibility notes:** Input must be **exact** file bytes used in the bundle, not a re-serialization unless byte-identical.
- **Not guaranteed:** Cross-version hash rules if a future `arb_version` changes the contract.

---

## `write_arb`

- **Kind:** function
- **Import path:** `from aurora.arb import write_arb`
- **Signature:**  
  `write_arb(dest: Path, *, manifest: dict[str, Any], graph_yaml: str, inputs: dict[str, Any], segments: dict[str, Any], predictions: dict[str, Any]) -> str`
- **Purpose:** Write a **minimal valid** ARB v0.1 directory tree under **`dest`**; return **`root_hash`** hex string.
- **Behavior guaranteed by current CI:** Required manifest keys, `arb_version == "0.1"`, `runtime_mode == "offline_batch"`, path fields for minimal layout, deterministic outputs for pinned inputs (see §8 digests in tests).
- **Compatibility notes:** Overwrites paths under `dest` as needed; does not read pre-existing files.
- **Not guaranteed:** Non-minimal bundles, LIVE_STREAM / training profiles, or arbitrating semantic content of predictions.

---

## `read_arb`

- **Kind:** function
- **Import path:** `from aurora.arb import read_arb`
- **Signature:** `read_arb(bundle_root: str | Path) -> ArbBundle`
- **Purpose:** **Load** minimal v0.1 tree from disk into [`ArbBundle`](#arbbundle); validates manifest shape consistent with writer; parses JSON per spec UTF-8 rules.
- **Behavior guaranteed by current CI:** Happy path + structural error cases (missing files, invalid JSON, BOM rejection).
- **Compatibility notes:** **Does not** verify hashes — caller must use [`validate_arb`](#validate_arb) for integrity (**§3–§6**).
- **Not guaranteed:** Security against malicious paths (caller supplies `bundle_root`); streaming reads.

---

## `validate_arb`

- **Kind:** function
- **Import path:** `from aurora.arb import validate_arb`
- **Signature:** `validate_arb(bundle_root: str | Path) -> None`
- **Purpose:** Verify **required files**, **canonical JSON on disk** for hashed objects, **`sha256_manifest.json`** structure, **per-file SHA-256** against bytes, **`root_hash.txt`** against manifest bytes — see docstring in `validator.py` (aligned with **§3–§6**).
- **Behavior guaranteed by current CI:** Raises [`ArbValidationError`](#arbvalidationerror) on any failure; success returns `None`.
- **Compatibility notes:** Same **minimal v0.1** scope as writer/reader; **`arb_version`** must remain **`"0.1"`** for normative checks.
- **Not guaranteed:** **Semantic** validation of model outputs, codec checks, or **replay** of audio through a runtime graph.

---

## Validate-only CLI (`python -m aurora.arb`)

**Not** a name in **`__all__`**, but part of the **committed public handoff** (see `src/aurora/arb/__main__.py` and [`../aurora.md`](../aurora.md)).

- **Invocation:** `python -m aurora.arb <bundle-root>` with exactly **one** argument aside from program (see **§7.2** — `sys.argv` length **2** in normal `-m` runs).
- **Behavior:** Calls [`validate_arb`](#validate_arb); prints **`OK: ARB v0.1 bundle is valid.`** on success.
- **Exit codes:** `0` success, `1` validation failure (stderr prefix `ARB_VALIDATION_FAILED: `), `2` usage error.
- **Not guaranteed:** Inspect/read subcommands, replay, or anything beyond validate-only scope (**M30**).

---

## Export list (source of truth)

Alphabetical per **`aurora.arb.__all__`:**

`ArbBundle`, `ArbValidationError`, `canonicalize`, `compute_root_hash`, `read_arb`, `sha256_hex`, `validate_arb`, `write_arb`
