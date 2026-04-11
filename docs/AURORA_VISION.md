# AURORA

## Acoustic Unified Runtime for Observable, Replayable Acoustics

### Foundry Case Study Vision Document

**Status:** Canonical vision / anchoring document  
**Role:** Shared context for GPT, Cursor, and future contributors  
**Last updated:** 2026-04-10

**Related (committed, operational):** [`docs/aurora.md`](aurora.md) (authoritative project record and ledger); [`docs/AURORA_OPERATING_MANUAL.md`](AURORA_OPERATING_MANUAL.md) (how to use and verify the repo today); [`README.md`](../README.md) (public landing and documentation map).

---

# Canonical Anchor Statement

> **AURORA** is a governed acoustic runtime and refactor program built on top of a MediaPipe fork and used as a flagship **Foundry case study**. Its purpose is to turn a high-entropy, real-world perception framework into a deterministic, artifact-bound, replayable audio system with explicit runtime seams, auditable outputs, and a credible external proof point in BirdCLEF 2026. AURORA is not a generic “rewrite MediaPipe” effort. It is a disciplined transformation of MediaPipe’s audio-related substrate into a governed acoustic kernel whose outputs can be traced, replayed, evaluated, and eventually certified at the artifact boundary.

---

# 1. Executive Summary

AURORA exists at the intersection of four goals:

1. **Refactor a real, complex upstream system** rather than building a toy greenfield demo.
2. **Demonstrate the Foundry thesis** on a live system: small, stable architectural primitives and explicit runtime boundaries can impose order on high-entropy software.
3. **Produce a reusable acoustic kernel** that can support research, evaluation, and deployment use cases.
4. **Validate the result publicly** through BirdCLEF 2026 and the broader “Pantanal Listening Engine” effort.

AURORA should be understood in three ways at once:

- a **MediaPipe governance and runtime program**
- a **Foundry-aligned case study**
- the **substrate** for a larger bioacoustic system

The central idea is simple:

> **Make the system safe to change, then make the runtime explicit, then make the surface coherent, then extract the kernel.**

That sequence is the backbone of AURORA.

---

# 2. Why AURORA Exists

Modern audio ML systems are often strong on modeling and weak on systems discipline. In practice they are frequently:

- notebook-centric
- difficult to replay
- weakly versioned
- hard to audit
- rich in implicit state
- fragile at the Python/native boundary
- optimized for leaderboard iteration rather than architectural integrity

MediaPipe is a compelling study surface because it is already powerful:

- graph-based execution
- modular calculators
- task APIs
- cross-platform ambitions
- a substantial C++ runtime substrate

But it also shows the classic symptoms of long-lived, successful infrastructure:

- multiple overlapping API surfaces
- weak repo governance relative to system size
- substantial wrapper duplication
- hidden assumptions at runtime boundaries
- insufficient artifact visibility
- incomplete determinism story for async/live modes

AURORA exists to address those issues in a way that preserves MediaPipe’s strengths instead of discarding them.

---

# 3. Relationship to Foundry

## 3.1 AURORA is a Foundry case study, not Foundry core

Foundry is a clean-room, audit-first architecture program that extracts recurring patterns from major systems and implements them as minimal, composable primitives. AURORA is **not** a direct extension of the Foundry core repository and should not be treated as such.

AURORA is an **external case study** that tests whether Foundry’s ideas hold up when applied to a large, messy, real-world codebase.

That distinction matters.

### Foundry core
- clean-room primitives
- minimal architecture substrate
- cross-system validation before primitive admission
- no upstream code copying into the kernel

### AURORA case study
- operates on a **forked implementation surface**
- may directly modify MediaPipe inside its own repository
- is allowed to pursue behavior-preserving refactors in place
- produces architectural evidence, not automatic primitive admissions

## 3.2 Clean-room boundary

The Foundry clean-room rule still applies at the conceptual boundary:

- **AURORA may modify its own fork.**
- **Foundry may learn from AURORA only at the architectural level.**
- **No MediaPipe-derived implementation should be copied into Foundry core.**
- Any future Foundry primitive influenced by AURORA must be:
  - architecture-first
  - implementation-agnostic
  - justified across more than one source system when possible
  - re-derived clean-room

## 3.3 What AURORA proves for Foundry

If successful, AURORA demonstrates that Foundry’s methodology can:

