# AURORA — Project Record

**Canonical anchor:** AURORA is the governed acoustic runtime and MediaPipe refactor program tracked in this repository; it is a Foundry-aligned case study and the substrate for PANTANAL-1, aimed at deterministic, artifact-bound, replayable audio execution without pretending the upstream monorepo is already well-governed.

**Status:** Active — milestone **M02** (truthful CI skeleton); **M01** complete (see Milestone ledger)  
**Last updated:** 2026-03-25 — **M01 closeout recorded (UTC):** 2026-03-26T04:00:00Z — **M02 implementation:** see Milestone ledger

This file is the **authoritative project record** for the `aurora/` git repository. It is maintained at milestone boundaries (especially closeout) so the repo stays legible, bounded, and aligned with evidence from audits and preflight locks.

---

## What AURORA is

AURORA is:

- a **governed acoustic runtime** — explicit seams, honest async semantics, and traceable outputs over time
- a **MediaPipe refactor program** — behavior-preserving, evidence-based change on a real fork’s audio-capable surfaces (not a casual whole-repo rewrite)
- a **Foundry-aligned case study** — proves architectural discipline on a large, messy codebase; does not ship MediaPipe code into Foundry
- the **substrate for PANTANAL-1** — the BirdCLEF-facing deployment and observatory narrative sits on top of AURORA and the ORNITHOS model layer

AURORA is not a generic “rewrite MediaPipe” effort, not a backdoor to import upstream implementation into Foundry core, and not a demand that every research path be forced through TFLite on day one.

---

## Workspace and repository model

The workspace groups several directories; **only one is a git repository**:

| Location | Role |
|----------|------|
| **`aurora/`** (this repo) | **Tracked repository.** All commits, branches, and PRs target here only. |
| **`mediapipe/`** (sibling in the workspace) | **Read-only reference clone** for study and evidence. Do not modify. |
| **`docs/`** at workspace root | **Local governance** — milestones, prompts, preflight packs. Read and follow; **do not commit** these into `aurora/`. |

Additional rules:

- **No git repository** at the workspace root — the boundary model depends on a single repo under `aurora/`.
- **No import, copy, or paste** of MediaPipe source from `mediapipe/` into `aurora/`. Architectural learning is allowed; code transfer is not.

---

## Relationship to Foundry

- **AURORA is a case study, not Foundry core.** It may fork and change its own implementation surface.
- **Foundry may learn from AURORA only at the architectural level** — patterns, seams, evidence of what works at scale.
- **No MediaPipe-derived implementation** should be copied into Foundry core. Anything that “graduates” must be re-derived clean-room, implementation-agnostic, and justified beyond a single codebase where possible.

AURORA should remain **explainable in Foundry terms** without becoming dependent on Foundry code.

---

## Relationship to PANTANAL-1, ORNITHOS, and BirdCLEF

Naming and roles:

| Name | Role |
|------|------|
| **AURORA** | Governed runtime and refactor program (this repo’s focus). |
| **ORNITHOS** | Domain model stack — training, scoring, representation learning on top of AURORA surfaces. |
| **PANTANAL-1** | End-to-end deployment, BirdCLEF submission, observatory-style narrative, case study. |
| **BirdCLEF** | Public benchmark and stress test — not the sole definition of success, but a protected proof path. |

**Protected competition rail:** A valid BirdCLEF submission path must remain possible throughout the refactor. Refactor milestones must not block the benchmark; baseline and submission safety are tracked as a **parallel rail** (see *Program Roadmap (proposed)* — C01–C05). Exact repo layout and integration for that rail are **deferred**; the requirement is planning-level until a later milestone locks structure.

---

## Audit-established starting facts

The following are **binding starting truths** from full-repo and finishing audits (see workspace `docs/context/` for full evidence):

