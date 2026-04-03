# AURORA Run Bundle (ARB) — v0.1 canonical format and deterministic hashing contract

**Status:** **Normative specification** (M26); **M27**/**M28**/**M29** add **stdlib** **`src/aurora/arb/`** — **writer** + **hash** helpers (**`write_arb`**, **`canonicalize`**, **`sha256_hex`**, **`compute_root_hash`**), a **minimal reader** (**`read_arb`**, **`ArbBundle`**), and a **standalone programmatic validator** (**`validate_arb`**, **`ArbValidationError`**) — **no** replay tooling, **no** ARB CLI. This document locks the **implementation-ready** contract for **offline / batch** bundles; **M27**/**M28**/**M29** conform to it for the **minimal valid** tree only.

**Relationship to prior work:** **`docs/aurora_run_bundle_boundary.md`** (M25) defines **intent**, **ownership**, and a **conceptual** tree. This document **narrows** that into **normative v0.1** rules for a **minimal valid** offline/batch ARB. Where they conflict on detail, **this spec wins** for implementers.

**Grounding:** Aligns with workspace **`AURORA_VISION.md`** §9 (*Artifact Model*) at the level of “explicit boundaries over ad hoc blobs”; vision text is not committed here.

---

## 1. Scope and normative replay

### 1.1 In scope (v0.1)

- **Canonical bundle form:** directory tree at rest (see §2).
- **Minimal required files and directories** for a **valid** offline/batch ARB (see §3).
- **`manifest.json`** required fields, including **`arb_version`** (see §4).
- **JSON canonicalization** rules for **deterministic hashing** of JSON artifacts (see §5).
- **SHA-256** hashing contract: what is hashed, in what order, and how the **bundle root hash** is derived (see §6).
- **Optional** archive transport (`.tar` / `.zip`) as **non-normative** wrappers (see §2.3).
- One **realistic but tiny** illustrative example (see §8).

### 1.2 Normative replay statement (offline / batch only)

**Replay** as a **normative** concept in ARB v0.1 applies **only** to **offline** and **batch** execution modes: file-backed inputs, controlled evaluation, and certification-oriented reruns where **recorded inputs + graph/spec + deterministic settings + manifests** support an honest story.

### 1.3 Explicitly out of normative scope (deferred / open)

The following are **not** specified as normative contracts in v0.1:

- **LIVE_STREAM** / async capture bundles, event-log semantics, or callback-order guarantees.
- **Training-run** or **experiment** profiles (seeds, checkpoints, optimizer state as **required** contents).
- **Competition-specific** or **BirdCLEF-only** bundle profiles (belong in downstream repos per **`docs/aurora.md`** — *Proposed downstream repo layout*).
- **YAML graph canonicalization** beyond “hash the **file bytes** as stored” (see §5.3).
- **Certification** execution: **RediAI** (or equivalent) remains **external** — ARB v0.1 describes **artifacts AURORA should be able to produce**, not embedded certifiers.

---

## 2. Bundle form: directory tree and transport wrappers

### 2.1 Canonical identity

The **canonical ARB** is a **directory tree** (the **bundle root**). **Identity**, **validity**, and **hashing** are defined against the **files and directories** under that root as **stored on disk** for JSON-backed rules in §5–§6.

### 2.2 Bundle root

The **bundle root** is the directory that contains the **top-level** `manifest.json` (see §3). Implementations **must not** require a specific root directory name (e.g., the root may be named `run/`, `arb_001/`, or unpacked from an archive); **normative** paths in this spec are **relative to the bundle root**.

### 2.3 Optional archive transport (non-normative wrapper)

**`.tar`**, **`.tar.gz`**, **`.zip`**, or similar **may** be used **only** as **transport** packaging: they **wrap** the **canonical directory tree** without changing the **normative** layout inside. **Hashing** and **validity** **must not** be defined over wrapper bytes (e.g., tar headers, zip central directory metadata) as the **primary** identity surface.

**Rule:** Extract / materialize the tree, then apply §3–§6 to the **extracted** files.

---

## 3. Minimal valid ARB (v0.1, offline / batch)

A **minimal valid** ARB v0.1 for **offline / batch** **must** contain exactly the following **files** at these **relative paths** (directories created as needed):

