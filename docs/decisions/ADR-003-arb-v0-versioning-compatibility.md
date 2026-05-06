# ADR-003 — ARB v0.1 versioning and compatibility

**Status:** Accepted  
**Date:** 2026-05-06  
**Milestone:** M36  
**Scope:** Documentation / governance

## Context

**ARB v0.1** is the current **public artifact contract** for deterministic, on-disk run bundles under [`../aurora_run_bundle_boundary.md`](../aurora_run_bundle_boundary.md) and [`../aurora_run_bundle_v0_spec.md`](../aurora_run_bundle_v0_spec.md). The `src/aurora/arb/` package implements **read**, **write**, **validate**, **hashing**, and the **validate-only CLI** (`python -m aurora.arb`) against that spec.

Consumers need a clear rule: **which version of the format** the published APIs target, and what happens if the format **changes**.

## Decision

1. **Current contract:** **ARB v0.1** (`arb_version`: `"0.1"`, **offline/batch** scope per spec) is the **only** normative version implemented and documented as the **public** artifact boundary in this repository today.
2. **Governed surfaces:** **`write_arb`**, **`read_arb`**, **`validate_arb`**, **canonical JSON**, **hashing**, and the **CLI** remain governed by **[`aurora_run_bundle_v0_spec.md`](../aurora_run_bundle_v0_spec.md)** and verified by the existing test suite — **not** by silent drift in docs or code.
3. **Breaking changes:** Any **breaking** on-disk layout, manifest schema, hash semantics, or validation rules requires an **explicit future versioning decision** (new `arb_version`, new spec document, milestone authorization, and migration narrative). **M36 does not** introduce a new version or breaking change.
4. **M36 scope:** This milestone adds **documentation only** — **no** behavior, schema, hash, CLI, or validation semantics changes.

## Consequences

- Downstream tooling may pin to **v0.1** semantics using the committed spec + exported APIs.
- Future **v0.2+** work is **not** implied by M36.

## Invariants

- Public API docs under [`../api/arb.md`](../api/arb.md) align with **`aurora.arb.__all__`** and v0.1 spec sections referenced in code.
- No milestone silently redefines **“v0.1”** without ledger and spec updates.

## Non-goals

- **Replay** orchestration, **transport** wrappers, **semantic bundle gates** beyond current **validate_arb**, or **training** / LIVE_STREAM profiles — deferred per [`../aurora.md`](../aurora.md).

## Verification

- `validate_arb` / `write_arb` / `read_arb` docstrings and tests remain consistent with §3–§7 of the v0.1 spec.
- Cross-check [`../api/arb.md`](../api/arb.md) and this ADR for **v0.1** wording.
