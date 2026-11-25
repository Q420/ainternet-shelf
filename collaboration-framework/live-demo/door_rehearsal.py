#!/usr/bin/env python3
"""Door, carriage, transition — the OFFLINE rehearsal
(door scope, 2026-11-24; scope and examiner acceptance
at INDEX 522–523).

Four scenarios driven by a deterministic scripted
stand-in through the working-set rehearsal's own stub
at the real NVIDIA connector seam — the REAL loop,
native adapter (text-judged, as a contribution is the
text contract's shape), doorway and executor run; no
provider is contacted and no room is stocked.

DOOR — the combined configuration with the delivery
declaration sealed at assembly, Gary's role-memory
snapshot and a structured opening record in the case:
the stand-in answers his first wake with one valid
contribution carrying a brief text. The contribution
records; the office files it at scratch/brief.md in
the run's sandbox; the loop completes on the filing.

CONTROL — the same contribution under a case carrying
NO delivery declaration (and a generation sealing
none): the contribution is an ordinary outcome, no
filing event stands, no file stands, and the stand-in
yields at his second wake, exactly as before the door.

GATE — the declared configuration: the first response
is a run-6-shaped malformed contribution envelope —
the contribute envelope's opening, unparseable (its
JSON breaks before the end). The gate fires: the raw
response stands preserved in the response-evidence
artifact, a DELIVERY_GATE event records what arrived
and what failed, the next wake's package carries the
correction, and his plain valid resubmission is filed
and completes the run.

REFUSAL — the declared configuration: the first
response is malformed prose with no contribute
discriminator. No gate fires; the run takes today's
stall path (provider_failure) unchanged.

FILING-FAILURE scenarios — the declared configuration
under injected filing failures (the examiner's
filing-integrity correction, 2026-11-24), each driven
through a double at one real seam, restored after the
scenario:

RECORD-FAILS — a worker draft stands at the
destination; the doorway's filing append is doubled
to raise after the write has landed. The destination
is rolled back to the draft's exact bytes; the loop
stalls fail-closed; no filing event stands.

RECORD-FAILS-NO-DRAFT — the same record failure with
no pre-existing file: the destination is absent
afterwards.

PARTIAL-WRITE — the filing's staging write is doubled
to write partial bytes and raise on its first call:
the destination never holds partial content — the
draft's bytes stand intact — and the loop stalls.

DOUBLE-FAILURE — the record append raises AND the
rollback's restore write fails: a durable
reconciliation note stands beside the destination
naming the incomplete filing.

COMMIT-FAILS — the filing's event INSERT genuinely
happens and the store's commit is doubled to fail
at that exact commit (the examiner's round-six
correction, 2026-11-24): the pending filing insert
must be rolled back before the stall is recorded,
so no filing event stands in the exported record
for a filing that was rolled back on disk, and the
destination returns to the draft's exact bytes.

Outputs land in the rehearsal work directory, one
subdirectory per scenario, in the working-set
rehearsal's shape (report.json, captures, export,
readout).
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

import working_set_rehearsal as _ws
from demo_run import DELIVERY, ROLE_MEMORY
from first_worker_run import _commission_brief
import stock_demo

import framework.loop as _loop_module  # noqa: E402
from framework.doorway import Doorway  # noqa: E402
from framework.record import FrameworkStore  # noqa: E402

HERE = Path(__file__).resolve().parent

BRIEF_TEXT = (
    "The collaborative agent framework lets generated "
    "agents work under a governed record: its Stage 2 "
    "accountability foundation and the agent layer's "
    "assembly, grants and bounded loop stand proven; "
    "a generated worker completing a real assignment "
    "inside the loop, and genuine collaboration "
    "between agents, do not yet. (Scripted stand-in "
    "brief for the door rehearsal.)")

OPENING = {
    "worker_statements": [
        "I understand the job: read the three sources "
        "and write a short brief for a newcomer."],
    "office_answers": [
        "Delivery is by contribution: hand the brief "
        "back as a contribute outcome and the office "
        "files it at scratch/brief.md."],
    "settled": [
        "Plain prose, about 600 words, the four "
        "coverage points, nothing invented."],
    "unresolved": [],
}

GROUNDS = (
    "Door rehearsal: the scripted stand-in's probe "
    "trials settled 5/5 native — the recommendation "
    "stands as evidence — and the stand-in examiner "
    "judges TEXT, because the case under examination "
    "is a contribution, a shape only the text "
    "contract carries. Rehearsal furniture by a "
    "scripted stand-in examiner.")


def _contribute_step(call_id, text):
    return {"respond": _ws._text_response(
        call_id, json.dumps({"outcome": "contribute",
                             "text": text})),
        "action": None}


def _yield_step(summary):
    return {"respond": _ws._text_response(
        "yield", json.dumps({"outcome": "yield",
                             "summary": summary})),
        "action": None}


def build_script_door():
    return {"chat": [
        _ws._identify_step("door"),
        _contribute_step("contribute-1", BRIEF_TEXT)],
        "chat-raw-bounded": _ws._probe_steps()}


def build_script_control():
    return {"chat": [
        _ws._identify_step("door-control"),
        _contribute_step("contribute-1", BRIEF_TEXT),
        _yield_step("Contributed the brief text as an "
                    "ordinary contribution.")],
        "chat-raw-bounded": _ws._probe_steps()}


# The gate scenario's malformed envelope: the
# contribute envelope's exact opening — the outcome
# discriminator as its first key, the text key opening
# its string — with the JSON broken before the end
# (the closing brace never arrives), run 6's shape.
MALFORMED_CONTRIBUTION = (
    '{\n  "outcome": "contribute",\n  "text": "'
    + BRIEF_TEXT + '"\n')


def build_script_gate():
    return {"chat": [
        _ws._identify_step("door-gate"),
        {"respond": _ws._text_response(
            "contribute-malformed",
            MALFORMED_CONTRIBUTION),
         "action": None},
        _contribute_step("contribute-2", BRIEF_TEXT)],
        "chat-raw-bounded": _ws._probe_steps()}


MALFORMED_PROSE = (
    "I have the brief ready but I cannot seem to "
    "format my answer properly this time, sorry.")


def build_script_refusal():
    return {"chat": [
        _ws._identify_step("door-refusal"),
        {"respond": _ws._text_response(
            "prose-malformed", MALFORMED_PROSE),
         "action": None}],
        "chat-raw-bounded": _ws._probe_steps()}


def _brief(*, declared):
    manifest, manifest_hash, _stock = \
        stock_demo.verify_source_set()
    kwargs = {}
    if declared:
        kwargs = {"delivery": DELIVERY,
                  "role_memory": ROLE_MEMORY,
                  "opening": OPENING}
    brief = _commission_brief(
        _ws.ASSIGNMENT_COMBINED, manifest_hash,
        glossary=_ws.GLOSSARY, onboarding=_ws.ONBOARDING,
        **kwargs)
    return brief, manifest, manifest_hash


# The filing-failure scenarios' pre-existing worker
# draft: the worker's own unfinished brief, standing
# at the deliverable destination before the office's
# filing is attempted. A failed filing must restore
# these bytes exactly — never delete them, never leave
# the contribution or a partial in their place.
DRAFT_TEXT = (
    "Draft in progress — my brief so far, unfinished. "
    "(Scripted stand-in draft for the door rehearsal's "
    "filing-failure scenarios.)")


def _stage_with_draft(sandbox, manifest):
    """Stage the sandbox sources as usual, then place
    the worker's draft at the declared destination."""
    problem = _ws._stage_sandbox_sources(sandbox,
                                         manifest)
    if problem is not None:
        return problem
    dest = Path(sandbox) / DELIVERY["destination"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(DRAFT_TEXT.encode("utf-8"))
    return None


@contextlib.contextmanager
def _record_append_fails():
    """The record-failure double: the doorway's filing
    append (Doorway.record_deliverable_filed — the
    exact seam the loop calls) raises, for the
    scenario's duration. The filing's write has already
    landed when this fires, which is the examiner's
    case: write succeeded, recording failed."""
    original = Doorway.record_deliverable_filed

    def double(self, *args, **kwargs):
        raise RuntimeError(
            "injected filing-record failure (door "
            "rehearsal double)")

    Doorway.record_deliverable_filed = double
    try:
        yield
    finally:
        Doorway.record_deliverable_filed = original


@contextlib.contextmanager
def _staging_write_fails(fail_on):
    """The write-failure double: the filing's staging
    write (framework.loop._filing_write — the filing's
    one write seam) writes partial bytes and raises on
    the calls numbered in `fail_on` (1-based), and
    delegates to the real write on every other call.
    fail_on={1} fails the filing's own staging write;
    fail_on={2} lets the filing's write land and fails
    the rollback's restore write."""
    original = _loop_module._filing_write
    calls = {"n": 0}

    def double(path, data):
        calls["n"] += 1
        if calls["n"] in fail_on:
            Path(path).write_bytes(
                data[:len(data) // 2])
            raise OSError(
                "injected partial filing write (door "
                "rehearsal double)")
        return original(path, data)

    _loop_module._filing_write = double
    try:
        yield
    finally:
        _loop_module._filing_write = original


def _double_failure():
    """Both failures at once: the record append raises
    and the rollback's restore write (the staging
    write's second call) fails — the path that must
    leave the reconciliation note."""
    stack = contextlib.ExitStack()
    stack.enter_context(_record_append_fails())
    stack.enter_context(_staging_write_fails({2}))
    return stack


@contextlib.contextmanager
def _filing_commit_fails():
    """The commit-failure double (the examiner's
    round-six correction): unlike the record-failure
    double above — which raises before the insert —
    this one lets the filing's event INSERT genuinely
    happen through the store's real append, then
    doubles the store's commit (FrameworkStore.commit,
    the store's own commit seam: the method whose one
    job is the connection's commit, called by
    record_deliverable_filed immediately after its
    append) to raise once, at exactly the filing's
    commit, without calling through. The filing insert
    stands pending in the store's open transaction
    when the failure fires; every later commit
    delegates to the real commit, so the stall's own
    recording proceeds — and would land the pending
    filing alongside the terminal if the filing path
    did not roll the transaction back first."""
    original_append = FrameworkStore.append
    original_commit = FrameworkStore.commit
    armed = {"on": False}

    def append_double(self, type_, *args, **kwargs):
        ev = original_append(self, type_, *args,
                             **kwargs)
        if type_ == "DELIVERABLE_FILED":
            armed["on"] = True
        return ev

    def commit_double(self):
        if armed["on"]:
            armed["on"] = False
            raise RuntimeError(
                "injected filing-commit failure (door "
                "rehearsal double)")
        return original_commit(self)

    FrameworkStore.append = append_double
    FrameworkStore.commit = commit_double
    try:
        yield
    finally:
        FrameworkStore.append = original_append
        FrameworkStore.commit = original_commit


def _run(work_dir, *, scenario, declared, script,
         stage=None, patch=None):
    brief, manifest, manifest_hash = _brief(
        declared=declared)
    if stage is None:
        stage_fn = lambda sandbox: \
            _ws._stage_sandbox_sources(sandbox, manifest)
    else:
        stage_fn = lambda sandbox: stage(sandbox,
                                         manifest)

    def go():
        return _ws._run_scenario(
            work_dir, scenario=scenario, brief=brief,
            manifest_hash=manifest_hash,
            seal_entries=manifest["sources"],
            stage_fn=stage_fn,
            script=script, grounds=GROUNDS,
            adapter_mode="text",
            freshness_suspended=True,
            delivery_declaration=declared)

    if patch is not None:
        with patch:
            return go()
    return go()


def run_rehearsal(work_dir):
    """Run all nine scenarios under `work_dir`
    (created fresh): the four door/gate scenarios and
    the five filing-failure scenarios. Returns
    {"door": report, "control": report, "gate":
    report, "refusal": report, "record_fails": report,
    "record_fails_nodraft": report, "partial_write":
    report, "double_failure": report, "commit_fails":
    report}."""
    work_dir = Path(work_dir).resolve()
    if work_dir.exists() and any(work_dir.iterdir()):
        raise RuntimeError(
            f"rehearsal work directory {work_dir} is not "
            f"empty; refusing to overwrite a standing "
            f"rehearsal")
    work_dir.mkdir(parents=True, exist_ok=True)
    door = _run(work_dir / "door", scenario="door",
                declared=True, script=build_script_door())
    control = _run(work_dir / "control",
                   scenario="door-control", declared=False,
                   script=build_script_control())
    gate = _run(work_dir / "gate", scenario="door-gate",
                declared=True, script=build_script_gate())
    refusal = _run(work_dir / "refusal",
                   scenario="door-refusal", declared=True,
                   script=build_script_refusal())
    record_fails = _run(
        work_dir / "filing-record-fails",
        scenario="door-filing-record-fails",
        declared=True, script=build_script_door(),
        stage=_stage_with_draft,
        patch=_record_append_fails())
    record_fails_nodraft = _run(
        work_dir / "filing-record-fails-nodraft",
        scenario="door-filing-record-fails-nodraft",
        declared=True, script=build_script_door(),
        patch=_record_append_fails())
    partial_write = _run(
        work_dir / "filing-partial-write",
        scenario="door-filing-partial-write",
        declared=True, script=build_script_door(),
        stage=_stage_with_draft,
        patch=_staging_write_fails({1}))
    double_failure = _run(
        work_dir / "filing-double-failure",
        scenario="door-filing-double-failure",
        declared=True, script=build_script_door(),
        stage=_stage_with_draft,
        patch=_double_failure())
    commit_fails = _run(
        work_dir / "filing-commit-fails",
        scenario="door-filing-commit-fails",
        declared=True, script=build_script_door(),
        stage=_stage_with_draft,
        patch=_filing_commit_fails())
    return {"door": door, "control": control,
            "gate": gate, "refusal": refusal,
            "record_fails": record_fails,
            "record_fails_nodraft": record_fails_nodraft,
            "partial_write": partial_write,
            "double_failure": double_failure,
            "commit_fails": commit_fails}


def main():
    import sys
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        HERE / "door-rehearsal"
    reports = run_rehearsal(work)
    print(json.dumps(
        {k: {"outcome": v.get("outcome"),
             "checker": v.get("checker")}
         for k, v in reports.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
