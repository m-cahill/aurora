# Public API reference (hand-curated)

This directory holds **human-maintained** Markdown describing the **contractual public handoff** for Python consumers. **M36** deliberately does **not** add Sphinx, MkDocs, pdoc, or other generated-doc tooling — see [`../decisions/ADR-001-stdlib-runtime-boundary.md`](../decisions/ADR-001-stdlib-runtime-boundary.md).

## Scope

| Document | Package / surface |
|----------|-------------------|
| [`runtime.md`](runtime.md) | **`aurora.runtime`** |
| [`arb.md`](arb.md) | **`aurora.arb`** |

## Rule: `__all__` is the public contract

Names documented in **`runtime.md`** and **`arb.md`** are exactly those exported via **`aurora.runtime.__all__`** and **`aurora.arb.__all__`** (see `src/aurora/runtime/__init__.py` and `src/aurora/arb/__init__.py`).

- **Internal modules** (`dispatch_tokens`, `image_dispatch`, `audio_dispatch`, `native_audio_dispatcher`, ARB submodules, …) may change layout without a semver promise unless promoted into **`__all__`**.
- **Undocumented names** are **not** supported API — use at your own risk.

## Architecture decisions (ADRs)

Decisions behind boundaries and non-proofs:

| ADR | Topic |
|-----|--------|
| [`../decisions/ADR-001-stdlib-runtime-boundary.md`](../decisions/ADR-001-stdlib-runtime-boundary.md) | Stdlib **runtime** vs dev/CI tooling |
| [`../decisions/ADR-002-fake-backed-testing-native-non-proof.md`](../decisions/ADR-002-fake-backed-testing-native-non-proof.md) | Structural CI vs native proof |
| [`../decisions/ADR-003-arb-v0-versioning-compatibility.md`](../decisions/ADR-003-arb-v0-versioning-compatibility.md) | ARB **v0.1** compatibility |
| [`../decisions/ADR-004-downstream-dependency-direction.md`](../decisions/ADR-004-downstream-dependency-direction.md) | One-way downstream direction |

## Normative ARB spec (on-disk)

- [`../aurora_run_bundle_boundary.md`](../aurora_run_bundle_boundary.md) — artifact boundary framing  
- [`../aurora_run_bundle_v0_spec.md`](../aurora_run_bundle_v0_spec.md) — **v0.1** on-disk format, hashing, CLI contract  

Also linked from the canonical record [`../aurora.md`](../aurora.md).

## Explicit non-proofs

Documentation and **green `ci` / `repo-safety`** do **not** establish:

1. **Native execution** of a real Tasks / MediaPipe shared library on CI or your machine  
2. **Decode correctness** (audio bytes → validated samples for real codecs)  
3. **Graph / TFLite correctness**  
4. **MediaPipe application parity** or competition readiness  
5. **BirdCLEF / PANTANAL-1** submission harness, Kaggle-only packaging, or downstream repo implementation inside `aurora/`  

For the project-level charter, see **Downstream must not assume** in [`../aurora.md`](../aurora.md).
