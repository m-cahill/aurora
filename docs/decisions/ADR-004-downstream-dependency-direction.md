# ADR-004 — Downstream dependency direction

**Status:** Accepted  
**Date:** 2026-05-06  
**Milestone:** M36  
**Scope:** Documentation / governance

## Context

AURORA is the **open-core** governed runtime and ARB substrate. **ORNITHOS** (model stack) and **PANTANAL-1** (BirdCLEF-facing deployment narrative) are **conceptually downstream**. Without an explicit rule, competition-specific or private code can create **reverse pressure** on the runtime repo.

[`../aurora.md`](../aurora.md) already documents **one-way** dependency direction; this ADR captures the decision for ADR consumers.

## Decision

1. **Role split:** **AURORA** (`aurora/`) owns the **generic** governed runtime seams, honest CI, and **public** ARB v0.1 **stdlib** implementation. **ORNITHOS** and **PANTANAL-1** are **downstream** (present or future repos) — **not** dependencies of the runtime package.
2. **Dependency direction:** **One-way:** downstream projects **may** depend on **released AURORA** surfaces and artifacts. **AURORA must not** depend on **ORNITHOS**, **PANTANAL-1**, **private** product code, or **competition-only** packages.
3. **Competition logic:** **BirdCLEF / Kaggle-only** notebooks, submission packaging, species-only tuning, and benchmark orchestration **belong downstream** unless a change also improves **generic** governed runtime surfaces under an **explicit** milestone authorization.
4. **No hidden coupling:** Private or downstream implementation must **not** introduce **reverse imports** or “temporary” coupling that **pulls model/competition concerns** back into `aurora/`.

## Consequences

- Release consumers get a **stable** boundary: compatibility discussions start at **published AURORA APIs + ARB v0.1**, not at downstream monorepo shapes.
- Ecosystem planning in [`../aurora.md`](../aurora.md) remains **charter**, not proof that sibling repos exist.

## Invariants

- `src/aurora/` **must not** add imports or packaging dependencies on downstream or **competition-only** code paths.
- Documentation must **not** imply ORNITHOS/PANTANAL-1 repos exist unless separately evidenced.

## Non-goals

- **Creating** ORNITHOS or PANTANAL-1 **repositories** or **scaffolds** inside **M36**.
- Choosing **license** or **release channel** details for downstream repos (handled in their own milestones).

## Verification

- Grep / packaging review on **future** milestones if dependency direction is challenged; M36 is docs-only.
- Align wording with **Proposed downstream repo layout and dependency directionality** in [`../aurora.md`](../aurora.md).
