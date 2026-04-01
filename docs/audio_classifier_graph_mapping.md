# Audio classifier graph mapping (Phase D — scope lock / evidence)

**Role:** Evidence-backed map of the **upstream** MediaPipe **Tasks** audio classifier path in the workspace **read-only** clone. This document **locks** the first explicit **post-M19** target for any future milestone that would wire first-party `AUDIO_*` dispatch to a real native / Tasks path. It is **descriptive planning**, not a proof of correctness, parity, or decode behavior in `aurora/`.

**Evidence basis:** Direct inspection of files under **`mediapipe/mediapipe/`** (relative to the workspace root). Paths below use that prefix. If your clone layout differs, resolve relative to the repository root of the MediaPipe tree.

**Canonical project record:** `docs/aurora.md` — execution phase boundaries and milestone ledger remain authoritative over any long-horizon roadmap table.

---

## 1. Scope and non-goals

### 1.1 In scope

- Name the **observed** Python → shared library → C → C++ → graph → calculator chain for **AudioClassifier**.
- Identify **dependency pressure points** (TFLite, metadata, tensor bridge, optional audio DSP externals).
- Separate **observed wiring** from **likely first native-wiring seam** and **proof obligations** for a future implementation milestone.

### 1.2 Explicit non-goals

- **No** claim that `aurora/` CI validates this graph, native execution, or model outputs.
- **No** instruction to copy upstream source into `aurora/`.
- **No** ARB, ORNITHOS, BirdCLEF harness, or competition-rail decisions.

---

## 2. End-to-end chain (observed)

### 2.1 Python Tasks API

| Step | Location | Role |
|------|----------|------|
| Public API | `mediapipe/mediapipe/tasks/python/audio/audio_classifier.py` | `AudioClassifier` loads the Tasks C API via `mediapipe.tasks.python.core.mediapipe_c_bindings.load_shared_library` with ctypes signatures for `MpAudioClassifierCreate`, `MpAudioClassifierClassify`, `MpAudioClassifierClassifyAsync`, `MpAudioClassifierCloseResult`, `MpAudioClassifierClose`. Uses `SerialDispatcher` for synchronous calls. |
| Running modes | Same file + `audio_task_running_mode` | AUDIO_CLIPS vs AUDIO_STREAM; stream mode uses async callback path. |

**Seam note:** This is the **Python ingress** that would eventually align with first-party `aurora.runtime` audio vocabulary (`AuroraAudio`, `AUDIO_*` tokens) **only if** a future milestone explicitly authorizes wiring — **not** implied by M19 or M20.

### 2.2 C API (exported boundary)

| Step | Location | Role |
|------|----------|------|
| C wrapper | `mediapipe/mediapipe/tasks/c/audio/audio_classifier/audio_classifier.cc` | `MpAudioClassifierCreate` builds `mediapipe::tasks::audio::audio_classifier::AudioClassifierOptions`, then `AudioClassifier::Create`. `MpAudioClassifierClassify` converts `MpAudioData` to `mediapipe::Matrix` (`CppConvertToMatrix`) and calls `AudioClassifier::Classify`. |

### 2.3 C++ task object and graph packaging

| Step | Location | Role |
|------|----------|------|
| Factory | `mediapipe/mediapipe/tasks/cc/audio/audio_classifier/audio_classifier.cc` | `AudioClassifier::Create` calls `core::AudioTaskApiFactory::Create` with `CreateGraphConfig`, which builds a **single-node** graph whose calculator/subgraph type is `mediapipe.tasks.audio.audio_classifier.AudioClassifierGraph` (`kSubgraphTypeName`). Streams: `AUDIO`, optional `SAMPLE_RATE`; outputs `CLASSIFICATIONS` and/or `TIMESTAMPED_CLASSIFICATIONS`. |
| Clip vs stream | Same | `Classify` sends matrix + sample rate packets; `ClassifyAsync` sends timestamped audio stream packets. |

### 2.4 Task graph (`AudioClassifierGraph`)

| Step | Location | Role |
|------|----------|------|
| Graph builder | `mediapipe/mediapipe/tasks/cc/audio/audio_classifier/audio_classifier_graph.cc` | `AudioClassifierGraph::GetConfig` builds preprocessing specs from **TFLite model + metadata** (`BuildPreprocessingSpecs`), configures **`AudioToTensorCalculator`** (`ConfigureAudioToTensorCalculator`), connects **`AUDIO`** and optional **`SAMPLE_RATE`** (or default sample rate via `ConstantSidePacketCalculator` + `SidePacketToStreamCalculator`), then **`AddInference`** → **`ClassificationPostprocessingGraph`**. |
| Post-processing | Same | Tensors from inference feed `ClassificationPostprocessingGraph`; timestamps connect in non-stream mode for vector-of-results path. |

