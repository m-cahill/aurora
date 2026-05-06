# ARB v0.1 performance baseline (M38)

This document describes **how** AURORA records **bounded, non-authoritative** timings for the **stdlib** **ARB v0.1** **public Python API** only.

## Scope

- **In scope:** [`aurora.arb`](api/arb.md) surfaces implemented under [`src/aurora/arb/`](../src/aurora/arb/) — **canonical JSON serialization** (`canonicalize`), **hash helpers** (`sha256_hex`, `compute_root_hash`), **`write_arb`**, **`read_arb`**, **`validate_arb`** — using a **deterministic synthetic** bundle shaped like the spec §8 illustration (see tests under [`tests/test_arb_writer.py`](../tests/test_arb_writer.py)).
- **Out of scope / explicit non-proofs:** These timings are **not** evidence of **native execution** performance, **audio decode** performance, **graph / TFLite** runtime performance, **MediaPipe application parity**, or **BirdCLEF / PANTANAL-1** inference performance. They do **not** define SLAs, regression gates, or production SLOs.

## Method

- **Implementation:** [`../scripts/measure_arb_performance.py`](../scripts/measure_arb_performance.py) (**stdlib** only; imports **public** [`aurora.arb`](../src/aurora/arb/__init__.py) APIs).
- **Timer:** `time.perf_counter_ns` per iteration.
- **Statistics:** For each named operation, the script collects `iterations × repeat` samples, reports **min**, **median** (rounded to nearest integer nanosecond), **p95** (nearest-rank on sorted samples), and **max**, and includes the raw **`samples_ns`** list in the JSON artifact.
- **Workloads:** **`write_arb`**, **`read_arb`**, and **`validate_arb`** use **`tempfile.TemporaryDirectory`** bundle roots (fresh tree per sample for **write**; **read** / **validate** time a bundle after an untimed **write** setup inside the same temporary workflow per sample).

## Interpretation

- Artifacts are **baseline evidence** for the **declared synthetic workload** on the **GitHub Actions** runner (or your host, if run locally). Numbers will **vary** by machine, filesystem, and load.
- **`non_sla`:** Always **`true`** in the JSON schema — consumers **must not** treat outputs as performance **contracts**.

## Commands

### Local (repository root)

After [`pip install -e .`](../DEVELOPMENT.md) (or with `PYTHONPATH=src`):

```bash
python scripts/measure_arb_performance.py \
  --iterations 50 \
  --repeat 5 \
  --output artifacts/arb_performance_baseline.json
```

Or:

```bash
make performance
```

### CI

The **`ci` / `repo-safety`** workflow runs the same script with **`PYTHONPATH=src`** and uploads **`artifacts/arb_performance_baseline.json`** as part of the existing **`artifacts/`** upload (see [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

**Authoritative** baseline JSON for releases should be taken from **clean CI artifacts**, not ad hoc local runs.

## Artifact

- **Path (CI / local):** `artifacts/arb_performance_baseline.json`
- **Schema id:** `schema_version` field (currently `m38.arb_performance.v1`).

## Canonical record

For project status, milestone ledger, and non-proofs, see **[`aurora.md`](aurora.md)**.
