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

Outputs land in the rehearsal work directory, one
subdirectory per scenario, in the working-set
rehearsal's shape (report.json, captures, export,
readout).
"""

from __future__ import annotations

import json
from pathlib import Path

import working_set_rehearsal as _ws
from demo_run import DELIVERY, ROLE_MEMORY
from first_worker_run import _commission_brief
import stock_demo

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


def _run(work_dir, *, scenario, declared, script):
    brief, manifest, manifest_hash = _brief(
        declared=declared)
    return _ws._run_scenario(
        work_dir, scenario=scenario, brief=brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox:
            _ws._stage_sandbox_sources(sandbox, manifest),
        script=script, grounds=GROUNDS,
        adapter_mode="text", freshness_suspended=True,
        delivery_declaration=declared)


def run_rehearsal(work_dir):
    """Run all four scenarios under `work_dir` (created
    fresh). Returns {"door": report, "control": report,
    "gate": report, "refusal": report}."""
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
    return {"door": door, "control": control,
            "gate": gate, "refusal": refusal}


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
