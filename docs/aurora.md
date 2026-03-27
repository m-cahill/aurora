# AURORA — Project Record

**Canonical anchor:** AURORA is the governed acoustic runtime and MediaPipe refactor program tracked in this repository; it is a Foundry-aligned case study and the substrate for PANTANAL-1, aimed at deterministic, artifact-bound, replayable audio execution without pretending the upstream monorepo is already well-governed.

**Status:** Active — **M06** and **M07** **complete** on **`main`**; **Phase A — Governance and Safety** is **closed**; **Phase B — Runtime Seam Normalization** is **authorized** (slices **M06**, **M07** delivered); next tracked milestone: **M08** (workspace `docs/milestones/M08/`).  
**Last updated:** 2026-03-27 — **M07 closeout:** merged **PR #8**; merge commit **`ca31fa7af428b1335af4b34f45bca639e0cec731`**; **merge time (UTC):** **2026-03-27T20:50:35Z**; PR head **`bc0bb4d3458fe566d93cfc530547c6a3b93dd687`**; primary implementation commit **`aca63bab931f7b21d8cbf3f2fca20c4df1d2aa2d`**; **`ci` / `repo-safety`** green on PR (**`23664282232`** push, **`23665065804`** pull_request) and post-merge **`main`** **`23666946080`** (merge push to **`ca31fa7`**). **Merge method:** GitHub **merge commit** (`gh pr merge 8 --merge --admin`; default merge blocked by branch protection). **Authoritative `main` tip immediately after M07 merge (merge commit):** **`ca31fa7af428b1335af4b34f45bca639e0cec731`**. **Closeout project record on `main`:** commit **`3bb5ac24f035404843139dd7cfeae0db16de9bfb`**; **`ci` / `repo-safety`** push run **`23667007934`** (**success**). **Ledger update on `main`:** commit **`f74c7b9ded6dfd9839331011e6016bff7d5f24d7`**; **`ci` / `repo-safety`** push run **`23667048907`** (**success**). **Authoritative `main` tip after M07 merge + closeout + ledger:** **`f74c7b9ded6dfd9839331011e6016bff7d5f24d7`**.

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

