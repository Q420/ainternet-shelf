"""Probe P2's live driver (NATIVE-ADAPTER-P2-PROBE-
PROPOSAL Rev 1, PASSED at INDEX 358).

    PYTHONPATH=src python3 live-demo/native_probe_p2.py \
        [--prepare-only] <suffix>

The run's directory is live-demo/native-probe-p2-<suffix>;
an existing directory is refused, as the harness refuses
an existing run. The driver:

1. builds the probe's construction from the evidenced
   run's record (live-demo/first-worker-evidenced1, or
   NATIVE_PROBE_P2_SOURCE_DIR) by the framework's real
   construction path — framework.native_probe_p2 does
   the work: the baseline regenerated and verified
   against the record, the full granted catalogue
   derived from the sealed catalogue and offered
   natively (nothing withheld), and the task context
   varied as disclosed (the brief required to rest on
   sources/stock-take.md and sources/a3-pass.md, each
   in full; the sources listing pre-presented);
2. builds the comparison artifact and checks the
   release precondition — the request differing from
   the admitted native-offer request at exactly the
   task-context path, the tools field byte-unchanged —
   a failure aborts before anything is sent anywhere;
3. writes comparison.json into the run directory;
4. with --prepare-only, stops there: no adapter is
   built and no provider request is made;
5. otherwise makes the five trial generations over the
   Groq connector's raw call — exactly one request per
   trial, paced at the settled 65-second monotonic
   floor, nothing dispatched or executed — and writes
   probe-evidence.json with the per-call records, the
   counts and the reading.

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
from framework import native_probe_p2 as p2  # noqa: E402
import first_worker_run as harness  # noqa: E402
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call)

SOURCE_DIR = os.environ.get(
    "NATIVE_PROBE_P2_SOURCE_DIR",
    os.path.join(HERE, "first-worker-evidenced1"))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    prepare_only = "--prepare-only" in argv
    argv = [a for a in argv if a != "--prepare-only"]
    if len(argv) != 1:
        print("usage: native_probe_p2.py "
              "[--prepare-only] <suffix>")
        return 2
    suffix = argv[0]
    out_dir = os.path.join(HERE, f"native-probe-p2-{suffix}")
    if os.path.exists(out_dir):
        print(f"ABORT: {out_dir} already exists; the "
              f"probe does not overwrite a standing run")
        return 1
    with tempfile.TemporaryDirectory(
            prefix="native-probe-p2-baseline-") as work:
        try:
            prepared = p2.prepare(
                SOURCE_DIR, work, harness.GROQ_MODEL_PIN)
        except p2.NativeProbeRefusal as refusal:
            print(f"ABORT: {refusal}")
            return 1
    comparison = prepared["comparison"]
    problems = p2.check_precondition(
        prepared["baseline"], prepared["native_modified"],
        prepared["request"], comparison,
        prepared["package"],
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
    print(f"P2 request:        {comparison['request_sha256']}")
    print(f"definitions:       "
          f"{comparison['definitions_sha256']}")
    print(f"vs native paths:   "
          f"{comparison['vs_native_offer']['differing_paths']}")
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
        trials = p2.run_p2_trials(raw_call, prepared)
    except p2.NativeProbeRefusal as refusal:
        print(f"ABORT: {refusal}")
        return 1
    evidence = p2.probe_evidence_object(comparison, trials)
    native_probe.write_outputs(out_dir, comparison,
                               evidence)
    print(f"trials: settled {evidence['settled_count']} "
          f"of {evidence['trial_count']}; behaviour "
          f"{evidence['counts']['behaviour']}")
    print(f"reading: {evidence['reading']}")
    print(f"evidence hash: {evidence['evidence_hash']}")
    print(f"probe evidence: "
          f"{os.path.join(out_dir, 'probe-evidence.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