- impose governance on a large perception framework
- expose and normalize runtime seams
- isolate a reusable kernel from a monorepo
- preserve behavior while improving determinism and traceability
- produce public proof of value under competitive conditions

That is a much stronger validation than a toy proof.

---

# 4. What AURORA Is

AURORA is:

- a **governed acoustic runtime**
- a **refactor program** centered on MediaPipe’s audio-capable surfaces
- a **determinism and replay effort**
- an **artifact-bound execution model**
- a **case study in Foundry-aligned system transformation**
- the **substrate** for the final BirdCLEF 2026 moonshot project

AURORA is not:

- a repo-wide rewrite for its own sake
- a claim that every MediaPipe subsystem must be unified immediately
- a demand that all model research be forced into TFLite on day one
- a generic Kaggle notebook stack
- a production planetary observatory from day one
- a backdoor way of importing MediaPipe code into Foundry core

---

# 5. The System Under Study

## 5.1 Upstream study surface

The current study surface is a fork of MediaPipe with particular attention to:

- `mediapipe/tasks/python/`
- `mediapipe/tasks/cc/`
- `mediapipe/calculators/audio/`
- graph/runtime seams in the C++ task and calculator layers
- Python/native boundary and dispatch behavior
- legacy-vs-tasks API overlap
- build-system constraints affecting extraction

## 5.2 What the audits already established

The audit work matters and should be treated as binding context.

### Confirmed truths
- The repo is large, serious, and worth the effort.
- The architecture is salvageable.
- Repo governance is weaker than the architecture and must be repaired first.
- The dispatcher seam is real.
- Vision-task duplication is real and can be abstracted safely.
- Audio calculators are modular enough to form the basis of a kernel.
- TFLite is deeply embedded in the current build macros and should be treated as a core dependency rather than prematurely abstracted away.
- `@com_google_audio_tools` is a real external audio dependency and must be pinned and managed explicitly.
- LIVE_STREAM callback ordering is not a contractual deterministic surface and must be documented accordingly.

### Working interpretation
AURORA is feasible as a phased program because the codebase has real seams and bounded risks. It is **not** feasible as a casual whole-repo rewrite.

---

# 6. The AURORA Target Architecture

## 6.1 Layered mental model

```text
MediaPipe fork
  ↓
Governed runtime seams
  ↓
AURORA acoustic kernel
  ↓
Model adapters and inference nodes
  ↓
Artifact bundles, replay, certification boundary
  ↓
Observatory / benchmark deployments
```

## 6.2 Canonical AURORA layers

### Layer 1 — Upstream substrate
The forked MediaPipe runtime, task bindings, graph engine, calculators, and build rules.

### Layer 2 — Governance and runtime control
The seams that make the substrate safe to evolve:

- CI and branch protection
- dependency pinning
- coverage and drift detection
- loader/dispatcher abstractions
- lifecycle normalization
- documented public/internal boundaries

### Layer 3 — Acoustic kernel
The smallest coherent audio-focused runtime surface we are trying to create. At minimum it should support:

- audio ingestion
- segmentation and framing
- resampling and filtering
- feature extraction
- model-node invocation through adapters
- result conversion
- artifact emission
- replay
- deterministic offline execution

### Layer 4 — Domain model stack
The BirdCLEF-facing model layer (ORNITHOS) that consumes AURORA surfaces rather than bypassing them.

### Layer 5 — Observatory and external proof
The final system deployment surface (PANTANAL-1), BirdCLEF benchmark harness, public write-up, and artifact-boundary certification.

## 6.3 Graph spec as law

AURORA aims to make the graph definition itself a first-class governance object.

The desired end state is that a run can be explained by a small set of explicit inputs:

- graph spec
- model references
- runtime mode
- deterministic settings
- input manifest
- environment capture
- artifact bundle hash

The graph is not just execution machinery. It is part of the audit surface.

---

# 7. Canonical AURORA Components

## 7.1 Dispatcher and LibraryLoader seam

The Python/native boundary is one of the most important leverage points.

AURORA treats the current loading and dispatch path as a proper service boundary, not an incidental implementation detail.

Desired properties:

- injectable loader rather than hardwired singleton access
- dispatcher abstraction rather than concrete coupling
- testability of Python/native interaction
- explicit lifecycle and shutdown semantics
- isolation of raw-CDLL paths
- a clear rule for which modes are synchronous vs asynchronous

