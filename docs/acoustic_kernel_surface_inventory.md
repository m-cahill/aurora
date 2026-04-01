# Acoustic kernel surface inventory (Phase D — planning / ingress / scoping)

**Role:** Evidence-backed inventory of **acoustic-kernel-relevant** surfaces in the workspace **read-only** `mediapipe/` clone, aligned with the **Python + C++** audio path as the active AURORA study surface. This document **names** ingress candidates and a **recommended first implementation slice for M19**; it is **not** kernel implementation, extraction design, or a claim of MediaPipe, native, or decode correctness.

**Canonical project record:** `aurora.md` — Phase D remains **planning / ingress / scoping** until a milestone explicitly authorizes implementation beyond that scope.

**Evidence basis:** File paths and `BUILD` dependency edges are taken from the workspace `mediapipe/` tree at inventory time (read-only inspection). Paths use forward slashes for portability.

---

## 1. Scope and non-scope

### 1.1 In scope (this inventory)

- **Python Tasks audio bindings** — `mediapipe/tasks/python/audio/` (classifier API, running modes, record helpers).
- **C++ Tasks audio surface** — `mediapipe/tasks/cc/audio/` (classifier graph, core task API factory, tensor specs).
- **Core DSP calculators** — `mediapipe/calculators/audio/` (time-series, spectrogram, MFCC/Mel, resampling, FIR, decode, log stabilization).
- **Tensor-bridge calculators** — `mediapipe/calculators/tensor/` targets `audio_to_tensor_calculator` and `tensors_to_audio_calculator` (audio ↔ tensor ↔ TFLite boundary).
- **External build constraints** — `@com_google_audio_tools` exposure per surface (see §5), plus **TFLite** coupling where the graph build pulls inference.

### 1.2 Adjacent surfaces (acknowledged, not inventoried)

These exist in upstream MediaPipe and matter for product completeness; they are **not** the M18 inventory target:

- **Web / iOS / Java / C** Tasks audio bindings and platform-specific graphs under `mediapipe/tasks/web/audio/`, `mediapipe/tasks/ios/audio/`, `mediapipe/tasks/java/.../tasks/audio/`, `mediapipe/tasks/c/audio/`, etc.

**Substance:** Other platform bindings are **out of scope** for this document. M18 focuses on the **Python → native Tasks / graph → C++ calculators** path because that path aligns with the current **AURORA** repo posture (first-party Python runtime under `src/aurora/`, Phase A–C delivery) and with **M17** framing (ingress attaches to bounded first-party seams; workspace `mediapipe/` is **evidence only**).

### 1.3 Explicit non-goals (consistent with `kernel_ingress_strategy.md`)

- **No** claim of parity with upstream Tasks behavior, **no** decode correctness proof, **no** assertion that CI in `aurora/` validates MediaPipe graphs.
- **No** ARB, ORNITHOS, BirdCLEF harness, or competition-rail layout decisions.
- **No** instruction to copy upstream source into `aurora/` — architectural learning only.

---

## 2. Functional-group inventory (top level)

### 2.1 Python task / binding path

| Group | Location (workspace `mediapipe/`) | Role |
|--------|-----------------------------------|------|
| **Tasks Python audio** | `mediapipe/tasks/python/audio/` | Public Python API surface for audio tasks (e.g. classifier), `core/audio_record.py`, `core/audio_task_running_mode.py`, package `BUILD`. This is the **Python ingress** that would eventually align with first-party `aurora.runtime` seams if a milestone authorizes it. |

**Ingress note:** Phase A–C normalized **image** dispatch (`AuroraImage`, tokens, `image_dispatch.py`). **M19** adds the parallel bounded **audio** seam (`AuroraAudio`, `audio_dispatch.py`, `AUDIO_*` tokens in `dispatch_tokens.py`) — **structural** first-party vocabulary only; **not** kernel extraction or upstream parity (see **`DEVELOPMENT.md`**).

