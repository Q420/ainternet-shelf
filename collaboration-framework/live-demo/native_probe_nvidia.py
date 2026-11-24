"""The NVIDIA-route native-offer probe's live driver
(NVIDIA-PROBE-BUILD-SCOPE-2026-11-24, passed).

    PYTHONPATH=src python3 live-demo/native_probe_nvidia.py \
        [--prepare-only] <suffix>

The run's directory is live-demo/native-offer-nvidia-<suffix>;
an existing directory is refused, as the harness refuses
an existing run. The driver:

1. regenerates the baseline request from the evidenced
   run's record (live-demo/first-worker-evidenced1, or
   NVIDIA_PROBE_SOURCE_DIR) by the framework's real
   construction path — framework.native_probe_nvidia
   does the work and verifies the regeneration against
   the record's own commitments;
2. derives the modified request (the three granted
   retrieval actions offered as native tools, tool
   choice omitted, the validation flag absent), builds
   the comparison artifact, and checks the scope's
   precondition — the comparison bound to the scope's
   full hashes (baseline / modified / definitions,
   differing at exactly ["tools"]) — a failure aborts
   before anything is sent anywhere;
3. writes comparison.json into the run directory;
4. with --prepare-only, stops there: no transport is
   built and no provider request is made;
5. otherwise makes the five trial generations over the
   NVIDIA connector's raw call — exactly one request
   per trial, paced at the settled 65-second monotonic
   floor, nothing dispatched or executed — and writes
   probe-evidence.json with the classifications, the
   counts, the delivered denominator and the reading
   the scope's S3 table produces.

This driver is machinery for a released run. The build
scope's passage authorises the build only: a live run
requires its own release examination, and nothing here
runs the worker, activates an assembly, or touches the
framework record. One open item stands for that release
stage, recorded in the build report: whether NVIDIA's
live catalogue serves the pinned model identifier the
bound construction names — a catalogue question this
build does not ask and does not assume.
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from framework import native_probe  # noqa: E402
from framework import native_probe_nvidia as nvn  # noqa: E402
from nvidia_connector_transport import (  # noqa: E402
    install_nvidia_connector_raw_call)

SOURCE_DIR = os.environ.get(
    "NVIDIA_PROBE_SOURCE_DIR",
    os.path.join(HERE, "first-worker-evidenced1"))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    prepare_only = "--prepare-only" in argv
    argv = [a for a in argv if a != "--prepare-only"]
    if len(argv) != 1:
        print("usage: native_probe_nvidia.py "
              "[--prepare-only] <suffix>")
        return 2
    suffix = argv[0]
    out_dir = os.path.join(HERE, f"native-offer-nvidia-{suffix}")
    if os.path.exists(out_dir):
        print(f"ABORT: {out_dir} already exists; the "
              f"probe does not overwrite a standing run")
        return 1
    with tempfile.TemporaryDirectory(
            prefix="native-offer-nvidia-baseline-") as work:
        try:
            prepared = nvn.prepare(
                SOURCE_DIR, work, nvn.MODEL_PIN)
        except nvn.NativeProbeRefusal as refusal:
            print(f"ABORT: {refusal}")
            return 1
    comparison = prepared["comparison"]
    problems = nvn.check_precondition(
        prepared["baseline"], prepared["modified"],
        comparison)
    if problems:
        print("ABORT: the request comparison fails the "
              "scope's precondition; no trial runs:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    native_probe.write_outputs(out_dir, comparison)
    print(f"baseline request: {comparison['baseline_sha256']}")
    print(f"modified request: {comparison['modified_sha256']}")
    print(f"definitions:      {comparison['definitions_sha256']}")
    print(f"differing paths:  {comparison['differing_paths']}")
    if prepare_only:
        print("prepare-only: comparison.json written; "
              "no provider request was made")
        return 0
    raw_call = install_nvidia_connector_raw_call(
        os.environ.get("NVIDIA_HELPER_PATH")
        if os.environ.get("NVIDIA_HELPER_PATH") else None,
        nvn.MODEL_PIN)
    try:
        trials = nvn.run_nvidia_trials(raw_call, prepared)
    except nvn.NativeProbeRefusal as refusal:
        print(f"ABORT: {refusal}")
        return 1
    evidence = nvn.probe_evidence_object(comparison, trials)
    native_probe.write_outputs(out_dir, comparison,
                               evidence)
    print(f"trials: settled {evidence['settled_count']} "
          f"of {evidence['trial_count']}; delivered "
          f"{evidence['delivered_count']} of "
          f"{evidence['trial_count']}; behaviour "
          f"{evidence['counts']['behaviour']}")
    print(f"reading: {evidence['reading']}")
    print(f"evidence hash: {evidence['evidence_hash']}")
    print(f"probe evidence: "
          f"{os.path.join(out_dir, 'probe-evidence.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
