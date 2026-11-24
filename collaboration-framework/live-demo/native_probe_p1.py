"""Probe P1's live driver (NATIVE-ADAPTER-P1-PROBE-
PROPOSAL Rev 1, PASSED at INDEX 358).

    PYTHONPATH=src python3 live-demo/native_probe_p1.py \
        [--prepare-only] <suffix>

The run's directory is live-demo/native-probe-p1-<suffix>;
an existing directory is refused, as the harness refuses
an existing run. The driver:

1. builds the probe's construction from the evidenced
   run's record (live-demo/first-worker-evidenced1, or
   NATIVE_PROBE_P1_SOURCE_DIR) by the framework's real
   construction path — framework.native_probe_p1 does
   the work: the baseline regenerated and verified
   against the record, the definitions derived from
   the sealed catalogue and narrowed (sandbox.list and
   sandbox.search offered, sandbox.read_range
   withheld), the task context varied (the sources
   listing pre-presented, the brief required to rest
   on the full contents of sources/stock-take.md), and
   the two condition requests built (identical except
   for Groq's disable_tool_validation: absent / true);
2. builds the two-level comparison artifact and checks
   the release precondition — the condition pair
   differing at exactly the flag path, each condition
   differing from the admitted native-offer request at
   exactly the designed paths, the narrowing recomputed
   — a failure aborts before anything is sent anywhere;
3. writes comparison.json into the run directory;
4. with --prepare-only, stops there: no adapter is
   built and no provider request is made;
5. otherwise makes the ten trial generations over the
   Groq connector's raw call — five per condition,
   exactly one request per trial, paced at the settled
   65-second monotonic floor, nothing dispatched or
   executed — and writes probe-evidence.json with the
   classifications, the counts and the readings.

This driver is machinery for a released run. The
proposal's passage (INDEX 358) authorises the build
only: a live run requires its own release examination
(Ben's release, on Vane's examination), and nothing
here runs the worker, activates an assembly, or
touches the framework record.
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from framework import native_probe  # noqa: E402
from framework import native_probe_p1 as p1  # noqa: E402
import first_worker_run as harness  # noqa: E402
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call)

SOURCE_DIR = os.environ.get(
    "NATIVE_PROBE_P1_SOURCE_DIR",
    os.path.join(HERE, "first-worker-evidenced1"))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    prepare_only = "--prepare-only" in argv
    argv = [a for a in argv if a != "--prepare-only"]
    if len(argv) != 1:
        print("usage: native_probe_p1.py "
              "[--prepare-only] <suffix>")
        return 2
    suffix = argv[0]
    out_dir = os.path.join(HERE, f"native-probe-p1-{suffix}")
    if os.path.exists(out_dir):
        print(f"ABORT: {out_dir} already exists; the "
              f"probe does not overwrite a standing run")
        return 1
    with tempfile.TemporaryDirectory(
            prefix="native-probe-p1-baseline-") as work:
        try:
            prepared = p1.prepare(
                SOURCE_DIR, work, harness.GROQ_MODEL_PIN)
        except p1.NativeProbeRefusal as refusal:
            print(f"ABORT: {refusal}")
            return 1
    comparison = prepared["comparison"]
    problems = p1.check_precondition(
        prepared["baseline"], prepared["native_modified"],
        prepared["off_request"], prepared["on_request"],
        comparison, prepared["package"],
        prepared["info"]["catalogue_hash"])
    if problems:
        print("ABORT: the request comparison fails the "
              "probe's precondition; no trial runs:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    native_probe.write_outputs(out_dir, comparison)
    print(f"baseline request:  {comparison['baseline_sha256']}")
    print(f"native-offer req:  "
          f"{comparison['native_offer_modified_sha256']}")
    print(f"OFF request:       "
          f"{comparison['conditions']['off']['request_sha256']}")
    print(f"ON request:        "
          f"{comparison['conditions']['on']['request_sha256']}")
    print(f"narrowed defs:     "
          f"{comparison['narrowed_definitions_sha256']}")
    print(f"pair diff paths:   "
          f"{comparison['condition_pair_differing_paths']}")
    print(f"OFF vs native:     "
          f"{comparison['vs_native_offer']['off']['differing_paths']}")
    print(f"ON vs native:      "
          f"{comparison['vs_native_offer']['on']['differing_paths']}")
    if prepare_only:
        print("prepare-only: comparison.json written; "
              "no provider request was made")
        return 0
    adapter = harness._build_adapter("groq")
    raw_call = install_groq_connector_raw_call(
        adapter,
        os.environ.get("GROQ_HELPER_PATH",
                       harness.GROQ_CONNECTOR_HELPER),
        adapter.model)
    try:
        trials = p1.run_p1_trials(raw_call, prepared)
    except p1.NativeProbeRefusal as refusal:
        print(f"ABORT: {refusal}")
        return 1
    evidence = p1.probe_evidence_object(comparison, trials)
    native_probe.write_outputs(out_dir, comparison,
                               evidence)
    readings = evidence["readings"]
    print(f"trials: settled {evidence['settled_count']} "
          f"of {evidence['trial_count']}; behaviour "
          f"{evidence['counts']['behaviour']}")
    print(f"readings: off="
          f"{readings['per_condition']['off']['reading']}, "
          f"on="
          f"{readings['per_condition']['on']['reading']}, "
          f"cross={readings['cross_condition']}")
    print(f"evidence hash: {evidence['evidence_hash']}")
    print(f"probe evidence: "
          f"{os.path.join(out_dir, 'probe-evidence.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