1. **Governance lags architecture** — the codebase is worth saving, but repo safety (CI, pins, gates) must be repaired before deep runtime surgery.
2. **The dispatcher seam is real** — almost all Tasks API modules use `SerialDispatcher`; formalizing a `Dispatcher` boundary is feasible and low-risk at the typing layer once prerequisites are met.
3. **Vision task duplication is real** — large, repeated boilerplate; abstraction is justified after seams are normalized.
4. **Audio calculators are modular** — C++ audio calculators are testable, composable ingredients for a future acoustic kernel; they depend on `@com_google_audio_tools`, which must be pinned and treated as a first-class dependency.
5. **TFLite is embedded in graph build macros** — treat TFLite as a **core first-wave dependency**; do not attempt to decouple the whole graph build in early phases.
6. **`@com_google_audio_tools` is a real external dependency** — any extraction or build that touches audio DSP must account for it explicitly.
7. **LIVE_STREAM callback order is not the determinism contract** — offline/batch modes are the strong determinism core; live/async semantics must be documented honestly (timestamps and recorded events, not callback order alone).

---

## Startup invariants and verification posture (preflight)

The workspace **preflight pack** (`docs/preflight/aurora_startup_lock/`) locks **sequencing, boundaries, and proof**, not the contents of this file. Summarized expectations:

- **Behavior preservation is the default** for refactors unless a change is explicitly classified otherwise, with criteria, tests or artifacts, and rollback clarity.
- **CI must be truthful** when introduced: green means safe; no `continue-on-error` on enforcement gates; no placeholder tests; no fake coverage narratives; evidence (logs, artifacts) inspectable after the fact.
- **Invariant surfaces** (public task APIs, Python→C dispatch path, model loading, outputs, async semantics, graph init, audio structural parity with vision, global-state discipline) require explicit verification appropriate to the change — smoke tests, golden outputs where needed, and honest CI.

Detailed tables live in `AURORA_INVARIANTS.md`, `AURORA_RUNTIME_TRUTHS.md`, `AURORA_CI_TRUTHFULNESS.md`, and `AURORA_VERIFICATION_PLAN.md` in the preflight pack.

---

## Execution Phase Boundaries (locked)

These phases define **ordering and permission**, not dates. Work **must not** skip ahead in ways that violate this sequence. This section is **locked** for startup sequencing; it is not the long-range milestone map.

| Phase | Name | What it means |
|-------|------|----------------|
| **A** | **Governance and Safety** | Make the repo safe to change: truthful CI, pins, lint baseline, branch protection, hygiene, canonical docs. **No** runtime seam extraction, dispatcher migration, or task-base refactors yet. |
| **B** | **Runtime Seam Normalization** | Make implicit seams explicit: `Dispatcher` protocol, `image.py` migration off raw CDLL (behavior-preserving), loader/documentation of async semantics, smoke tests per domain. **No** `VisionTaskBase` / `AudioTaskBase`, no C API signature changes, no kernel extraction. |
| **C** | **Abstraction and Deduplication** | Reduce duplication: task bases, data extraction, logging hygiene, honest coverage thresholds when baselines exist. **No** acoustic kernel extraction as a monolithic rewrite; no premature ARB implementation. |
| **D** | **Kernel Extraction (later)** | Extract a governed acoustic kernel — planned only after A–C justify stable surfaces. |

**Explicitly deferred until the right phase:** ARB format, ORNITHOS architecture, graph-spec-as-law implementation, observatory layer, certification/RediAI integration details, Legacy Solutions deprecation without parity and migration story, plugin systems.

**Protected parallel competition rail:** BirdCLEF baseline and submission viability stay a **parallel** concern; refactor work must not eliminate the ability to produce a valid submission candidate.

---

## Program Roadmap (proposed)

This section is a **planning map** — a proposal aligned to the vision and PANTANAL workstreams, **not** a contract. Milestone IDs and ranges may be adjusted; **Execution Phase Boundaries (locked)** still govern what kind of work is allowed when.

### Long-horizon program map (M01–M33)

| Program phase | Theme | Milestones (proposed) |
|---------------|--------|------------------------|
| **I** | Governance closure & safe-to-change baseline | M01–M05 |
| **II** | Runtime seam normalization | M06–M09 |
| **III** | Surface coherence & task abstraction | M10–M14 |
| **IV** | Acoustic kernel extraction | M15–M19 |
| **V** | Artifact runtime & certification boundary | M20–M23 |
| **VI** | ORNITHOS model stack | M24–M28 |
| **VII** | PANTANAL-1 submission, observatory, case study | M29–M33 |

### Protected competition rail (C01–C05) — proposal only

A separate **C01–C05** track is reserved for **baseline and submission safety** (credible BirdCLEF path, frozen candidates, compliance). It runs **alongside** refactor phases; integration points with AURORA runtime surfaces are **not** fixed in M01. Location, tooling, and repo structure for this rail remain **deferred**.