### 2.2 C++ task-layer audio surface

| Group | Location | Role |
|--------|----------|------|
| **Audio classifier** | `mediapipe/tasks/cc/audio/audio_classifier/` | `audio_classifier.cc` / `.h`, **`audio_classifier_graph.cc`** — composes **framer**, **`audio_to_tensor`**, **TFLite inference**, post-processing. |
| **Core task API** | `mediapipe/tasks/cc/audio/core/` | `base_audio_task_api.h`, `audio_task_api_factory.h`, `running_mode.h` — shared Tasks audio API patterns. |
| **Utils** | `mediapipe/tasks/cc/audio/utils/` | `audio_tensor_specs` — tensor layout / specs for audio tasks. |

**Ingress note:** The **audio_classifier_graph** is the **narrowest** end-to-end **Tasks** graph that exercises the **Python+C++** audio path with **real** model inference — and therefore pulls **TFLite** and **inference_calculator** dependencies immediately (see §5).

### 2.3 Core DSP calculators (`calculators/audio/`)

| Group | Role |
|--------|------|
| **Framing / windows** | `time_series_framer_calculator` — segments time series; uses `@com_google_audio_tools//audio/dsp:window_functions`. |
| **Spectral / MFCC** | `spectrogram_calculator`, `mfcc_mel_calculators` — spectral features; **strong** `@com_google_audio_tools` usage (spectrogram stack, MFCC). |
| **Resampling** | `rational_factor_resample_calculator`, `resample_time_series_calculator` — resampler / `resampler_q` from audio_tools. |
| **Filtering / log** | `two_tap_fir_filter_calculator`, `stabilized_log_calculator` — FIR from audio_tools; stabilized log is **MediaPipe-local** proto/deps (no `com_google_audio_tools` on the library target). |
| **Primitives** | `basic_time_series_calculators` — Eigen/time-series utilities; **no** `com_google_audio_tools` on the `cc_library` target. |
| **Decode** | `audio_decoder_calculator` — depends on `//mediapipe/util:audio_decoder` (not `@com_google_audio_tools` on the calculator target). |

**Ingress note:** Calculators are **modular** (audit truth) but **Bazel**- and **dependency**-entangled as soon as DSP is touched.

### 2.4 Tensor-bridge calculators

| Group | Location | Role |
|--------|----------|------|
| **Audio → tensor** | `mediapipe/calculators/tensor/audio_to_tensor_calculator` | Bridges time-series/matrix inputs to **TFLite**-oriented tensors; deps include **`@com_google_audio_tools//audio/dsp:resampler_q`**, **`window_functions`**, **`@org_tensorflow//tensorflow/lite/c:common`**, **`@pffft`**. |
| **Tensor → audio** | `mediapipe/calculators/tensor/tensors_to_audio_calculator` | Inverse bridge; **`window_functions`**, **`@pffft`**. |

**Ingress note:** These are the **direct** coupling between **audio DSP** and the **Tasks inference** path used by **`audio_classifier_graph`**.

### 2.5 External dependencies and build constraints