This seam is foundational because it affects determinism, testability, and future backend flexibility.

## 7.2 Task base abstractions

AURORA favors extracting behavior-preserving base abstractions where repetition is already obvious and uniform.

Examples:
- `VisionTaskBase` as a refactor enabler and proof of runtime normalization
- `AudioTaskBase` as the acoustic analogue
- shared lifecycle, resource, and result-handling code
- pluggable option/result converters

These bases are not ends in themselves. They are a way to create stable runtime surfaces.

## 7.3 Acoustic DSP kernel

The modular audio calculators are a major asset. AURORA should preserve and eventually expose a coherent audio kernel built from capabilities such as:

- framing/windowing
- resampling
- spectrogram generation
- mel/MFCC extraction
- log stabilization
- simple FIR filtering
- audio decoding

The long-term goal is not merely “keep the calculators.” It is to make them legible as reusable kernel primitives.

## 7.4 Artifact-bound execution

AURORA should produce explicit artifacts at meaningful boundaries.

At a minimum, a run should be able to yield:

- input manifest
- segment index
- feature artifacts
- embedding artifacts when applicable
- prediction artifacts
- verifier outputs
- metrics
- environment and dependency record
- canonical hashes

AURORA should prefer explicit artifacts over hidden in-memory state whenever the choice affects auditability or replay.

## 7.5 Replay and trace

Replay is a first-class design target.

AURORA’s offline modes should support:
- deterministic re-run under the same graph and inputs
- traceable transitions through major pipeline stages
- artifact-based debugging rather than guesswork
- failure replay from recorded inputs and graph state

For async/live settings, replayability should be defined over **recorded events and timestamps**, not wall-clock callback order.

## 7.6 Verifier and policy layer

AURORA should support post-inference verifier logic as part of the runtime surface, not as ad hoc scripts bolted on afterward.

Examples:
- frequency-band sanity checks
- temporal consistency checks
- co-occurrence rules
- domain priors
- output-shaping or confidence penalties
- policy checks over artifact completeness

This is where AURORA begins to look like a governed observatory substrate rather than a loose model pipeline.

---

# 8. Determinism Model

## 8.1 Offline modes are the contractual core

The strongest deterministic guarantees should attach to:
- batch runs
- file-backed inference
- timestamp-addressable offline streams
- controlled evaluation and certification runs

For these modes, the expectation is:

> same graph + same input manifest + same model versions + same deterministic settings = same logical artifacts

## 8.2 Live mode is explicitly weaker

The audits already surfaced a critical rule: callback arrival order in LIVE_STREAM mode is not the right determinism contract.

Therefore, AURORA should define live-mode semantics explicitly:

- arrival order of Python callbacks is **not** the primary stable surface
- input timestamps and sequence IDs are the stable addressing mechanism
- replay should be based on recorded event order / source timestamps
- any user-facing docs must avoid overpromising total order guarantees in async mode

## 8.3 Training determinism is containment, not mythology

AURORA should distinguish inference determinism from training determinism.

Training is allowed to use stochastic methods, but the system should still record:
- seeds
- augmentation configuration
- optimizer state snapshots when relevant
- model/data version
- environment capture
- exact run config

The policy is:
- **contain nondeterminism**
- **do not pretend it does not exist**
- **make it measurable and inspectable**

---

# 9. Artifact Model

## 9.1 Canonical bundle concept

AURORA should standardize around a deterministic run bundle. A practical initial name is:

**AURORA Run Bundle (ARB)**

The name is intentionally neutral: it does not overcommit to a final public spec while still making the artifact surface concrete.

## 9.2 Suggested bundle shape

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

Not every run needs every directory. The important point is that meaningful boundaries are explicit.

## 9.3 Certification boundary

RediAI should remain external to the runtime. AURORA should not embed certification logic into core execution.

The desired boundary is:

- **AURORA produces bundles**
- **RediAI validates bundles**
- certification remains a boundary concern, not runtime entanglement

If ARB later converges to an EPB-compatible or EPB-profiled artifact format, that is a strong bonus, but it is not a required starting condition.

---

# 10. Foundry Primitive Mapping

AURORA is not required to literally import Foundry primitives, but it should be explainable in Foundry terms.