| Relative path | Role |
|---------------|------|
| **`manifest.json`** | Top-level run manifest (§4). |
| **`graph.yaml`** | Graph / pipeline specification for the run (YAML; **hashed as raw bytes** — §5.3). |
| **`inputs/audio_index.json`** | Input manifest listing audio inputs (JSON; **canonical JSON** — §5). |
| **`segments/segments.json`** | Segment index for the run (JSON; **canonical JSON** — §5). |
| **`predictions/predictions.json`** | Prediction outputs (JSON; **canonical JSON** — §5). |
| **`hashes/sha256_manifest.json`** | Per-file SHA-256 manifest (JSON; **canonical JSON** — §5, §6). |
| **`hashes/root_hash.txt`** | Single line: **64** lowercase hex characters = **SHA-256** of the **canonical JSON** bytes of **`hashes/sha256_manifest.json`** (§6). |

**Optional** directories and files from M25’s conceptual map (e.g., `features/`, `embeddings/`, `metrics/`, `environment/`, `report.md`) **may** appear; they **must** be listed in **`hashes/sha256_manifest.json`** if present **unless** explicitly excluded by §6.1.

---

## 4. `manifest.json` contract (required fields)

The top-level **`manifest.json`** **must** be JSON conforming to §5 and **must** contain at least:

| Field | Type | Meaning |
|-------|------|---------|
| **`arb_version`** | string | **Must** be **`"0.1"`** for this spec revision. |
| **`bundle_id`** | string | Stable identifier for this bundle (e.g., UUID or project-scoped id). |
| **`created_utc`** | string | UTC timestamp in **ISO 8601** form, **Z** suffix (example: **`2026-04-02T12:00:00Z`**). |
| **`runtime_mode`** | string | **Must** be **`"offline_batch"`** for normative v0.1 offline/batch ARBs. |
| **`graph_spec_path`** | string | Relative path to graph spec from bundle root; **must** be **`"graph.yaml"`** for minimal valid ARBs. |
| **`input_manifest_path`** | string | Relative path; **must** be **`"inputs/audio_index.json"`** for minimal valid ARBs. |
| **`hash_manifest_path`** | string | Relative path; **must** be **`"hashes/sha256_manifest.json"`** for minimal valid ARBs. |
| **`root_hash_path`** | string | Relative path; **must** be **`"hashes/root_hash.txt"`** for minimal valid ARBs. |

**Versioning policy:** **`arb_version`** is the **ARB manifest schema** version. Future specs may add fields or values; **`"0.1"`** is frozen for this document.

**Float policy:** **`manifest.json`** **must not** contain JSON **number** values that require floating-point representation. Use **strings**, **integers**, or **booleans** for all manifest fields. (Scores and reals belong in **`predictions/predictions.json`** as **strings** — §5.2.)

---

## 5. Canonicalization and serialization (JSON and YAML)

### 5.1 Text encoding and line endings

- All **JSON** and **YAML** text files listed in §3–§4 **must** be **UTF-8** **without BOM**.
- **Newlines** in JSON/YAML text files **must** be **LF** (`\n`) only.

### 5.2 JSON: strict structural typing for determinism

For every **JSON** file that is **hashed** using **canonical JSON** (§6):

1. **Object keys** **must** be sorted in **ascending lexicographic order** by Unicode code point (UTF-16 code units in JSON’s normal string comparison is **not** used for sorting; sort by **UTF-8** byte sequence of key strings interpreted as Unicode scalar values — implementers: **sort keys as UTF-8 strings lexicographically**).
2. **No insignificant whitespace** outside string values: **no** extra spaces; **no** trailing commas; **compact** serialization (minimal separators).
3. **Forbidden values:** **`NaN`**, **`Infinity`**, **`-Infinity`** are **forbidden** in **any** JSON artifact in scope of this spec.
4. **Numbers:** Prefer **integers**; **avoid floats** in **manifest** and **core structural metadata**. Where a real-valued score **must** appear (e.g., in **`predictions/predictions.json`**), encode it as a **string** holding a **decimal** representation (e.g., **`"0.987"`**, **`"-0.25"`**). If a **float** is **unavoidable** in a future revision, that revision **must** define a **single** normalized decimal string format and **forbid** alternate spellings; **v0.1** **does not** use JSON floats for predictions — use **strings** only for scalar scores.
5. **Arrays:** Order is **significant** unless a field’s definition says otherwise; **do not** reorder arrays that carry ordered semantics.

