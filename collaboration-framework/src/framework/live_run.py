"""The minimal live-run harness — Piece 8 (A8).

Demonstrates the existing framework with two REAL model seats
behind the provider adapter. It redesigns nothing: every act
goes through the doorway under the existing authority rules;
it manufactures no acts, bypasses no gates, and gives the
models no tokens. The orchestrator, examiner and director
seats are conducted by the harness operator (as the test
suites conduct them); the two crew seats are occupied by the
adapter's models, whose words — contributions, declines,
failures — are whatever they actually return. The run is not
stage-managed.

Completion is attempted, never forced: the route runs only
through acts the record supports, and where it stops, the
run remains open and the report says so. A crew seat's own
completion claim is an act the response contract does not
elicit, so the route is expected to stop at readiness unless
the record supports more — the demonstration succeeds as
evidence either way.

The report is DERIVED matter, labelled as such: it narrates
wake outcomes from the drivers' returns. Where it attributes
a decline to a seat, that decline is a non-act — NO decline
event exists in the authoritative run record.

Run it:  python3 -m framework.live_run --store run.db \
             --report report.json [--observer-out run.html]
Configuration is by environment: ADAPTER_ENDPOINT,
ADAPTER_MODEL, ADAPTER_API_KEY_ENV (default NVIDIA_API_KEY),
ADAPTER_TIMEOUT (default 120).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from .adapter import AdapterFailure, OpenAICompatibleAdapter
from .doorway import Doorway, DoorwayRefusal
from .driver import Driver
from .observer import export_html
from .office import Office
from .onboarding import onboard
from .projection import snapshot as projection_snapshot
from .record import CONSTITUTION_HASH, FrameworkStore

RUN_ID = "run-live-1"
TREE = {"A": ["B"], "B": []}
GATES = {"assembly": "assembly", "completion": "completion",
         "B": "judgement"}
SEATS = {
    "orch-1": {"role": "orchestrator",
               "identity_status": "declared"},
    "exam-1": {"role": "examiner", "identity_status": "declared"},
    "dir-1": {"role": "director", "identity_status": "declared"},
    "crew-a": {"role": "crew", "identity_status": "declared"},
    "crew-b": {"role": "crew", "identity_status": "declared"},
}
BRIEFS = {
    "crew-a": {
        "part": "A",
        "assignment": "Write two or three sentences explaining "
                      "what a shared, durable record gives a "
                      "team of agents that a passing chat log "
                      "does not.",
        "verification_list": ["the text answers the assignment"],
    },
    "crew-b": {
        "part": "B",
        "assignment": "Part A's contribution stands in your "
                      "view. Write one or two sentences on what "
                      "it missed or got wrong.",
        "verification_list": ["the text engages part A's "
                              "contribution"],
    },
}
CREW = ["crew-a", "crew-b"]


def _act(doorway, store, token, type_, payload):
    return doorway.act(token, type_, payload,
                       view_seq=doorway.state()["head_seq"])


def run_demonstration(store_path, adapter, report_path=None,
                      observer_out=None):
    report = {"kind": "live-run harness report (derived matter, "
                      "not record)",
              "run_id": RUN_ID, "seats_live": CREW,
              "seats_conducted_by_operator":
                  ["orch-1", "exam-1", "dir-1"],
              "onboarding": {}, "wakes": [], "completion": {},
              "end_state": None}
    store = FrameworkStore(store_path)
    store.insert_run(RUN_ID, CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": RUN_ID, "tree": dict(TREE),
        "seats": dict(SEATS), "briefs": dict(BRIEFS),
        "gates": dict(GATES)})
    store.commit()
    doorway = Doorway(store)
    office = Office(doorway)
    tok = {s: doorway.issue_token(s) for s in SEATS}

    # Onboard the two live seats through the adapter (A5): the
    # declaration is the model's own words; provider_model_id is
    # the provider's report. Side by side, never merged, and the
    # identity status stays "declared".
    for seat in CREW:
        try:
            identity = adapter.identify()
        except AdapterFailure as exc:
            report["onboarding"][seat] = {
                "failed": exc.kind, "detail": exc.detail}
            report["end_state"] = "onboarding failed for " + seat
            _finish(store, report, report_path, observer_out)
            return report
        onboard(doorway, tok["orch-1"], seat,
                declaration=identity["declaration"],
                provider_model_id=identity["provider_model_id"],
                terms_acknowledged=True)
        # Piece 6 (F2): once onboarding stands, the seat's token
        # binds to the established declaration — re-issue it, or
        # the pre-onboarding token is refused (R5).
        tok[seat] = doorway.issue_token(seat)
        report["onboarding"][seat] = {
            "declaration": identity["declaration"],
            "provider_model_id": identity["provider_model_id"],
            "identity_status": "declared",
            "note": "two attributed claims, recorded verbatim; "
                    "no comparison verdict is recorded in the "
                    "run record"}

    # Assembly gate (examiner, conducted by the operator).
    _act(doorway, store, tok["exam-1"], "GATE_OUTCOME",
         {"joint": "assembly", "outcome": "allow"})

    # Cases issued through the office: verification, the
    # examiner's judgement, then authorisation — the recorded
    # issuance route (R15/R16).
    for seat in CREW:
        issued = office.issue_new(tok["orch-1"], seat)
        if not issued.get("ok"):
            report["end_state"] = f"case issue failed for {seat}: " \
                                  f"{issued.get('problems')}"
            _finish(store, report, report_path, observer_out)
            return report
        _act(doorway, store, tok["exam-1"], "CASE_JUDGED",
             {"case_id": issued["case_id"],
              "version": issued["version"]})
        office.authorise(tok["orch-1"], issued["case_id"],
                         issued["version"])

    # Wake the live seats, in tree order. Whatever they return
    # is what the record gets. A non-root part stands behind
    # its judgement gate (R22): before waking the seat that
    # works into it, the examiner records the gate's outcome
    # on the upstream work as it stands — the operator's
    # judgement, in the record like any other.
    report["gate_steps"] = []
    for seat in CREW:
        part = BRIEFS[seat]["part"]
        if part in GATES and GATES[part] == "judgement":
            try:
                _act(doorway, store, tok["exam-1"], "GATE_OUTCOME",
                     {"joint": part, "outcome": "allow"})
                report["gate_steps"].append(
                    f"judgement gate {part}: allow (recorded "
                    f"before waking {seat})")
            except DoorwayRefusal as refusal:
                report["gate_steps"].append(
                    f"judgement gate {part}: refused: "
                    f"{refusal.ground}")
        driver = Driver(doorway, seat, tok[seat], adapter)
        result = driver.wake_cycle()
        entry = {"seat": seat, "woke": result.get("woke"),
                 "failed": result.get("failed"),
                 "recorded": [e["type"] for e in
                              result.get("recorded", [])],
                 "refused": result.get("refused", [])}
        if result.get("declined") is not None:
            entry["declined"] = result["declined"]
            entry["decline_note"] = (
                "a decline is a non-act: no decline event "
                "exists in the authoritative run record; this "
                "attribution comes from the driver's returned "
                "wake outcome")
        report["wakes"].append(entry)

    # Attempt the completion route — only as far as the record
    # supports (A8). Each step is attempted through the doorway;
    # a refusal stops the route and is reported, not worked
    # around.
    state = doorway.state()
    steps = []
    steps.append("completion claim: not attempted — a crew "
                 "seat's own claim is an act the response "
                 "contract does not elicit, and the harness "
                 "manufactures no acts")
    try:
        _act(doorway, store, tok["orch-1"],
             "RUN_READY_FOR_COMPLETION", {})
        steps.append("readiness: recorded")
        _act(doorway, store, tok["exam-1"], "GATE_OUTCOME",
             {"joint": "completion", "outcome": "allow"})
        steps.append("completion gate: allow (recorded)")
        _act(doorway, store, tok["exam-1"], "CERTIFICATION",
             {"coverage": "full",
              "identity_status":
                  {s: "declared" for s in CREW}})
        steps.append("certification: recorded")
        _act(doorway, store, tok["orch-1"], "RUN_CLOSED", {})
        steps.append("run closed: recorded")
    except DoorwayRefusal as refusal:
        steps.append(f"route stopped: {refusal.ground}")
    report["completion"] = {"steps": steps}

    state = doorway.state()
    report["end_state"] = state["lifecycle"]
    _finish(store, report, report_path, observer_out)
    return report


def _finish(store, report, report_path, observer_out):
    """Quiesce the store, verify the record with the §3.10
    checker, render the observer, and write the report."""
    snap = projection_snapshot(store)
    run_id = store.get_run_id()
    store_path = store.path
    # Quiesce the WAL so the checker's immutable read accepts
    # the store (the Piece 7 suite's established pattern).
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    env = dict(os.environ)
    src = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "checker"],
        input=json.dumps({"store_path": store_path,
                          "run_id": run_id, "snapshot": snap}),
        capture_output=True, text=True, env=env, timeout=120)
    try:
        verdict = json.loads(proc.stdout)
        report["checker"] = {
            check: verdict["checks"][check]["result"]
            for check in verdict.get("checks", {})}
    except (ValueError, KeyError):
        report["checker"] = {"error": "checker verdict unreadable",
                              "stdout": proc.stdout[:500]}
    if observer_out:
        export_html(store_path, run_id, observer_out)
        report["observer_rendered_to"] = observer_out
    if report_path:
        with open(report_path, "w") as fh:
            json.dump(report, fh, indent=1)
    return report


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="framework.live_run")
    ap.add_argument("--store", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--observer-out")
    args = ap.parse_args(argv)
    adapter = OpenAICompatibleAdapter(
        endpoint=os.environ.get(
            "ADAPTER_ENDPOINT",
            "https://integrate.api.nvidia.com/v1/chat/completions"),
        model=os.environ.get("ADAPTER_MODEL"),
        api_key_env=os.environ.get("ADAPTER_API_KEY_ENV",
                                   "NVIDIA_API_KEY"),
        timeout=float(os.environ.get("ADAPTER_TIMEOUT", "120")))
    report = run_demonstration(args.store, adapter,
                               report_path=args.report,
                               observer_out=args.observer_out)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
