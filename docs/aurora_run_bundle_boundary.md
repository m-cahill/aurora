# AURORA Run Bundle (ARB) — boundary and v0 conceptual specification

**Status:** **Boundary / specification only** (M25). This document **does not** claim that ARB is implemented in **`src/aurora/`**, that a concrete on-disk format is frozen, or that replay tooling exists. It refines the vision sketch into an explicit, reviewable repo surface for downstream milestones.

**Grounding:** The conceptual bundle shape below starts from the workspace vision narrative **`AURORA_VISION.md`** §9.2 (*Artifact Model* — suggested bundle layout). That vision lives outside this repository; this file is the **committed** anchor for ARB in **`aurora/`** and must stay aligned with **`docs/aurora.md`** on determinism, certification, and ownership.

---

## 1. Purpose of ARB

**ARB (AURORA Run Bundle)** is the intended **deterministic run artifact** for AURORA: a bounded package that ties together what was run (graph/spec, inputs, mode, settings), what was produced (artifacts at explicit pipeline boundaries), and how to **audit** and **replay** an **offline / batch** execution.

M25 locks **intent and vocabulary** so later milestones can implement writers, readers, hashing, and CI without inventing a competing concept.

---

## 2. Why ARB belongs in AURORA

- **AURORA** owns the **generic governed runtime substrate** and **artifact-bound execution** as a matter of architecture — not competition-specific packaging (see **`docs/aurora.md`** — *Proposed downstream repo layout and dependency directionality*).
- A portable **run bundle** is the natural **interface** between runtime execution, external **certification**, and **replay** tooling. Defining ARB here keeps that interface **explicit** and **separate** from ORNITHOS training artifacts and PANTANAL-1 submission bundles.
- The committed record previously listed “ARB specification and tooling” under **Deferred topics**. M25 narrows that to: **committed boundary/spec** exists; **implementation** remains deferred.

---

## 3. Minimal v0 conceptual bundle shape

The following is a **conceptual** layout — **not** a mandatory file tree for implementers yet. It follows the vision sketch (§9.2): meaningful directories and manifests over ad hoc blobs.

```text
run/
  manifest.json
  graph.yaml
  inputs/
    audio_index.json
    metadata.json
  segments/
    segments.json
  features/
    spectrogram_manifest.json
    mel/
    mfcc/
  embeddings/
    embeddings_manifest.json
  predictions/
    predictions.json
    logits.npy
  verifiers/
    verifier_report.json
  metrics/
    metrics.json
  environment/
    versions.json
    hardware.json
    seeds.json
  hashes/
    sha256_manifest.json
  report.md
```

**Notes:**

- Not every run needs every directory; **explicit boundaries** matter more than a fixed shape.
- **Schema**, **serialization**, **versioning**, and **canonical hashing** of this tree are **out of scope** for M25 (see **Non-goals**).
- Names like `manifest.json` / `graph.yaml` are **illustrative**; a future milestone may choose different top-level names or split manifests.

---

## 4. Determinism and replay principles

**Normative contract (M25):** The **strong** determinism and replay story applies to **offline** and **batch** modes — file-backed inference, controlled evaluation, and certification-oriented reruns — consistent with **`docs/aurora.md`** (*Audit-established starting facts*): **offline/batch** modes are the **contractual core** for determinism.

**Out of scope for the ARB contract in M25:**

- **LIVE_STREAM** / async callback **arrival order** as a determinism guarantee (timestamps and **recorded events**, not raw callback order, are the honest replay surface).
- **Training-run** containment (seeds, optimizer snapshots, augmentation config) as **required** bundle contents. These may be revisited as **future** ARB profiles or **open questions**; they are **not** part of the M25-locked **offline/batch** contract.

Replay should be defined over **recorded inputs + graph/spec + deterministic settings + manifests**, for modes where that story is technically honest.

---

## 5. Certification boundary (RediAI external)

Following the vision (**§9.3 Certification boundary**):

- **AURORA** is expected to **produce** bundles suitable for inspection.
- **RediAI** (or equivalent) remains **external** — **validation** and **certification** are **boundary** concerns, **not** embedded in core runtime execution in this milestone.
- If ARB later aligns with an EPB-compatible or EPB-profiled format, that is **optional** and **not** a M25 requirement.

---

## 6. Ownership boundary vs ORNITHOS and PANTANAL-1

| Concern | Owner |
|--------|--------|
| **Generic** run bundle concept, runtime-level artifact boundaries, offline replay vocabulary | **AURORA** (this repo — **spec** in M25; **implementation** deferred) |
| **Bioacoustic model stack**, training pipelines, heads, exports that **consume** AURORA | **ORNITHOS** |
| **BirdCLEF-facing** submission packaging, competition-specific orchestration, observatory narrative | **PANTANAL-1** |

**Rule:** Competition-only or species-specific **content** should not be **smuggled** into ARB as if it were generic runtime vocabulary. Profiles or **extensions** may be defined in later milestones; M25 does not define them.

---

## 7. Explicit non-goals (M25)

- Any **`src/aurora/`** code: **no** ARB writer, reader, schema enforcement, or hash implementation.
- **No** claim of **decode**, **graph**, **TFLite**, **native** execution, or **MediaPipe** correctness — unchanged from Phase D closure posture.
- **No** new **execution-phase row** in **`docs/aurora.md`** *Execution Phase Boundaries (locked)* — see **§9**.
- **No** ORNITHOS or PANTANAL-1 repository creation; **no** Kaggle/submission implementation.

---

## 8. Execution phase labeling (explicit)

**M25** ARB boundary/spec work proceeds **without** canonizing a new **formal post–Phase D execution-phase label** in **`docs/aurora.md`**. The **post–Phase D** execution-phase name remains **unset** until a **later** milestone **explicitly** locks a single sharp execution objective for that row — consistent with **M24** and the Phase E readiness posture.

---

## 9. Open questions and deferred decisions

- Concrete **on-disk format** (single archive vs directory tree), **manifest schema**, and **version field** policy.
- **Writer/reader** APIs, **canonicalization** rules for hashing, and **CI** gates.
- Optional **training-run** or **experiment** profiles (seeds, checkpoints) — **not** part of the M25 offline/batch contract.
- **LIVE_STREAM** / async capture semantics for bundles (event logs, timestamp alignment) beyond the honest non-contract in **§4**.
- Alignment with **EPB** or other external certification formats — **nice-to-have**, not blocking.

---

## Document control

| Item | Value |
|------|--------|
| **Introduced** | M25 — docs-only; verifier enforces presence of this path |
| **Implementation** | **Deferred** — see **`docs/aurora.md`** *Deferred topics* |
