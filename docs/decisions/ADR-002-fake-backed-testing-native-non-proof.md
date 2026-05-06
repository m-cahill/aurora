# ADR-002 — Fake-backed testing and native non-proof

**Status:** Accepted  
**Date:** 2026-05-06  
**Milestone:** M36  
**Scope:** Documentation / governance

## Context

AURORA’s CI (`ci` / `repo-safety`) exercises **first-party** Python with **structural** tests: patched `ctypes`, fake dispatchers, and filesystem-backed ARB fixtures. That bar is **honest** for what it checks — but it is **easy to misread** as evidence of real native stacks, decode correctness, or application-level parity with MediaPipe.

The committed project record (`docs/aurora.md`) already binds **explicit non-proofs**; this ADR locks that interpretation as an **architectural decision**, not an accident.

## Decision

1. **Intentional seam testing:** **Fake-backed** and **structural** tests are the **deliberate** default for `src/aurora/` in CI: they prove **wiring shape**, error paths, and **governance** constraints — not a real Tasks shared library on the runner.
2. **What CI does *not* prove:**
   - **Real native library execution** on GitHub-hosted runners (or any host).
   - **Decode correctness** (audio bytes → validated samples for real codecs).
   - **Graph / TFLite correctness** or end-to-end graph behavior.
   - **MediaPipe application parity** or benchmark/competition readiness.
3. **Safety boundary:** Structural proof is **not** a hidden claim of native correctness. Green CI **must not** be read as overriding the non-proofs in [`../aurora.md`](../aurora.md).
4. **Future native proof:** Any milestone that aims to prove **real** native execution, decode, graph correctness, or parity must be **separately scoped**, **explicitly authorized**, and **documented** with its own evidence bar — it is **out of band** for the default M31+ maintenance posture.

## Consequences

- Downstream consumers should assume **handoff surfaces are contractual APIs + tests**, not **environment-specific native certification**.
- Releases and audits should separate **“structural coverage / honest CI”** from **“native correctness.”**

## Invariants

- This ADR is **documentation-only**; it does not weaken or change tests or workflows by itself.
- Language in ADRs and API docs must remain **aligned** with [`../aurora.md`](../aurora.md) non-proofs.

## Non-goals

- Demanding **integration tests** against real native MediaPipe artifacts inside `aurora/` **by default**.
- Implying that **optional** local-native attempts (documented elsewhere) are **required** for Phase D closure — the committed record permits **“not attempted”** with honest disclosure.

## Verification

- [`../api/README.md`](../api/README.md) and runtime API pages state structural / non-proof posture plainly.
- `DEVELOPMENT.md` and [`../aurora.md`](../aurora.md) remain the authoritative **what CI proves** references.
