#!/usr/bin/env python3
"""Bounded ARB v0.1 performance baseline (stdlib only; evidence — not a gate).

Measures public ``aurora.arb`` surfaces using deterministic synthetic inputs.
Output is baseline evidence only (``non_sla``); exit codes reflect script errors only.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable

# Editable-install / CI convention: package importable as ``aurora``.
from aurora.arb import (
    canonicalize,
    compute_root_hash,
    read_arb,
    sha256_hex,
    validate_arb,
    write_arb,
)

SCHEMA_VERSION = "m38.arb_performance.v1"

# Spec §8–style deterministic fixture (same field values as tests ``test_arb_writer``).
_FIX_MANIFEST: dict[str, str] = {
    "arb_version": "0.1",
    "bundle_id": "example-arb-0001",
    "created_utc": "2026-04-02T12:00:00Z",
    "graph_spec_path": "graph.yaml",
    "hash_manifest_path": "hashes/sha256_manifest.json",
    "input_manifest_path": "inputs/audio_index.json",
    "root_hash_path": "hashes/root_hash.txt",
    "runtime_mode": "offline_batch",
}

_FIX_GRAPH_YAML = """# Example graph stub — content is hashed as raw bytes in v0.1
version: 0
pipeline: audio_classifier_stub
"""

_FIX_INPUTS: dict[str, object] = {
    "entries": [
        {
            "duration_ms": "5000",
            "path": "inputs/example.wav",
            "sample_rate_hz": "16000",
        }
    ]
}

_FIX_SEGMENTS: dict[str, object] = {
    "segments": [
        {
            "end_ms": "5000",
            "id": "seg-001",
            "input_path": "inputs/example.wav",
            "start_ms": "0",
        }
    ]
}

_FIX_PREDICTIONS: dict[str, object] = {
    "predictions": [
        {
            "label": "species_a",
            "score": "0.91",
            "segment_id": "seg-001",
        }
    ]
}

_SMALL_PAYLOAD = b"aurora-m38-arb-baseline-payload"


def _percentile_95_sorted(sorted_ns: list[int]) -> int:
    n = len(sorted_ns)
    if n == 0:
        return 0
    idx = int(math.ceil(0.95 * n)) - 1
    return sorted_ns[max(0, min(idx, n - 1))]


def _run_timed(
    iterations: int,
    repeat: int,
    fn: Callable[[], object],
) -> list[int]:
    samples: list[int] = []
    for _ in range(repeat):
        for _i in range(iterations):
            t0 = time.perf_counter_ns()
            fn()
            t1 = time.perf_counter_ns()
            samples.append(t1 - t0)
    return samples


def _summarize(name: str, samples_ns: list[int]) -> dict[str, Any]:
    sorted_ns = sorted(samples_ns)
    return {
        "name": name,
        "min_ns": sorted_ns[0] if sorted_ns else 0,
        "median_ns": int(round(statistics.median(samples_ns))) if samples_ns else 0,
        "p95_ns": _percentile_95_sorted(sorted_ns),
        "max_ns": sorted_ns[-1] if sorted_ns else 0,
        "samples_ns": samples_ns,
    }


def _measure_all(iterations: int, repeat: int) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []

    manifest_obj: dict[str, str] = dict(_FIX_MANIFEST)
    manifest_bytes = canonicalize(manifest_obj)

    def bench_canonicalize() -> None:
        canonicalize(manifest_obj)

    operations.append(
        _summarize(
            "canonicalize_small_manifest",
            _run_timed(iterations, repeat, bench_canonicalize),
        )
    )

    def bench_sha256() -> None:
        sha256_hex(_SMALL_PAYLOAD)

    operations.append(
        _summarize(
            "sha256_hex_small_payload",
            _run_timed(iterations, repeat, bench_sha256),
        )
    )

    def bench_root_hash() -> None:
        compute_root_hash(manifest_bytes)

    operations.append(
        _summarize(
            "compute_root_hash_small_manifest_bytes",
            _run_timed(iterations, repeat, bench_root_hash),
        )
    )

    def bench_write() -> None:
        with TemporaryDirectory() as tmp:
            write_arb(
                Path(tmp),
                manifest=dict(_FIX_MANIFEST),
                graph_yaml=_FIX_GRAPH_YAML,
                inputs=dict(_FIX_INPUTS),
                segments=dict(_FIX_SEGMENTS),
                predictions=dict(_FIX_PREDICTIONS),
            )

    operations.append(
        _summarize("write_arb_spec8_fixture", _run_timed(iterations, repeat, bench_write))
    )

    def bench_read() -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(_FIX_MANIFEST),
                graph_yaml=_FIX_GRAPH_YAML,
                inputs=dict(_FIX_INPUTS),
                segments=dict(_FIX_SEGMENTS),
                predictions=dict(_FIX_PREDICTIONS),
            )
            read_arb(root)

    operations.append(
        _summarize("read_arb_spec8_fixture", _run_timed(iterations, repeat, bench_read))
    )

    def bench_validate() -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_arb(
                root,
                manifest=dict(_FIX_MANIFEST),
                graph_yaml=_FIX_GRAPH_YAML,
                inputs=dict(_FIX_INPUTS),
                segments=dict(_FIX_SEGMENTS),
                predictions=dict(_FIX_PREDICTIONS),
            )
            validate_arb(root)

    operations.append(
        _summarize(
            "validate_arb_spec8_fixture",
            _run_timed(iterations, repeat, bench_validate),
        )
    )

    return operations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure ARB v0.1 public API baseline timings (evidence only)."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Inner loop count per repeat (default: 50)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=5,
        help="Outer repeat count (default: 5)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="JSON output path",
    )
    ns = parser.parse_args(argv)
    if ns.iterations < 1 or ns.repeat < 1:
        print("iterations and repeat must be >= 1", file=sys.stderr)
        return 2

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "iterations": ns.iterations,
        "repeat": ns.repeat,
        "units": "nanoseconds",
        "non_sla": True,
        "operations": _measure_all(ns.iterations, ns.repeat),
    }

    out_path: Path = ns.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
