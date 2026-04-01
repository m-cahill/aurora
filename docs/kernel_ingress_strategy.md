# Kernel ingress strategy (Phase D entry)

**Role:** Bounded framing for how **acoustic kernel** work may **enter** the tracked `aurora/` repository after **Phase C** closeout (**M16**). This document is **planning and contract** for ingress; it is **not** an implementation spec, extraction design, or claim of kernel behavior.

**Canonical project record:** `docs/aurora.md` — execution phases, milestone ledger, and Phase D constraints.

---

## 1. What “kernel ingress” means here

**Kernel ingress** is the **controlled, milestone-gated** introduction of **documentation, seams, and (later) code** that move the repo toward a **governed acoustic kernel** — without monolithic rewrites, without implying MediaPipe parity, and without bypassing the locked phase sequence in `docs/aurora.md`.

For **M17** specifically, ingress is **docs-only**: naming the problem space, candidate surfaces, non-goals, and proof bars for **future** implementation milestones. No new runtime modules are required to satisfy ingress at this milestone.

---

## 2. Candidate ingress surfaces (not commitments)

These are **plausible** places future Phase D work could attach; they are **not** approved scopes until a later milestone locks them.

| Surface | Role |
|--------|------|
| **`docs/`** in this repo | Strategy, boundaries, and references that keep extraction incremental and auditable. |
| **First-party `src/aurora/`** | Bounded modules that compose with existing **`Dispatcher` / `LibraryLoader`** seams — **M19** authorizes **`AuroraAudio`** (Candidate A) only; further modules remain milestone-gated. |
| **Verifier / CI** | Future gates that match an agreed extraction seam — **not** changed in planning-only milestones unless the milestone says so. |
| **Workspace `mediapipe/`** (read-only) | Study and evidence only; **no** copy of upstream source into `aurora/`. |

---

## 3. Explicit non-goals (Phase D entry / M17)

- **No** acoustic kernel implementation, C++/Python packaging of calculators, or “lift” of MediaPipe audio graphs in **M17**.
- **No** `VisionTaskBase` / `AudioTaskBase` without a **second** repeated task-shaped surface in-repo (per prior phase posture).
- **No** ARB specification, ORNITHOS work, or BirdCLEF harness structure decisions beyond **protecting** the parallel competition rail.
- **No** claims of **native correctness**, **decode correctness**, or **MediaPipe** application parity from CI green alone.
- **No** change to workflow identity, coverage thresholds, or enforcement semantics unless a milestone explicitly requires it.

---

## 4. Proof required for later implementation milestones

A future milestone that **implements** kernel-related code should define, at minimum:

- **Behavior class:** governance-only vs behavior-preserving vs intentional behavior change.
- **Verification:** tests, artifacts, or smoke appropriate to the seam — aligned with `DEVELOPMENT.md` *what CI proves / does not prove*.
- **Rollback:** how to revert or narrow the change if the seam proves wrong.
- **Blast radius:** which directories and contracts are touched; no accidental expansion into “whole graph” or monolithic extraction.

Until those are locked, **Phase D** remains **planning / ingress / scoping** — not blanket implementation authorization.

---

## 5. Competition rail (BirdCLEF) — non-interference

Refactor and Phase D planning **must not** remove the ability to pursue a **credible BirdCLEF submission path** as a **parallel** concern (see `docs/aurora.md` — protected competition rail). Kernel ingress framing **does not** fix baseline location, harness, or repo layout for that rail; it **must not** block or contradict future baseline work.

---

## 6. Relationship to other docs

- **`docs/aurora.md`** — authoritative phase state, milestone ledger, Phase D entry constraints.
- **`DEVELOPMENT.md`** — what the **current** first-party seam proves and explicitly does not prove.
- **Workspace vision / audits** — context only; not committed here unless copied in a doc milestone.

When Phase D implementation milestones begin, **this file** should be updated at closeout so ingress narrative stays aligned with what actually landed.

---

## 7. M19 (first bounded implementation slice)

**M19** is authorized **only** for **Candidate A** in **`docs/acoustic_kernel_surface_inventory.md`** §5: a **bounded Python-first audio seam** (**`AuroraAudio`**, shared **`dispatch_tokens`**, **`audio_dispatch.py`**) with **structural** tests — **not** C++ calculators, BUILD/graph work, TFLite decoupling, or MediaPipe code copy. Proof bar: behavior class (**additive seam**), verification (unittest fakes + composed smoke; **`verify_repo_state.py`** seam list), rollback (revert M19 commits), blast radius (**`src/aurora/runtime/`** + tests + docs — no `mediapipe/`).