**Rationale:** Avoid relying on “whatever the JSON encoder does” for floats; match artifact-bound and certification-adjacent practice (M26 lock).

### 5.3 YAML (`graph.yaml`)

For **`graph.yaml`**, **v0.1** **does not** define a YAML canonicalization for hashing. **Per-file hash** is **SHA-256** over the **raw file bytes** **as stored** after §5.1 (UTF-8, LF). **Future** specs may introduce canonical YAML if needed.

---

## 6. Hashing contract (SHA-256)

### 6.1 Hash algorithm

- **Algorithm:** **SHA-256** (256-bit output).
- **Digest encoding:** lowercase **hexadecimal** (**64** characters per digest).

**Rationale:** SHA-256 is the default “boring” choice for artifact manifests and interoperates with common bundle and certification vocabulary; M26 does **not** entertain alternative hash functions.

### 6.2 Which files are hashed

**Listed in `hashes/sha256_manifest.json`:** Every **file** under the bundle root that is **part of the ARB** **except**:

- **`hashes/sha256_manifest.json`** itself (**not** self-listed — avoids circular hashing; see §6.4).
- **`hashes/root_hash.txt`** (derived record of the root hash).

**Normative minimal set:** `manifest.json`, `graph.yaml`, `inputs/audio_index.json`, `segments/segments.json`, `predictions/predictions.json`.

### 6.3 Per-file content hashes

For each **listed** file:

- **`graph.yaml`:** Hash **SHA-256** over the **exact octets** on disk (§5.1, §5.3).
- **JSON** files governed by §5.2 (`manifest.json`, `inputs/audio_index.json`, `segments/segments.json`, `predictions/predictions.json`): First **serialize** to **canonical JSON bytes** (UTF-8, LF), then hash those bytes **as the file’s logical content** for **`sha256_manifest`** listing. **On-disk** files **should** match that canonical form so byte-level hash equals logical hash.

### 6.4 `hashes/sha256_manifest.json`

**Purpose:** Single manifest of **relative POSIX paths** → **SHA-256** hex digests for every **included** file **except** the two exclusions in §6.2.

**Canonical JSON object** (keys sorted per §5.2):

- **`arb_version`**: **`"0.1"`**
- **`files`**: JSON array of objects, **each** with **`path`** (string, relative, forward slashes) and **`sha256`** (64-char lowercase hex). The array **must** be sorted by **`path`** ascending lexicographically (UTF-8 byte order).

**Construction (normative):**

1. Compute the digest for **`graph.yaml`** from **raw bytes** (§5.3).
2. Compute digests for **`manifest.json`**, **`inputs/audio_index.json`**, **`segments/segments.json`**, **`predictions/predictions.json`** from each file’s **on-disk** bytes (which **must** equal **canonical JSON** bytes per §5.2).
3. Build **`files`** from those **five** paths and digests **only** (sorted by **`path`**).
4. Serialize **`hashes/sha256_manifest.json`** in **canonical JSON** form (§5.2). **Do not** add **`hashes/sha256_manifest.json`** to its own **`files`** list.

### 6.5 `hashes/root_hash.txt`

**Content:** Exactly **one** line: the **64**-character lowercase hex **SHA-256** digest of the **canonical JSON bytes** of **`hashes/sha256_manifest.json`** (the file **as stored** on disk after §5.1–§5.2).

**Root hash identity:** The **bundle root hash** is this **SHA-256** value — the **normative** single-hash identity for the ARB v0.1 **given** the hashing rules above.

---

## 7. Non-goals and implementation gaps (explicit)

- **M27** adds a **stdlib-only** **minimal writer** and **hash** helpers under **`src/aurora/arb/`** (**`write_arb`**, **`canonicalize`**, **`sha256_hex`**, **`compute_root_hash`**). **M28** adds a **stdlib-only** **minimal reader** (**`read_arb`**, **`ArbBundle`**) — eager load, **no** implicit hash verification in the reader API. **M29** adds **`validate_arb(bundle_root)`** and **`ArbValidationError`** — **separate** programmatic verification (**`None`** on success, exception on failure); **no** replay tooling, **no** CLI, **no** semantic CI gate on bundle contents beyond existing **`scripts/verify_repo_state.py`** structural checks.
- **No** schema validator beyond what the writer enforces for **minimal valid** v0.1 manifests (the **M29** validator additionally checks **integrity** and **minimal** **`sha256_manifest.json`** structure for v0.1 — not a general-purpose schema engine).
- **Decode**, **graph execution**, **TFLite**, **native** correctness: **unchanged** from Phase D posture — not claimed by this spec.

