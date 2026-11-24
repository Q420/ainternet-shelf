"""The native-offer probe's live driver
(NATIVE-OFFER-PROBE-SCOPE Rev 2, PASSED at INDEX 334).

    PYTHONPATH=src python3 live-demo/native_offer_probe.py \
        [--prepare-only] <suffix>

The run's directory is live-demo/native-offer-<suffix>;
an existing directory is refused, as the harness refuses
an existing run. The driver:

1. regenerates the baseline request from the evidenced
   run's record (live-demo/first-worker-evidenced1, or
   NATIVE_OFFER_SOURCE_DIR) by the framework's real
   construction path — framework.native_probe does the
   work and verifies the regeneration against the
   record's own commitments;
2. derives the modified request (the three granted
   retrieval actions offered as native tools, tool choice
   omitted), builds the comparison artifact, and checks
   the scope's precondition — a failure aborts before
   anything is sent anywhere;
3. writes comparison.json into the run directory;
4. with --prepare-only, stops there: no adapter is built
   and no provider request is made;
5. otherwise makes the five trial generations over the
   Groq connector's raw call — the same capture seam the
   assembly probe used — exactly one request per trial,
   nothing dispatched or executed, and writes
   probe-evidence.json with the classifications, the
   counts and the reading. The runner paces the trials
   (the paced repetition, INDEX 340): strictly
   sequential, each request starting at least 65 seconds
   after the previous request's start, each start and
   applied wait recorded in the evidence.

This driver is machinery for a released run. The scope
passage (INDEX 334) authorises the build only: a live
run requires the build's own release examination, and
nothing here runs the worker, activates an assembly, or
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
import first_worker_run as harness  # noqa: E402
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call)

SOURCE_DIR = os.environ.get(
    "NATIVE_OFFER_SOURCE_DIR",
    os.path.join(HERE, "first-worker-evidenced1"))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    prepare_only = "--prepare-only" in argv
    argv = [a for a in argv if a != "--prepare-only"]
    if len(argv) != 1:
        print("usage: native_offer_probe.py "
              "[--prepare-only] <suffix>")
        return 2
    suffix = argv[0]
    out_dir = os.path.join(HERE, f"native-offer-{suffix}")
    if os.path.exists(out_dir):
        print(f"ABORT: {out_dir} already exists; the "
              f"probe does not overwrite a standing run")
        return 1
    with tempfile.TemporaryDirectory(
            prefix="native-offer-baseline-") as work:
        try:
            baseline, package, info = \
                native_probe.build_baseline(
                    SOURCE_DIR, work,
                    harness.GROQ_MODEL_PIN)
            definitions, catalogue_source = \
                native_probe.derive_offered_definitions(
                    package, info["catalogue_hash"])
        except native_probe.NativeProbeRefusal as refusal:
            print(f"ABORT: {refusal}")
            return 1
    modified = native_probe.build_modified_request(
        baseline, definitions)
    comparison = native_probe.build_comparison(
        baseline, modified, definitions, catalogue_source,
        info)
    problems = native_probe.check_precondition(
        baseline, modified, comparison)
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
    adapter = harness._build_adapter("groq")
    raw_call = install_groq_connector_raw_call(
        adapter,
        os.environ.get("GROQ_HELPER_PATH",
                       harness.GROQ_CONNECTOR_HELPER),
        adapter.model)
    try:
        trials = native_probe.run_native_trials(
            raw_call, baseline, modified, comparison)
    except native_probe.NativeProbeRefusal as refusal:
        print(f"ABORT: {refusal}")
        return 1
    evidence = native_probe.probe_evidence_object(
        comparison, trials)
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