**Observed graph shape (high level):**

```text
Matrix AUDIO [+ SAMPLE_RATE] → AudioToTensorCalculator → TENSORS → Inference → ClassificationPostprocessingGraph → CLASSIFICATIONS / TIMESTAMPED_CLASSIFICATIONS
```

---

## 3. Calculators and dependencies (pressure points)

### 3.1 `AudioToTensorCalculator` (in-graph, central)

- **Registered node:** `"AudioToTensorCalculator"` in `audio_classifier_graph.cc`.
- **Source:** `mediapipe/mediapipe/calculators/tensor/audio_to_tensor_calculator.cc` (and headers/proto).
- **Role (from file header comment):** Resampling, buffering, framing (including overlap), optional FFT — outputs **MediaPipe tensors** for inference. **Streaming vs non-streaming** behavior is controlled by options (`stream_mode` / task `use_stream_mode`).
- **External pressure (includes):** `audio/dsp/resampler_q.h`, `audio/dsp/window_functions.h` (**`@com_google_audio_tools`**), `pffft`, TensorFlow Lite C API — i.e. **DSP + tensor + inference boundary** in one calculator.

### 3.2 `time_series_framer_calculator` (BUILD only in this path)

- **`audio_classifier_graph` BUILD** lists `//mediapipe/calculators/audio:time_series_framer_calculator` as a **direct dependency** of target `audio_classifier_graph` (`mediapipe/mediapipe/tasks/cc/audio/audio_classifier/BUILD`).
- **`audio_classifier_graph.cc` does not** add a `TimeSeriesFramer` (or similarly named) node; framing for this task graph is handled **inside** `AudioToTensorCalculator` per that calculator’s documented behavior.

**M20 finding:** Treat **`time_series_framer_calculator`** as a **build/linkage** dependency for the graph target in this tree, **not** as a separate node in the **`AudioClassifierGraph` composition** in the inspected `.cc` file. Other graphs may use `TimeSeriesFramer` explicitly; this task graph does **not** (in the inspected source).

### 3.3 Inference and TFLite

- **`AddInference`** (from `mediapipe/tasks/cc/core/model_task_graph.h` pattern) wires **TFLite** inference for the loaded model.
- **Metadata:** `audio_classifier_graph.cc` requires TFLite model metadata for audio tensor specs (`BuildPreprocessingSpecs`); missing metadata is an error path.

### 3.4 Post-processing

- **Subgraph:** `mediapipe.tasks.components.processors.ClassificationPostprocessingGraph` — consumes inference tensors and emits classification protos/results.

---

## 4. Likely first native-wiring seam (for a future milestone)

This section is **planning judgment**, not upstream API commitment.

| Seam | Why it matters |
|------|----------------|
| **C API / shared library** | Python `audio_classifier.py` and C `MpAudioClassifier*` already define a **stable exported** boundary for task creation and classify paths. |
| **Matrix + sample rate → graph** | C++ `AudioClassifier::Classify` / `ClassifyAsync` already package `Matrix` and sample rate into the task runner; aligning **first-party** `AuroraAudio` / dispatcher behavior to this shape is a plausible **narrow** target — still **out of scope** until a milestone authorizes it. |
| **`AudioClassifierGraph` internals** | Touching **`AudioToTensorCalculator`** or inference implies **TFLite + metadata + `@com_google_audio_tools`** — **high** blast radius; not a default first wiring step without explicit scope. |

---

## 5. Proof obligations vs non-goals (future D1-style milestone)

**If** a milestone wires `AUDIO_*` to a real Tasks/native path, it should define explicitly:

| Category | Proof / obligation |
|----------|-------------------|
| **Behavior class** | Governance-only vs behavior-preserving vs intentional behavior change. |
| **Verification** | Appropriate tests or artifacts for the **declared** seam — not “green CI” as proxy for model correctness. |
| **Non-goals** | No blanket claim of MediaPipe parity, decode correctness, or full graph certification from `aurora/` repo checks alone. |

**M20 does not** satisfy D1; it **documents** the upstream chain so D1 can be scoped without monolithic Phase D expansion.

---

## 6. References (in-repo)

- `docs/acoustic_kernel_surface_inventory.md` — broader calculator inventory and `@com_google_audio_tools` map.
- `docs/kernel_ingress_strategy.md` — Phase D ingress rules and proof bars.
- `docs/aurora.md` — milestone ledger and Phase D constraints.

---

## 7. Revision note

**Inspected layout:** Workspace MediaPipe sources under **`mediapipe/mediapipe/`**. Inventory documents that predate this mapping may refer to paths without the leading duplicate `mediapipe/` segment; both refer to the **same** clone content.