### Next milestone (M03)

**M02** (truthful CI skeleton and repo safety rails) is in flight on branch `m02-truthful-ci-skeleton` — see Milestone ledger. **M03** follows after M02 closeout; plan stub: workspace `docs/milestones/M03/M03_plan.md`.

---

## Success criteria (repo-level)

- **Governance success** — the repo can be changed safely; CI is truthful when present; dependencies and boundaries are explicit; refactors are classifiable and revertible.
- **Runtime success** — loader/dispatcher paths are explicit and testable; duplicated runtime behavior moves behind stable abstractions where justified; audio flows read as a coherent subsystem.
- **Kernel success** — ingestion → features → model → outputs forms a governed pipeline with explicit artifacts and credible offline replay; async semantics stay honest.
- **Case-study success** — Foundry methodology is demonstrated on a real system with publishable architectural evidence; BirdCLEF and PANTANAL-1 can use the story without conflating leaderboard rank with architectural proof.

---

## Working rules for future milestones

1. **Classify** each change (governance, seam, API, kernel, model, artifact boundary, observatory) before coding.
2. **Preserve behavior** unless the milestone explicitly intends otherwise and proves it.
3. **Prefer seam extraction and small moves** over broad rewrites.
4. **Keep milestones small and reversible**, with explicit acceptance criteria and recorded commit SHAs.
5. **Use evidence over narration** — tests, audits, artifacts, diffs, CI logs.

---

## Deferred topics / not yet designed

- ARB (AURORA Run Bundle) specification and tooling
- ORNITHOS architecture and training/inference split
- Certification integration (e.g., RediAI) and CI gating details
- Competition baseline **location, repo layout, and harness** (C01–C05 content)
- Plugin/extension system and task discovery
- Legacy Solutions deprecation timeline and migration guarantees
- Package/module layout inside `aurora/` beyond hosting docs

---

## Milestone ledger

| ID | Title | Status | Initialized | Purpose | Closeout summary |
|----|-------|--------|-------------|---------|------------------|
| **M01** | Governance bootstrap, canonical docs initialization, and README anchor | **Complete** | 2026-03-25 | Establish `aurora/docs/aurora.md` as the committed source of truth; minimal `README.md`; separate locked phases from proposed roadmap; no runtime or `mediapipe/` changes. | Delivered substantive `docs/aurora.md` and minimal `README.md` on PR #1 (`m01-governance-bootstrap` → `main`). Scope verified docs-only: no `mediapipe/` edits; no runtime/code under `aurora/`. Primary delivery commit `f32c205ae21010ed3f09e841d7debc16a65c5095`. Closeout commit `742d9f0ff9c4a9e055d5fd28f46f1c8d265ccc8e` (ledger + header). **PR #1** merged to `main` (merge commit `2f4efea`). **Closeout recorded (UTC):** 2026-03-26T04:00:00Z. |
| **M02** | Truthful CI skeleton and repo safety rails | **In progress** | 2026-03-25 | First GitHub Actions workflow (`ci` / `repo-safety`), stdlib repo verifier, Ruff on `scripts/`, hygiene files; no runtime seam work. | **PR #2** (`m02-truthful-ci-skeleton` → `main`). Primary implementation commit **`4d1817e`**; ledger follow-ups on the same branch. CI **pass** on PR (workflow `ci`, job `repo-safety`). Example run IDs: `23577571189`, `23577573243`. Upload artifact name: **`m02-ci-artifacts`**. Intended GitHub required-check name: **`ci / repo-safety`** — **not** configured in repo settings by this milestone (document only). See workspace `docs/milestones/M02/M02_summary.md`. |

---

## References (workspace; not committed here)

Authoritative narrative and evidence live outside this repo in the workspace, for example:

- `docs/context/AURORA_VISION.md`
- `docs/context/mediapiperefactoraudit.md`, `docs/context/mediapipefinishingaudit.md`
- `docs/context/PANTANAL_1_MOONSHOT.md`
- `docs/preflight/aurora_startup_lock/` (startup locks and phase boundaries)

When those documents change, **this file should be updated at milestone closeout** if the repo-level posture or roadmap needs to stay aligned.