| Foundry primitive | AURORA analogue |
|---|---|
| `graph_executor` | explicit audio graph execution and node dependency model |
| `append_only_log` | ordered artifact/event history for runs and replay |
| `versioned_state_store` | versioned configs, model manifests, graph manifests, label maps |
| `event_bus` | observatory events, run events, completion signals, evaluation notifications |
| `reconciliation_loop` | verifier agents, policy checks, consistency enforcement |
| `task_scheduler` | queued run scheduling for evaluation and batch processing |
| `task_executor` | node/task execution substrate for training/evaluation jobs |
| `workflow_runtime` | multi-step training/evaluation/submission/certification orchestration |

This mapping is conceptual evidence. It is not permission to collapse AURORA into Foundry or vice versa.

---

# 11. Scope Boundaries

## 11.1 In scope
- MediaPipe fork hardening
- governance closure
- runtime seam normalization
- task-base extraction where justified
- audio kernel extraction
- artifact bundle design
- replay semantics
- BirdCLEF integration
- case-study evidence and documentation
- optional artifact certification at the boundary

## 11.2 Explicitly deferred or out of scope
- replacing TFLite across the system in the first wave
- forcing every training/inference flow through one backend immediately
- production global deployment
- full multi-platform productization on day one
- premature admission of AURORA code into Foundry core
- speculative primitive creation without evidence

---

# 12. Success Criteria

AURORA is successful if it delivers most of the following:

## 12.1 Governance success
- repo can be changed safely
- CI is truthful
- dependency posture is explicit
- behavior-preserving refactors are enforceable

## 12.2 Runtime success
- the loader/dispatcher path is explicit and testable
- duplicated runtime behavior is normalized behind stable abstractions
- audio flows are legible as a coherent subsystem

## 12.3 Kernel success
- audio ingestion → feature → model → output can be expressed as a governed pipeline
- artifact emission is explicit
- offline replay is credible
- async semantics are documented honestly

## 12.4 Case-study success
- AURORA clearly demonstrates the Foundry methodology on a real system
- architectural evidence is publishable
- the system can support BirdCLEF 2026 as a public proof point

## 12.5 Certification success
- bundles are stable enough that external verification is meaningful
- certification is a boundary layer, not an entangled implementation detail

Winning BirdCLEF would be excellent, but it is not the sole success condition for AURORA.

---

# 13. Operating Instructions for GPT / Cursor

When working on AURORA, use the following defaults.

## 13.1 Classify the work before changing code

Every change should first be classified as one of:
- governance
- runtime seam
- API surface
- kernel extraction
- model layer
- artifact/certification boundary
- observatory/demo layer

Do not jump levels casually.

## 13.2 Prefer seam extraction over sweeping rewrites

If a change can be expressed as:
- a new abstraction boundary
- a new documented interface
- a migrated call path
- a base-class extraction
- an additive runtime service

prefer that over invasive, multi-area rewrites.

## 13.3 Preserve behavior unless change is explicitly intended

Behavior-changing modifications require:
- a stated reason
- acceptance criteria
- tests or artifact evidence
- rollback clarity

## 13.4 Keep milestones small and revertible

AURORA should follow the same discipline used elsewhere:
- small milestones
- explicit acceptance criteria
- summary + audit
- deferred items called out clearly
- avoid needless CI churn after closure

## 13.5 Do not violate Foundry’s clean-room boundary

AURORA is allowed to modify the fork. Foundry is not allowed to ingest those modifications as-is.

Any idea that “graduates” from AURORA into Foundry must be re-expressed clean-room as an architectural primitive or composition.

## 13.6 Treat evidence as the source of truth

When in doubt, prefer:
- tests
- audits
- artifact bundles
- runtime traces
- measurements
- explicit code references

over narrative confidence.

---

# 14. Canonical Naming

Use these names consistently.

| Name | Meaning |
|---|---|
| **AURORA** | the governed acoustic runtime and MediaPipe refactor program |
| **ORNITHOS** | the bird/wildlife model layer that runs on top of AURORA |
| **PANTANAL-1** | the final BirdCLEF 2026 moonshot deployment / observatory case study |
| **ARB** | AURORA Run Bundle, the artifact surface for deterministic runs |

This naming system keeps the kernel, the model stack, and the final deployment distinct.

---

# 15. Final One-Sentence Summary

> **AURORA is a Foundry-aligned, audit-first transformation of a MediaPipe fork into a governed acoustic kernel whose value is proved not by rhetoric but by deterministic artifacts, replayable execution, and public validation through BirdCLEF 2026.**