### 7.1 M29 `validate_arb` — what it proves and does not prove

**Proves (minimal v0.1 offline/batch bundle):**

- Required on-disk layout from §3 exists.
- **`manifest.json`** passes the same minimal rules as **`write_arb`** and is **canonical JSON** on disk (§4–§5.2).
- **`graph.yaml`** is UTF-8 **without BOM** (§5.1); hashed as **raw bytes** (§5.3, §6.3).
- **`inputs/audio_index.json`**, **`segments/segments.json`**, **`predictions/predictions.json`** are **canonical JSON** on disk (§5.2).
- **`hashes/sha256_manifest.json`** matches the §6.4 structural contract (**`arb_version`**, **`files`** sorted by **`path`**, **`path`** / **`sha256`** entries) and is **canonical JSON** on disk.
- Per-file **`sha256`** entries match **SHA-256** recomputed from on-disk bytes for each listed payload path (§6.3).
- **`hashes/root_hash.txt`** (single line, 64 lowercase hex chars) equals **SHA-256** of the **on-disk bytes** of **`hashes/sha256_manifest.json`** (§6.5).

**Does not prove:**

- **Replay** execution, **CLI** tooling, or correctness of **decode** / **graph** / **native** execution.
- That a caller used **`read_arb`** — **load** (**`read_arb`**) and **verify** (**`validate_arb`**) are intentionally **separate** surfaces; bundles may load without verifying.

---

## 8. Minimal illustrative example (realistic but tiny)

**Label:** **Illustrative only** — not a committed fixture; shows **shape** and **field** intent.

### 8.1 Layout

```text
manifest.json
graph.yaml
inputs/audio_index.json
segments/segments.json
predictions/predictions.json
hashes/sha256_manifest.json
hashes/root_hash.txt
```

### 8.2 `manifest.json` (example)

```json
{"arb_version":"0.1","bundle_id":"example-arb-0001","created_utc":"2026-04-02T12:00:00Z","graph_spec_path":"graph.yaml","hash_manifest_path":"hashes/sha256_manifest.json","input_manifest_path":"inputs/audio_index.json","root_hash_path":"hashes/root_hash.txt","runtime_mode":"offline_batch"}
```

### 8.3 `graph.yaml` (example)

```yaml
# Example graph stub — content is hashed as raw bytes in v0.1
version: 0
pipeline: audio_classifier_stub
```

### 8.4 `inputs/audio_index.json` (example)

```json
{"entries":[{"duration_ms":"5000","path":"inputs/example.wav","sample_rate_hz":"16000"}]}
```

(Scalar **reals** as **strings**; **integers** where natural.)

### 8.5 `segments/segments.json` (example)

```json
{"segments":[{"end_ms":"5000","id":"seg-001","input_path":"inputs/example.wav","start_ms":"0"}]}
```

### 8.6 `predictions/predictions.json` (example)

```json
{"predictions":[{"label":"species_a","score":"0.91","segment_id":"seg-001"}]}
```

### 8.7 `hashes/sha256_manifest.json` and `hashes/root_hash.txt`

**Omitted here:** Values depend on **actual** file bytes per §6. **`hashes/sha256_manifest.json`** lists the **five** payload files from §6.2 (not itself, not **`root_hash.txt`**). **`root_hash.txt`** is a **single** line: **64** lowercase hex chars = **SHA-256** of the **canonical JSON bytes** of **`hashes/sha256_manifest.json`**, per §6.5.

---

## Document control

| Item | Value |
|------|-------|
| **Introduced** | M26 — specification only; **not** implementation |
| **Supersedes** | Nothing — **narrows** M25 boundary doc for v0.1 **offline/batch** |
| **Next** | **M27**/**M28**/**M29** delivered **stdlib** **writer/hash** + **reader** + **`validate_arb`** in **`src/aurora/arb/`**; **replay** / **CLI** — future milestones when explicitly authorized |