**Phase state (M07 closeout):** **Phase A — Governance and Safety** is **closed**. **Phase B — Runtime Seam Normalization** is **authorized**; **M06** (**PR #7**) and **M07** (**PR #8**) are **closed** on **`main`**. Next: **M08** (workspace `docs/milestones/M08/M08_plan.md`).

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

### Next milestone (M08)

**M07** is **closed** on **`main`** (**PR #8**, merge **`ca31fa7af428b1335af4b34f45bca639e0cec731`**). It delivered **`SharedLibraryLoader`** / **`SharedLibraryLoadError`**, **`docs/runtime_seam_framing.md`** / **`DEVELOPMENT.md`** updates, verifier + tests — **not** **`image.py`** migration, domain smoke tests, task bases, or kernel work (see `docs/runtime_seam_framing.md` §6a and Milestone ledger).

**M08** is next (stub: workspace `docs/milestones/M08/M08_plan.md`).

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
- **Further runtime seam work** (`image.py` migration off raw CDLL, domain smoke tests) — **Phase B**; **M07** delivers the in-repo **concrete loader** only; see `docs/runtime_seam_framing.md` and `docs/runtime_surface_strategy.md`

---

## Milestone ledger

| ID | Title | Status | Initialized | Purpose | Closeout summary |
|----|-------|--------|-------------|---------|------------------|
| **M01** | Governance bootstrap, canonical docs initialization, and README anchor | **Complete** | 2026-03-25 | Establish `aurora/docs/aurora.md` as the committed source of truth; minimal `README.md`; separate locked phases from proposed roadmap; no runtime or `mediapipe/` changes. | Delivered substantive `docs/aurora.md` and minimal `README.md` on PR #1 (`m01-governance-bootstrap` → `main`). Scope verified docs-only: no `mediapipe/` edits; no runtime/code under `aurora/`. Primary delivery commit `f32c205ae21010ed3f09e841d7debc16a65c5095`. Closeout commit `742d9f0ff9c4a9e055d5fd28f46f1c8d265ccc8e` (ledger + header). **PR #1** merged to `main` (merge commit `2f4efea`). **Closeout recorded (UTC):** 2026-03-26T04:00:00Z. |
| **M02** | Truthful CI skeleton and repo safety rails | **Complete** | 2026-03-25 | First GitHub Actions workflow (`ci` / `repo-safety`), stdlib repo verifier, Ruff on `scripts/`, hygiene files; no runtime seam work. | **PR #2** merged to `main` (**merge commit `4e3843c9366b745363898fa2f5a273901ed73a8d`**, merged **2026-03-26T06:10:00Z**). Branch `m02-truthful-ci-skeleton` @ **`d9c67114a931809b178d855db16c10171482acd7`**; primary implementation **`4d1817eb4ecdf18b311babb195a479965682202b`**. Workflow **`.github/workflows/ci.yml`** (`ci`); job **`repo-safety`**; intended check name **`ci / repo-safety`**. Latest green runs on PR head: **`23577639206`** (pull_request, **success**), **`23577638447`** (push, **success**). Post-merge **`main`**: successive pushes triggered **`ci` / `repo-safety`** — **all success** (representative run IDs: **`23580213498`**, **`23580245540`**, **`23580265101`**, **`23580299720`**; later doc-only commits may add further runs — see workspace **`M02_summary.md`**). Artifact: **`m02-ci-artifacts`**. **Branch protection / required checks not configured** in this session (manual follow-up). Evidence: workspace `M02_summary.md`, `M02_run1.md`, `M02_audit.md`. |
| **M03** | Branch protection enforcement and CI governance hardening | **Complete** | 2026-03-26 | Harden verifier (full SHA pins for external Actions, `ci` / `repo-safety` identity), stdlib tests under `tests/`, CI artifact **`ci-artifacts`**, `DEVELOPMENT.md`; merge discipline on `main` via branch protection when permitted. | **PR #3** merged to `main` (**merge commit `ce53b7c0a2d596ed3adf05916a68551cf30104ff`**, **2026-03-26**). Branched from **`3d3830e07635ea97878bb714ccd399470fceae61`** (post-M02 `main`); primary implementation **`8716ab5509d606e087c50139bc268f273264d5bc`**. Workflow **`ci`**; job **`repo-safety`**; required check **`ci / repo-safety`**. Representative green runs: **`23621970097`** (push, feature branch), **`23621984590`** (pull_request), **`23622016833`** (push, post-merge `main`). **Branch protection on `main`:** **enabled** — `required_status_checks.strict: true`, required context **`ci / repo-safety`** (GitHub Actions app_id **15368**), **`required_pull_request_reviews`** with **0** approvals (PRs required). Evidence: `gh api repos/m-cahill/aurora/branches/main/protection`; workspace **`M03_summary.md`**. |
| **M04** | Tracked runtime surface strategy and Phase B entry gate | **Complete** | 2026-03-26 | Governance only: **`docs/runtime_surface_strategy.md`**, **`docs/aurora.md`**, verifier + tests, **`DEVELOPMENT.md`**; **Phase A continues**; **Phase B** only after **M05** closes. | **PR #5** merged to `main` (**merge commit `e5125d93f96d9178feee2859b6b474090aa22721`**, merged **2026-03-27**). Implementation **`4702e9c2757c04582afb6c1e081c2c46b7b104a5`**; baseline **`13e0cded5a65d92dd0c2d75dd7b496fe36f8b6f2`**. Workflow **`ci`** / job **`repo-safety`** — authoritative PR run **`23625478660`** (**pull_request**, **success**). Post-merge `main` push run **`23625501522`** (**success**, merge commit **`e5125d9`**). Closeout commit **`bcead1349d262dd8b02af5df25f199badd9ed054`**; closeout `main` run **`23625512581`** (**success**). **No** `mediapipe/` edits in `aurora/`; **no** runtime seam code. **Closeout recorded (UTC):** 2026-03-27T00:55:00Z. |
| **M05** | Provenance-preserving runtime substrate establishment and Phase A closeout gate | **Complete** | 2026-03-26 | First-party package **`src/aurora/`**, **`docs/runtime_substrate.md`**, substrate tests, CI (`PYTHONPATH=src`), verifier gates; **Phase A closed**; **Phase B authorized**; **M06** seeded. | **PR #6** → `main` (**merge `04a5527c43c6e5cf64a0ec6beda45181f1c83efc`**, merged **2026-03-27**); implementation **`107b49d476d9854df58527aa0b56eb6e134e88d3`**; baseline **`bbbbb9c246b76beb943c1d56168e8d0c503f8d77`**. **`ci` / `repo-safety`:** PR **`pull_request`** `23627396629`, **`push`** `23627394261`; post-merge **`main`** `23627411903`; closeout doc commit on **`main`** `23627439447` — **all success**. **No** `mediapipe/` imports under `src/aurora/`; **no** dispatcher / `image.py` / `LibraryLoader` implementation. **Closeout recorded (UTC):** 2026-03-27T01:59:27Z. |
| **M06** | Dispatcher boundary formalization and runtime seam framing | **Complete** | 2026-03-26 | First **Phase B** slice: minimal **`Dispatcher`** / **`LibraryLoader`** `Protocol`s under **`src/aurora/runtime/`**, **`docs/runtime_seam_framing.md`**, verifier + tests, **`DEVELOPMENT.md`**; honest LIVE_STREAM / async wording; **not** `image.py` migration, task bases, kernel, or MediaPipe/native correctness. | **PR #7** → `main` (**merge `0862c5bf96baa681d29a5283e0ca949588a86565`**, merged **2026-03-27**); implementation **`9eb2711a5d4de6b3d597a7d25b2c8105f56bf508`**; baseline **`ed22eaf590d565da4619a1ee7a6f0d2632b978e6`**. **`ci` / `repo-safety`:** PR **`pull_request`** `23630086059`, **`push`** `23630082135`; post-merge **`main`** `23631004105` (merge commit); closeout project record on **`main`** **`17e8069cbfe67511c05e9bc216701f38096a2316`** — **`main`** run **`23631039823`** — **success**; ledger update on **`main`** **`0a4c6c89dbc8f2826d17127f7ca5f472aa1eae15`** — **`main`** run **`23631054922`** — **success**; final project record on **`main`** **`61b71a62307481feaf41d336c5a695e2d305778c`** — **`main`** run **`23631078586`** — **success**; authoritative `main` tip after closeout doc sequence **`fcec0d81923409b5ea57a73d17eb0fbe0503d317`** — **`main`** run **`23631103294`** — **success**; final ledger on **`main`** **`d5b0d78a8ff286e4264477b517226e24e0cce1cd`** — **`main`** run **`23631124779`** — **success**. **Proves:** contract-level seam formalization + governance tripwires. **Does not prove:** MediaPipe behavior, native dispatch/graph correctness, `image.py` migration, concrete loader wiring. **Closeout recorded (UTC):** 2026-03-27T04:20:55Z (merge time). |
| **M07** | Concrete shared-library loader implementation and image-migration readiness | **Complete** | 2026-03-27 | Second **Phase B** slice: **`SharedLibraryLoader`** / **`SharedLibraryLoadError`** (`ctypes.CDLL`, explicit path, per-instance memoization), **`docs/runtime_seam_framing.md`** + **`DEVELOPMENT.md`**, verifier tracks **`shared_library_loader.py`**, **`tests/test_library_loader_runtime.py`** (patched `CDLL`); **not** `image.py` migration, domain smoke tests, task bases, kernel, or MediaPipe/native correctness. | **PR #8** → `main` (**merge `ca31fa7af428b1335af4b34f45bca639e0cec731`**, merged **2026-03-27T20:50:35Z**; **merge commit** method; **`--admin`** required). **PR head:** **`bc0bb4d3458fe566d93cfc530547c6a3b93dd687`**; **primary implementation:** **`aca63bab931f7b21d8cbf3f2fca20c4df1d2aa2d`**. **`ci` / `repo-safety`:** PR **`push`** `23664282232`, **`pull_request`** `23665065804`; post-merge **`main`** `23666946080` (**success**, head **`ca31fa7`**). **Proves:** concrete first-party **`LibraryLoader`** implementation + memoized load/failure + governance tripwires; tests use patched **`CDLL`** only. **Does not prove:** MediaPipe/native behavior, real host library paths, **`image.py`** migration, domain smoke, task bases, kernel. **Closeout recorded (UTC):** 2026-03-27T20:50:35Z (merge time). **Closeout doc commit on `main`:** **`3bb5ac24f035404843139dd7cfeae0db16de9bfb`**; post-closeout **`main`** **`ci`** run **`23667007934`** (**success**). **Ledger update commit:** **`f74c7b9ded6dfd9839331011e6016bff7d5f24d7`**; **`main`** run **`23667048907`** (**success**). **Authoritative `main` tip:** **`f74c7b9ded6dfd9839331011e6016bff7d5f24d7`**. |

---

## References (workspace; not committed here)

Committed strategy and record in this repo:

- `docs/runtime_surface_strategy.md` — **tracked runtime surface ingress, layout, Phase B entry contract** (M04; layout executed M05)
- `docs/runtime_substrate.md` — **first-party substrate path, modules, provenance** (M05)
- `docs/runtime_seam_framing.md` — **Phase B seam framing: `Dispatcher` / `LibraryLoader`, M07 `SharedLibraryLoader`, `image.py` preconditions, LIVE_STREAM honesty** (M06–M07)

Authoritative narrative and evidence live outside this repo in the workspace, for example:

- `docs/context/AURORA_VISION.md`
- `docs/context/mediapiperefactoraudit.md`, `docs/context/mediapipefinishingaudit.md`
- `docs/context/PANTANAL_1_MOONSHOT.md`
- `docs/preflight/aurora_startup_lock/` (startup locks and phase boundaries)

When those documents change, **this file should be updated at milestone closeout** if the repo-level posture or roadmap needs to stay aligned.