| Constraint | Implication for ingress |
|------------|-------------------------|
| **`@com_google_audio_tools`** | Declared in upstream `WORKSPACE`; calculator `BUILD` files pull **dsp/** targets (mfcc, spectrogram, resampler, window_functions, two_tap_fir, etc.). Any extraction or build that touches these calculators must **account for this repo explicitly** (`aurora.md` — audit-established truth). |
| **TFLite** | Embedded in graph/task build macros (`cc_library_with_tflite`, inference calculators). **Do not** treat early milestones as decoupling the whole graph from TFLite (`runtime_surface_strategy.md`, vision doc). |
| **No copy rule** | `aurora/` must not import MediaPipe source from `mediapipe/`; learning and dependency naming are allowed; **code transfer is not**. |

### 2.6 Non-goals and protected boundaries

| Boundary | Rule |
|----------|------|
| **Phase D** | Remains **planning / ingress / scoping** until explicitly locked; this document **does not** authorize monolithic kernel extraction. |
| **Competition rail** | BirdCLEF / baseline path stays **parallel** and **protected** — refactor milestones must not block a credible submission path (`aurora.md`). |
| **Proof bar** | Future implementation milestones must state behavior class, verification, rollback, and blast radius (`kernel_ingress_strategy.md` §4). |

---

## 3. `@com_google_audio_tools` dependency map (M19 decision level)

This is a **specific** map of **direct** `BUILD` edges — **not** a full transitive closure. It is enough to distinguish **low** vs **high** external-DSP burden and **TFLite** coupling.

### 3.1 Per-calculator / per-target (upstream `cc_library` deps)

| Surface | Key `@com_google_audio_tools` labels (direct) | Other notable deps |
|---------|-----------------------------------------------|----------------------|
| `mfcc_mel_calculators` | `//audio/dsp/mfcc` | Framework, Eigen |
| `rational_factor_resample_calculator` | `//audio/dsp:resampler`, `:resampler_q` | Framework, Eigen |
| `resample_time_series_calculator` | `:resampler_q` | Framework, Eigen |
| `spectrogram_calculator` | `//audio/dsp:window_functions`, `//audio/dsp/spectrogram` | Framework, Eigen |
| `time_series_framer_calculator` | `:window_functions` | Framework, Eigen |
| `two_tap_fir_filter_calculator` | `//audio/linear_filters:two_tap_fir_filter` | Framework, Eigen |
| `stabilized_log_calculator` | *(none on library target)* | Framework |
| `basic_time_series_calculators` | *(none on library target)* | Eigen, time_series_util |
| `audio_decoder_calculator` | *(none on library target)* | `//mediapipe/util:audio_decoder` |
| `audio_to_tensor_calculator` | `:resampler_q`, `:window_functions` | TFLite C API, `pffft`, tensor formats |
| `tensors_to_audio_calculator` | `:window_functions` | `pffft`, tensor formats |

### 3.2 Tasks graph bundle (representative)

| Surface | Composition note | TFLite / inference |
|---------|------------------|---------------------|
| `audio_classifier_graph` | Depends on `time_series_framer_calculator`, `audio_to_tensor_calculator`, `inference_calculator_cpu`, constant/side-packet calculators | **Yes** — immediate TFLite + model resources path |

---

## 4. Appendix A — Per-calculator rows (where detail matters for M19)

Rows are included **only** where individual calculators change **ingress risk**, **dependency handling**, or **proof obligations**.

| Calculator / target | Ingress relevance | `@com_google_audio_tools` | Notes |
|---------------------|-------------------|----------------------------|--------|
| `time_series_framer_calculator` | **Framing** entry point for many graphs; lower MFCC/spectrogram surface area than full spectral stack | `window_functions` | Used directly by **`audio_classifier_graph`**. |
| `audio_to_tensor_calculator` | **Bridge** to TFLite tensors; combines DSP + **inference** concerns | `resampler_q`, `window_functions` | **High** coupling: TFLite + audio_tools + `pffft`. |
| `spectrogram_calculator` | Standalone spectral front-end | `window_functions`, `spectrogram` | Strong DSP story; not required to be “first” unless graph demands it. |
| `mfcc_mel_calculators` | Classic ASR-style features | `mfcc` | Distinct from spectrogram-only path; own proto options. |
| `rational_factor_resample_calculator` / `resample_time_series_calculator` | Rate conversion | `resampler`, `resampler_q` | Overlap in resampler_q between targets — dependency clustering for any extraction. |
| `two_tap_fir_filter_calculator` | Simple FIR path | `two_tap_fir_filter` | Smaller than full spectrogram stack but still audio_tools. |
| `stabilized_log_calculator` | Log stabilization in feature pipelines | None on cc_library | Lower external DSP burden; still graph-integrated. |
| `basic_time_series_calculators` | Time-series primitives | None on cc_library | Useful building block; no audio_tools on this target. |
| `audio_decoder_calculator` | File/container decode into time series | None on cc_library; uses `mediapipe/util:audio_decoder` | **Decode** semantics are a separate proof obligation from MFCC/spectrogram. |
| `tensors_to_audio_calculator` | Inverse of audio→tensor | `window_functions` | Pairs with `audio_to_tensor` in tests; reconstruction / round-trip concerns if ever proven. |

---

## 5. Appendix B — M19 implementation slice candidates (ranked)

This section **recommends** a single **first** slice for **M19** and lists **alternatives**. It is **planning only** — not implementation authorization. Any M19 work must still be classified, tested, and scoped per `kernel_ingress_strategy.md` and `DEVELOPMENT.md`.

### Candidate A — **recommended** (lowest extrinsic dependency, aligns with existing seams)

**Slice:** **Bounded first-party Python audio seam** in `aurora/` — parallel in *shape* to the existing **`Dispatcher` / `LibraryLoader` / `AuroraImage`** pattern: e.g. **audio dispatch tokens**, **dispatch helper module**, and **tests with fakes** only (no MediaPipe imports under `src/aurora/`, no new claims of native correctness).

**Rationale:**

- **Zero** `@com_google_audio_tools` or TFLite exposure inside `aurora/` until a later milestone explicitly brings calculator or graph code paths into scope.
- Extends the **proven** Phase B–C seam discipline (M06–M15) into the **audio vocabulary** without touching upstream `mediapipe/` or C++ extraction.
- **Reversible** and **small blast radius** — consistent with Phase D **non-monolithic** rule.

**Proof obligations (for a future M19 spec):** Behavior class (likely **governance / structural**); unittest fakes; `verify_repo_state` / CI alignment; explicit **does not prove** list (no decode, no Tasks parity, no kernel DSP).

---

### Candidate B — viable but **higher** dependency / risk

**Slice:** **Documentation + structural mapping** of the **`audio_classifier_graph`** wiring (Python entry → C++ graph → `time_series_framer` + `audio_to_tensor` + inference) with **no** or **minimal** code — *or* a **read-only** analysis artifact checked in (e.g. generated graph dependency list from `BUILD`).

**Rationale:** Clarifies the **real** end-to-end path for future work.

**Risk:** Easy to slide into **implicit** commitment to TFLite/inference proof bars; must keep claims **descriptive** only.

**Proof obligations:** Doc-only or generator script under `scripts/` with tests — **not** native execution proof.

---

### Candidate C — **deferred / not first-wave**

**Slice:** **C++ calculator-level** work (any of `calculators/audio/*` or tensor-bridge calculators) or **direct** integration with **`audio_classifier`** inference graphs.

**Rationale:** Immediately engages **`@com_google_audio_tools`**, **TFLite**, and **Bazel** coupling; contradicts **smallest safe** slice unless a milestone explicitly expands scope.

**Proof obligations:** Native build, graph correctness, model inference — **beyond** current `aurora/` CI posture.

---

## 6. Handoff summary

| Item | Content |
|------|---------|
| **Inventory focus** | Python + C++ audio path; other platforms **acknowledged only**. |
| **Dependency map** | §3 — direct `@com_google_audio_tools` edges per calculator/target; §3.2 for Tasks graph. |
| **Recommended M19 slice** | **Candidate A** — bounded **Python-first** audio seam (tokens + dispatch contract + fake tests), **no** upstream code copy. |
| **Alternatives** | Candidate B (graph/documentation stress), Candidate C (calculator/C++ — deferred). |

---

## 7. References (in-repo)

- `aurora.md` — phase state, milestone ledger, Phase D constraints.
- `kernel_ingress_strategy.md` — Phase D entry framing.
- `runtime_surface_strategy.md` — ingress rules, TFLite / audio_tools constraints.
- `../DEVELOPMENT.md` — what current CI proves and does not prove.
