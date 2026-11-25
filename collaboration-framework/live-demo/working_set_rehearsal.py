#!/usr/bin/env python3
"""Working-set carriage — the run-3 correction's OFFLINE
rehearsal (examiner's ruling, 2026-11-24).

Run 3's finding (INDEX 484/486): the full Nemotron run
stalled at the step ceiling having made twelve successful
retrieval dispatches and no progress, because each wake
package carried only the worker's most recent tool result
— the record retained the outcomes, but the worker's next
package did not retain their contents. The examiner's
ruling accepted working-set carriage under five
properties: accumulated, not latest-only; content and
provenance travel together (the served range preserved,
never expanded); no duplicate copies within a package;
reconstructable from the recorded outcomes, with the
checker independently reconstructing the exact set
presented at each iteration; and bounded, honestly — an
aggregate budget with over-budget material standing by
its provenance, marked not carried, never silently
truncated.

This rehearsal proves the correction offline, on the
examiner's narrow examination list, in five scenarios
driven by a deterministic scripted stand-in through a
stub at the real NVIDIA connector seam — the combined
rehearsal's pattern. The REAL loop, native adapter (with
the route's name translation), doorway and executor run;
no room is stocked (the scripts never call the execution
tool — the exec door is the combined rehearsal's proven
ground) and no provider is contacted.

Scenario A (continuity) runs the live driver's own
combined configuration — its grants, assignment and
glossary, imported from demo_run — against the released
source set, staged for the pull door exactly as the
driver stages it:
  (1) read sources/stock-take.md whole;
  (2) read sources/a3-pass.md whole;
  (3) read sources/stock-take.md AGAIN (the repeat);
  (4) read sources/index-tail.md in a range (lines
      1–4), proving a range stands in the set as the
      range actually retrieved, never expanded;
  (5) yield.
The witness reads the packages from the captured
requests and the outcomes from the record, and asserts
the set's growth, the dedupe, the range's preservation,
and the single presentation of every content.

Scenario B (budget) seals two synthetic sources of
40,000 bytes each (400 lines of exactly 100 bytes) into
the same configuration and pulls eight 100-line ranges
and one 10-line range across the two files — about
71,000 bytes of gatherings against the working set's
64,000-byte budget — so the final packages exercise the
stated over-budget behaviour: the entry that does not
fit stands by its provenance alone, marked not carried,
while a later smaller entry that does fit is still
carried.

Scenario C (freedom) is the freedom-first setup pass's
proof (2026-11-24), on the same combined configuration
and the same released source set:
  (1) read sources/index-tail.md WHOLE — 40,953 bytes,
      over the retrieval regime's per-result ceiling:
      under the working-set contract the read returns
      its full content as a recorded result, and the
      next wake's working set carries it whole;
  (2) read sources/stock-take.md whole;
  (3) read sources/a3-pass.md whole — the fourth wake
      then holds all three sources together, 57,562
      bytes carried against the 64,000 budget;
  (4) read sources/not-stocked.md — a path outside the
      case's sealed evidence boundary: the doorway
      refuses it, and the package presenting the
      refusal carries the failure instruction (what
      was asked, why in plain terms, the stocked
      sources as the working alternative);
  (5) read sources/not-stocked.md AGAIN — the package
      presenting the second refusal names it as a
      repeat: this exact call already failed at step 4;
  (6) yield.
Its packages also witness the orientation pass (Ben's
rulings on the worker consultation, 2026-11-24): every
wake states its step position and task status, and the
tool list equals the sealed grant set exactly.

Scenario D (batch) is the examiner's repeat-correction
witness (2026-11-24), judged TEXT — the native
per-response cap admits one call per response, so a
batch is exercised through the text contract, which
carries several tool requests in one response:
  (1) ONE response carrying TWO identical requests —
      read scratch/not-here.md, a granted door over a
      file that does not stand: both dispatch, both
      fail at the executor, and the package presenting
      both failures must name NEITHER as a repeat,
      because neither had been presented when the
      calls were made;
  (2) the identical request again in the next
      response — the package presenting its failure
      names it as a repeat of step 1, for this reason:
      the batch failures WERE presented in the wake
      between;
  (3) yield.

Scenario E (journal) witnesses the orientation pass's
Part A, on the combined configuration with the case
designating scratch/journal.md as the worker's
notebook:
  (1) write the first journal note (sandbox.write);
  (2) write the journal again carrying the first
      note plus a second — the package at each wake
      presents the journal as it stands: the first
      wake empty, then note one verbatim, then both
      notes in order. The append is the worker's own
      cooperative convention (he rewrites the notebook
      carrying what it held, plus the new note);
      nothing mechanically enforces append-only, and
      he could replace the notebook whole;
  (3) yield.

Scenario F (freshness) is the run-6 package's R31
witness (Ben's ruling, 2026-11-24: "Disable R31 until
we need to worry about that"), run as a pair on the
same combined configuration, judged TEXT — a
contribution is the text contract's outcome:
  (1) the worker answers his first wake with a
      contribution — the run-5 shape, the finished
      brief submitted as a contribute outcome. The
      answer is adjudicated after the iteration's
      response-evidence event has advanced the record
      past the package's frozen view, and that event
      names the case: the exact position in which
      run 5's deliveries were freshness-refused twice.
  (2) the yield.
The declared run's generation seals the freshness
guard's suspension, and the contribution records; the
control run seals nothing, and the same answer in the
same position stands refused under R31 — the pair
proves the switch works and the rule lives. Every
scenario's case also carries the run-6 package's
onboarding, and their packages witness the package's
structure: the onboarding at the first wake's head, a
short cover at later wakes, the deliverable statement
opening the assignment, the journal's purpose label,
and the tool list grouped by the job's phases.

Scenario G (staged) is the staged-onboarding witness
(INDEX 544, Ben's direction, 2026-11-25): the
generation seals the presentation contract beside the
working-set contract, and the scripted stand-in walks
the onboarding across his first wakes — his memory
introduced as his own (stage 1), his case's essentials
(stage 2), his files as pointers, listing the
briefcase himself at that stage (stage 3), his task
with the phase-grouped menu (stage 4) — then works
from dashboard wakes and completes the assignment
through the contribution door. No package in the run
carries the case dump, the view or the delta, and no
content item stands twice in any package. The control
is the rest of this rehearsal: the other scenarios'
generations seal no presentation declaration, and
their packages are the ordered packages they have
always been.

Outputs land in the rehearsal work directory, one
subdirectory per scenario: the run record, the stub's
captures, the decision receipt, the terminal readout,
and report.json.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "src"
RIG = ROOT / "room" / "rig"
for _p in (str(SRC), str(HERE), str(RIG)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fabric.canonical import canonical  # noqa: E402

from framework.adapter import (  # noqa: E402
    OpenAICompatibleAdapter)
from framework.doorway import (  # noqa: E402
    Doorway, established_case_content)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (  # noqa: E402
    CONSTITUTION_HASH, FrameworkStore)
from framework import tool_policy  # noqa: E402

from connector_transport import (  # noqa: E402
    install_connector_transport)
from nvidia_connector_transport import (  # noqa: E402
    install_nvidia_connector_raw_call)
from first_worker_run import (  # noqa: E402
    BOUNDS, RUN_ID, VERIFICATION_LIST, _act,
    _commission_brief, export_store, run_checker)
from demo_run import (  # noqa: E402
    ASSIGNMENT_COMBINED, GLOSSARY, GRANTS_COMBINED, MODEL,
    ONBOARDING, ROLE_MEMORY, _stage_sandbox_sources)

import stock_demo  # noqa: E402

ENDPOINT = ("https://integrate.api.nvidia.com/v1/chat/"
            "completions")
ROUTE = "nvidia"

# Scenario B's synthetic sources: 400 lines of exactly
# 100 bytes each — 40,000 bytes a file, every line
# distinct, so any range's content is exactly the file's
# bytes for those lines and its size is known to the
# byte before anything runs.
SYNTH_LINES = 400
SYNTH_LINE_BYTES = 100


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _synth_bytes(tag):
    lines = []
    for i in range(1, SYNTH_LINES + 1):
        head = f"{tag}{i:04d} "
        line = head + "x" * (SYNTH_LINE_BYTES - 1
                             - len(head)) + "\n"
        assert len(line.encode("utf-8")) == SYNTH_LINE_BYTES
        lines.append(line)
    return "".join(lines).encode("utf-8")


SYNTH_A = _synth_bytes("A")
SYNTH_B = _synth_bytes("B")

ASSIGNMENT_BUDGET = (
    "Read the two source documents named in the "
    "glossary, in ranges, and keep what you gather in "
    "front of you. (Working-set rehearsal, budget "
    "scenario: a scripted stand-in follows a fixed "
    "pull sequence; no brief is written.)")

GLOSSARY_BUDGET = [
    {"address": "sources/synth-a.md",
     "description": "Synthetic source A: 400 lines of "
                    "exactly 100 bytes. Pull it in "
                    "ranges."},
    {"address": "sources/synth-b.md",
     "description": "Synthetic source B: 400 lines of "
                    "exactly 100 bytes. Pull it in "
                    "ranges."},
    {"address": "scratch/",
     "description": "Your writing space."},
]


def _native_call(call_id, name, arguments):
    """One scripted provider response carrying a single
    native tool call — the combined rehearsal's shape."""
    return {
        "id": f"stub-{call_id}",
        "model": MODEL,
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(arguments),
                    },
                }],
            },
            "finish_reason": "tool_calls",
        }],
    }


def _text_response(call_id, content):
    return {
        "id": f"stub-{call_id}",
        "model": MODEL,
        "choices": [{
            "message": {"role": "assistant",
                        "content": content},
            "finish_reason": "stop",
        }],
    }


def _probe_steps():
    step = {
        "respond": _native_call(
            "fc-probe", "probe-lookup",
            {"object": "brass lantern"}),
        "action": None}
    return [dict(step) for _ in range(5)]


def _identify_step(scenario):
    return {"respond": _text_response(
        "identify",
        f"I am {MODEL}, a model served on the NVIDIA "
        f"route. (Scripted stand-in declaration for "
        f"the working-set offline rehearsal, "
        f"{scenario} scenario; no provider was "
        f"contacted.)"),
        "action": None}


def build_script_continuity():
    chat = [
        _identify_step("continuity"),
        # 1 — read the first source whole.
        {"respond": _native_call(
            "fc-ws-1", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 2 — read the second source whole.
        {"respond": _native_call(
            "fc-ws-2", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 3 — the repeat: the same read again.
        {"respond": _native_call(
            "fc-ws-3", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 4 — the third source in a range, as its
        # glossary entry directs.
        {"respond": _native_call(
            "fc-ws-4", "sandbox-read_range",
            {"path": "sources/index-tail.md",
             "start_line": 1, "end_line": 4}),
         "action": None},
        # 5 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Read the stock-take, the "
                           "A3 pass, the stock-take "
                           "again, and a range of the "
                           "index tail."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_freedom():
    chat = [
        _identify_step("freedom"),
        # 1 — the whole pull of index-tail: 40,953 bytes,
        # over the per-result ceiling the old populations
        # refuse at.
        {"respond": _native_call(
            "fc-f-1", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 2 — the second source whole.
        {"respond": _native_call(
            "fc-f-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 3 — the third source whole.
        {"respond": _native_call(
            "fc-f-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 4 — a path outside the sealed boundary: the
        # doorway refuses it; the presenting package
        # carries the failure instruction.
        {"respond": _native_call(
            "fc-f-4", "sandbox-read",
            {"path": "sources/not-stocked.md"}),
         "action": None},
        # 5 — the identical call again: the presenting
        # package names it as a repeat of step 4.
        {"respond": _native_call(
            "fc-f-5", "sandbox-read",
            {"path": "sources/not-stocked.md"}),
         "action": None},
        # 6 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Read all three sources whole; "
                           "asked twice for a file the "
                           "briefcase does not hold."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def _text_tool_requests(call_id, requests):
    """One scripted text-contract response carrying
    several tool requests — the batch shape the native
    per-response cap cannot express. The adapter's
    text contract names the list "requests"; the loop's
    internal shape renames it, as the adapter's own
    translation does."""
    return _text_response(call_id, json.dumps({
        "outcome": "tool_requests",
        "requests": requests}))


def build_script_batch():
    missing = {"tool": "sandbox.read",
               "parameters": {"path": "scratch/not-here.md"}}
    chat = [
        _identify_step("batch"),
        # 1 — ONE response, TWO identical requests: a
        # granted read of a file that does not stand.
        # Both dispatch; both fail at the executor.
        {"respond": _text_tool_requests(
            "batch-1", [dict(missing), dict(missing)]),
         "action": None},
        # 2 — the identical request again, after the
        # batch's failures were presented.
        {"respond": _text_tool_requests(
            "batch-2", [dict(missing)]),
         "action": None},
        # 3 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Asked three times for a "
                           "scratch file that does not "
                           "stand — twice in one response, "
                           "once after seeing both "
                           "failures."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


# Scenario E's journal notes: plain ASCII, each a
# complete note ending in a newline, so the append is
# visible byte for byte.
JOURNAL_NOTE_1 = (
    "Note 1 - where I was: started the assignment; "
    "the three sources stand in sources/, named in "
    "the glossary.\n")
JOURNAL_NOTE_2 = (
    "Note 2 - what to do next: pull index-tail whole "
    "(it returns whole now) and draft the brief.\n")


def build_script_journal():
    chat = [
        _identify_step("journal"),
        # 1 — the first journal note, through the
        # granted write door.
        {"respond": _native_call(
            "fc-j-1", "sandbox-write",
            {"path": "scratch/journal.md",
             "content": JOURNAL_NOTE_1}),
         "action": None},
        # 2 — the second note appended: sandbox.write
        # replaces the file, so the worker writes the
        # journal back with the new note added — the
        # journal his package carried, plus the note.
        {"respond": _native_call(
            "fc-j-2", "sandbox-write",
            {"path": "scratch/journal.md",
             "content": JOURNAL_NOTE_1 + JOURNAL_NOTE_2}),
         "action": None},
        # 3 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Kept a journal across the "
                           "run: two notes, appended in "
                           "order."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


# Scenario F's contribution text: a short brief-shaped
# contribution — the run-5 shape, in which the worker
# submitted his finished brief as a contribute outcome
# and the freshness guard refused it twice.
CONTRIBUTION_TEXT = (
    "The collaborative agent framework lets generated "
    "agents work under a governed record: the substrate "
    "pieces and the agent layer's assembly, grants and "
    "bounded loop stand proven; a live worker completing "
    "the standing assignment, and genuine multi-agent "
    "collaboration, do not yet. (Scripted stand-in "
    "contribution for the freshness rehearsal; no brief "
    "file is written.)")


def build_script_contribution(label):
    chat = [
        _identify_step(label),
        # 1 — the contribution: the run-5 shape. The
        # answer is adjudicated after the iteration's
        # response-evidence event has advanced the
        # record past the package's frozen view, and
        # that event names the case — the exact position
        # run 5's two refused deliveries stood in.
        {"respond": _text_response(
            "contribute-1",
            json.dumps({
                "outcome": "contribute",
                "text": CONTRIBUTION_TEXT})),
         "action": None},
        # 2 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Contributed the brief text "
                           "as a contribution."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


# Scenario G's contributed brief: the scripted worker's
# deliverable text, filed by the office through the
# contribution door. Plain words, deliberately short —
# the scenario witnesses the onboarding walk and the
# door, not composition.
STAGED_BRIEF_TEXT = (
    "The collaborative agent framework, briefly: a "
    "director, an orchestrator and an examiner design "
    "work as a process tree, and generated workers — "
    "assembled per task with their briefcase, their "
    "grants and their office — do the work in the open, "
    "on a record everything can be checked against. "
    "(Scripted stand-in's contribution for the staged-"
    "onboarding rehearsal; the office files it at "
    "scratch/brief.md.)")


def build_script_staged():
    """Scenario G's script: the staged onboarding walk.
    The stand-in takes each stage as it comes —
    acknowledges his memory and his case (no tools are
    offered at those wakes, and none are called), lists
    a file from the pointers at the files stage (the
    real pull the stage exists for), reads one source
    whole at the task stage, a second at the first
    dashboard wake, and completes the assignment
    through the contribution door."""
    chat = [
        _identify_step("staged"),
        # 1 — the memory stage: acknowledge, nothing
        # else is asked.
        {"respond": _text_response(
            "staged-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 2 — the case stage: acknowledge again.
        {"respond": _text_response(
            "staged-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: list a file from the
        # pointers himself — the stage's real pull
        # (sandbox.list takes a file's path and returns
        # its structure: size, lines, headings).
        {"respond": _native_call(
            "fc-st-1", "sandbox-list",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 4 — the task stage: read the first source
        # whole.
        {"respond": _native_call(
            "fc-st-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — the first dashboard wake: read the second
        # source whole.
        {"respond": _native_call(
            "fc-st-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 6 — the second dashboard wake: the
        # contribution, filed by the office at the
        # declared destination — the door completes the
        # assignment.
        {"respond": _text_response(
            "staged-contribute",
            json.dumps({
                "outcome": "contribute",
                "text": STAGED_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


# The early contribution the stage-gate scenarios offer:
# a brief sent before the task has been presented.
STAGED_GATE_TEXT = (
    "A brief sent before my task was presented: the "
    "framework is a collaborative agent framework; "
    "this text stands in the record, set aside "
    "unfiled, until the task arrives.")


def build_script_staged_gate_files():
    """Round nine's first gate scenario: the stand-in
    walks the onboarding honestly, then contributes at
    the FILES stage — before his task has been
    presented. The gate sets the contribution aside
    unfiled and the loop continues; at the task stage
    he reads a source, and at the first dashboard wake
    he contributes again — that contribution is the
    deliverable's arrival and completes the run."""
    chat = [
        _identify_step("staged-gate-files"),
        # 1 — the memory stage: acknowledge.
        {"respond": _text_response(
            "sgf-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 2 — the case stage: acknowledge.
        {"respond": _text_response(
            "sgf-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: the early contribution.
        # The stage gate fires: recorded, unfiled, the
        # loop continues.
        {"respond": _text_response(
            "sgf-early",
            json.dumps({
                "outcome": "contribute",
                "text": STAGED_GATE_TEXT})),
         "action": None},
        # 4 — the task stage: read the first source
        # whole.
        {"respond": _native_call(
            "fc-sgf-1", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — the first dashboard wake: the honest
        # contribution — filed, completing the run.
        {"respond": _text_response(
            "sgf-contribute",
            json.dumps({
                "outcome": "contribute",
                "text": STAGED_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_staged_gate_memory():
    """Round nine's second gate scenario: the stand-in
    contributes at the MEMORY stage — the first wake,
    before anything but his role's memory and the
    snapshot have been presented. The gate sets it
    aside; he acknowledges the case, lists a file at
    the files stage, and contributes honestly at the
    task stage, which files and completes."""
    chat = [
        _identify_step("staged-gate-memory"),
        # 1 — the memory stage: the early contribution.
        {"respond": _text_response(
            "sgm-early",
            json.dumps({
                "outcome": "contribute",
                "text": STAGED_GATE_TEXT})),
         "action": None},
        # 2 — the case stage: acknowledge.
        {"respond": _text_response(
            "sgm-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: list a file from the
        # pointers himself.
        {"respond": _native_call(
            "fc-sgm-1", "sandbox-list",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 4 — the task stage: the honest contribution —
        # filed, completing the run.
        {"respond": _text_response(
            "sgm-contribute",
            json.dumps({
                "outcome": "contribute",
                "text": STAGED_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_staged_noexample():
    """Round nine's omission scenario: the same
    onboarding walk as scenario G, but the case's
    glossary leads with a file that is not stocked —
    the office's demonstration call cannot be made, so
    no worked example stands in the seal and the files
    stage presents the map without one."""
    script = build_script_staged()
    script["chat"][0] = _identify_step("staged-noexample")
    return script


# Round ten's scenarios (INDEX 552): the directory form
# of sandbox.list, and the delivery-evidence gate. The
# declaration this job's case carries — the three
# sources, the standing assignment's evidence.
DELIVERY_EVIDENCE = {"addresses": [
    "sources/stock-take.md", "sources/a3-pass.md",
    "sources/index-tail.md"]}

# The evidence scenarios' contributed brief: the
# scripted worker's deliverable text, filed by the
# office through the contribution door once the named
# evidence stands gathered.
EVIDENCE_BRIEF_TEXT = (
    "The collaborative agent framework, briefly: "
    "generated workers do bounded jobs in their own "
    "offices, under a governed record — assembly, "
    "grants and the bounded loop stand proven, and one "
    "worker has now completed the standing assignment "
    "end to end in the office; genuine collaboration "
    "between workers does not yet stand. (Scripted "
    "stand-in's contribution for the delivery-evidence "
    "rehearsal; the office files it at "
    "scratch/brief.md.)")


def build_script_directory():
    """Round ten's directory scenario (the continuity
    configuration — Part A is population-independent):
    the stand-in lists his briefcase's directory both
    ways it can be spelled, lists his empty scratch,
    lists a file (the standing form), asks for a
    directory no grant covers, and yields. The two
    directory spellings must return the one result; the
    file's result must be the listing the performer has
    always returned for it."""
    chat = [
        _identify_step("directory"),
        # 1 — the directory, spelled bare.
        {"respond": _native_call(
            "fc-d-1", "sandbox-list",
            {"path": "sources"}),
         "action": None},
        # 2 — the same directory, spelled with the
        # trailing slash: the one governed route.
        {"respond": _native_call(
            "fc-d-2", "sandbox-list",
            {"path": "sources/"}),
         "action": None},
        # 3 — the scratch directory: empty, and his.
        {"respond": _native_call(
            "fc-d-3", "sandbox-list",
            {"path": "scratch"}),
         "action": None},
        # 4 — a file: the standing form of the tool.
        {"respond": _native_call(
            "fc-d-4", "sandbox-list",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — a directory under no grant's prefix: the
        # doorway refuses it, naming the ceiling prefix.
        {"respond": _native_call(
            "fc-d-5", "sandbox-list",
            {"path": "room/"}),
         "action": None},
        # 6 — the yield.
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Listed the briefcase both "
                           "ways, the scratch, and one "
                           "file; asked for a directory "
                           "outside my grants."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def _evidence_walk_steps(label):
    """The staged evidence scenarios' shared opening:
    acknowledge memory, acknowledge case, and at the
    files stage list the first source from the
    pointers — the habit pull, shape only."""
    return [
        _identify_step(label),
        {"respond": _text_response(
            f"{label}-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        {"respond": _text_response(
            f"{label}-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        {"respond": _native_call(
            f"fc-{label}-1", "sandbox-list",
            {"path": "sources/stock-take.md"}),
         "action": None},
    ]


def build_script_evidence_gates():
    """Round ten's progressive gate scenario: the
    stand-in begins the last source at the files stage
    with one range of it (a partial gather — it does
    not make the file stand), contributes at the task
    stage — the gate names all three sources; he reads
    one whole and contributes again — the gate names
    the other two; reads the second — the gate names
    the last; then completes the last file's ranges,
    which together compose its whole line range (the
    final range's asked end runs past the file's end
    and the performer clamps it — the record fact that
    establishes the file's whole line range, no listing
    of that file standing), and contributes a fourth
    time: filed, completing the run in twelve
    iterations — the rehearsal's standing step ceiling,
    each gate consuming exactly its own iteration."""
    chat = [
        _identify_step("evidence-gates"),
        # 1 — the memory stage: acknowledge.
        {"respond": _text_response(
            "eg-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 2 — the case stage: acknowledge.
        {"respond": _text_response(
            "eg-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: the first range of the
        # last source — lines 1–6 of its 24, a partial
        # gather only.
        {"respond": _native_call(
            "fc-eg-1", "sandbox-read_range",
            {"path": "sources/index-tail.md",
             "start_line": 1, "end_line": 6}),
         "action": None},
        # 4 — the task stage: the first contribution.
        # Gate: all three missing — the partial range
        # does not make its file stand.
        {"respond": _text_response(
            "eg-contribute-1",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 5 — read the first source whole.
        {"respond": _native_call(
            "fc-eg-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 6 — contribute again. Gate: two missing.
        {"respond": _text_response(
            "eg-contribute-2",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 7 — read the second source whole.
        {"respond": _native_call(
            "fc-eg-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 8 — contribute again. Gate: one missing.
        {"respond": _text_response(
            "eg-contribute-3",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 9–11 — the last source's remaining ranges:
        # 7–13, 14–20, and 21 to the file's end — the
        # asked end runs past it and the performer
        # clamps it to line 24. With the files stage's
        # 1–6, the four ranges compose the whole file.
        {"respond": _native_call(
            "fc-eg-4", "sandbox-read_range",
            {"path": "sources/index-tail.md",
             "start_line": 7, "end_line": 13}),
         "action": None},
        {"respond": _native_call(
            "fc-eg-5", "sandbox-read_range",
            {"path": "sources/index-tail.md",
             "start_line": 14, "end_line": 20}),
         "action": None},
        {"respond": _native_call(
            "fc-eg-6", "sandbox-read_range",
            {"path": "sources/index-tail.md",
             "start_line": 21, "end_line": 9999}),
         "action": None},
        # 12 — the fourth contribution: every named
        # address stands; filed, completing the run.
        {"respond": _text_response(
            "eg-contribute-4",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_evidence_listed():
    """Round ten's shape-is-not-substance scenario: the
    stand-in lists all three sources — every one of
    them stands listed in his working set — and
    contributes: the gate still names all three,
    because a listing is a file's shape, not its
    content. He then reads all three whole and
    contributes again: filed."""
    chat = _evidence_walk_steps("evidence-listed") + [
        # 4 — the task stage: list the second source.
        {"respond": _native_call(
            "fc-el-2", "sandbox-list",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 5 — list the third source.
        {"respond": _native_call(
            "fc-el-3", "sandbox-list",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 6 — contribute with all three listed and none
        # read. Gate: all three missing.
        {"respond": _text_response(
            "el-contribute-1",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 7–9 — read all three whole.
        {"respond": _native_call(
            "fc-el-4", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        {"respond": _native_call(
            "fc-el-5", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        {"respond": _native_call(
            "fc-el-6", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 10 — contribute again: filed.
        {"respond": _text_response(
            "el-contribute-2",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_evidence_whole():
    """Round ten's clean pass: the stand-in lists one
    file at the files stage, reads all three sources
    whole, and contributes — no gate fires, the filing
    stands, the run completes in seven iterations."""
    chat = _evidence_walk_steps("evidence-whole") + [
        # 4 — the task stage: read the first source.
        {"respond": _native_call(
            "fc-ew-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — read the second source whole.
        {"respond": _native_call(
            "fc-ew-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 6 — read the third source whole.
        {"respond": _native_call(
            "fc-ew-4", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 7 — the contribution: filed, no gate.
        {"respond": _text_response(
            "ew-contribute",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


# The third gate's scenarios (INDEX 557): the
# delivery-length gate. The declaration this job's case
# carries beside the evidence declaration — the floor
# under the brief.
DELIVERY_FLOOR = {"min_words": 550}


def _counted_text(word_count):
    """A contributed text of exactly `word_count` words
    under the office's count (whitespace-split): the
    evidence brief's own words, extended word by word
    from a plain sentence to the exact count — the
    scripted stand-in's deliverable at a governed
    length, so the gate's arithmetic is exercised at
    its boundary, not near it."""
    words = EVIDENCE_BRIEF_TEXT.split()
    filler = ("the framework's record stands exactly "
              "as the sources state it").split()
    i = 0
    while len(words) < word_count:
        words.append(filler[i % len(filler)])
        i += 1
    return " ".join(words[:word_count])


# One word under the floor, and exactly at it.
LENGTH_TEXT_UNDER = _counted_text(
    DELIVERY_FLOOR["min_words"] - 1)
LENGTH_TEXT_AT = _counted_text(
    DELIVERY_FLOOR["min_words"])


def build_script_length_gate():
    """The third gate's boundary scenario: the
    stand-in walks the staged onboarding, reads all
    three sources whole — the evidence stands, so the
    evidence gate has nothing to say — and contributes
    a brief one word under the declared floor: the
    length gate fires, naming the count it arrived
    with. He resubmits at exactly the floor: filed,
    completing the run in eight iterations."""
    chat = _evidence_walk_steps("length-gate") + [
        # 4 — the task stage: read the first source.
        {"respond": _native_call(
            "fc-lg-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — read the second source whole.
        {"respond": _native_call(
            "fc-lg-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 6 — read the third source whole.
        {"respond": _native_call(
            "fc-lg-4", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 7 — contribute one word under the floor.
        # Length gate: 549 of 550.
        {"respond": _text_response(
            "lg-contribute-1",
            json.dumps({
                "outcome": "contribute",
                "text": LENGTH_TEXT_UNDER})),
         "action": None},
        # 8 — resubmit at exactly the floor: filed.
        {"respond": _text_response(
            "lg-contribute-2",
            json.dumps({
                "outcome": "contribute",
                "text": LENGTH_TEXT_AT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_length_order_evidence():
    """The family's order, witnessed from the evidence
    side: the stand-in contributes a short brief with
    nothing read — the EVIDENCE gate fires (a brief is
    not judged for sufficiency before its evidence
    stands) and no length gate stands for that
    contribution. He reads all three whole and
    contributes the same short brief again: now the
    LENGTH gate fires. At the floor: filed, in nine
    iterations."""
    chat = _evidence_walk_steps(
        "length-order-evidence") + [
        # 4 — the task stage: contribute short, with
        # the evidence not gathered. Evidence gate.
        {"respond": _text_response(
            "loe-contribute-1",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 5–7 — read all three sources whole.
        {"respond": _native_call(
            "fc-loe-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        {"respond": _native_call(
            "fc-loe-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        {"respond": _native_call(
            "fc-loe-4", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 8 — the same short brief, evidence standing:
        # the length gate fires.
        {"respond": _text_response(
            "loe-contribute-2",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 9 — at the floor: filed.
        {"respond": _text_response(
            "loe-contribute-3",
            json.dumps({
                "outcome": "contribute",
                "text": LENGTH_TEXT_AT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_length_order_stage():
    """The family's order, witnessed from the stage
    side: the stand-in contributes a short brief at
    the FILES stage, before his task has been
    presented — the STAGE gate fires, and neither the
    evidence gate nor the length gate stands for that
    contribution. He then reads all three whole and
    contributes at the floor: filed, in seven
    iterations."""
    chat = [
        _identify_step("length-order-stage"),
        # 1 — the memory stage: acknowledge.
        {"respond": _text_response(
            "los-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 2 — the case stage: acknowledge.
        {"respond": _text_response(
            "los-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: contribute short,
        # before the task. Stage gate.
        {"respond": _text_response(
            "los-contribute-1",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
        # 4 — the task stage: read the first source.
        {"respond": _native_call(
            "fc-los-1", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — read the second source whole.
        {"respond": _native_call(
            "fc-los-2", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 6 — read the third source whole.
        {"respond": _native_call(
            "fc-los-3", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 7 — contribute at the floor: filed.
        {"respond": _text_response(
            "los-contribute-2",
            json.dumps({
                "outcome": "contribute",
                "text": LENGTH_TEXT_AT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_pointer():
    """The pointer-rule scenario (INDEX 568): the
    staged walk under the successor presentation
    contract. The stand-in acknowledges his memory and
    his case, lists the first source at the files stage
    (the stage's real pull), then reads all three
    sources whole, one per wake — each content stands
    in exactly one package, as that wake's newest
    result, and as a pointer in every package after.
    He then pulls the first source AGAIN — the re-pull
    a pointer invites — lists the second source (a
    small newest result, so the final wake is a
    dashboard wake with everything gathered and nothing
    bulky in front of him), and contributes: the
    evidence gate adjudicates on the record, where the
    three reads stand whole, while their contents stand
    in no current package — filed, completing the run
    in nine iterations."""
    chat = [
        _identify_step("pointer"),
        # 1 — the memory stage: acknowledge.
        {"respond": _text_response(
            "pointer-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 2 — the case stage: acknowledge.
        {"respond": _text_response(
            "pointer-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: list the first source
        # from the pointers — the stage's real pull.
        {"respond": _native_call(
            "fc-pointer-1", "sandbox-list",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 4 — the task stage: read the first source
        # whole.
        {"respond": _native_call(
            "fc-pointer-2", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 5 — the first dashboard wake: read the second
        # source whole.
        {"respond": _native_call(
            "fc-pointer-3", "sandbox-read",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 6 — read the third source whole.
        {"respond": _native_call(
            "fc-pointer-4", "sandbox-read",
            {"path": "sources/index-tail.md"}),
         "action": None},
        # 7 — the re-pull: read the first source again,
        # as its pointer invites. The working set gains
        # no second entry (the gather dedupes); the
        # content arrives again as this wake's newest
        # result — its second and only other standing.
        {"respond": _native_call(
            "fc-pointer-5", "sandbox-read",
            {"path": "sources/stock-take.md"}),
         "action": None},
        # 8 — list the second source: a small newest
        # result, so the final wake stands with all
        # three sources gathered, as pointers, and
        # nothing bulky in front of him.
        {"respond": _native_call(
            "fc-pointer-6", "sandbox-list",
            {"path": "sources/a3-pass.md"}),
         "action": None},
        # 9 — the contribution: every named address
        # stands in the record; filed, completing the
        # run.
        {"respond": _text_response(
            "pointer-contribute",
            json.dumps({
                "outcome": "contribute",
                "text": EVIDENCE_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


# The tool-shape scenario's failed generation: the
# stand-in's native reach, in the shape the live
# GPT-OSS run's refusal preserved — a container.exec
# call in the provider's own tool-call shape, testing
# whether the room is alive. The provider's refusal
# names it in its error body.
TOOLSHAPE_FAILED_GENERATION = json.dumps({
    "name": "container.exec",
    "arguments": {"cmd": [
        "bash", "-lc",
        "python3 - <<'PY'\nprint('test')\nPY"]}})

TOOLSHAPE_ERROR_BODY = {
    "error": {
        "message": "Tool choice is none, but model "
                   "called a tool",
        "type": "invalid_request_error",
        "code": "tool_use_failed",
        "failed_generation": TOOLSHAPE_FAILED_GENERATION}}

TOOLSHAPE_429_BODY = {
    "error": {
        "message": "Rate limit reached for model "
                   "openai/gpt-oss-120b in organization "
                   "org-rehearsal on tokens per minute "
                   "(TPM): Limit 8000, Used 7900, "
                   "Requested 900. Please try again in "
                   "30s.",
        "type": "tokens",
        "code": "rate_limit_exceeded"}}

# The tool-shape scenario's brief: plain words over
# the three sources, long enough to stand over the
# declared floor — the run must end in a filing, so
# the text is written to the job's own figures (about
# 600 words; the door files nothing under 550).
TOOLSHAPE_BRIEF_TEXT = (
    "The collaborative agent framework is a way for "
    "several agents to work on the same job together, "
    "through shared work rather than through messages "
    "about the work. A director decides what is to be "
    "done. An office assembles a worker for one bounded "
    "piece of that work: it chooses the model, states "
    "the worker's identity, grants exactly the tools "
    "the job needs, and packs a briefcase holding the "
    "assignment, the sources the job rests on, and the "
    "terms the work is judged under. The worker wakes "
    "in a room of its own, reads what it was given, "
    "gathers what it needs through the tools it holds, "
    "and delivers its work back through the office's "
    "door, where the delivery is checked against the "
    "record before it is filed. Everything that happens "
    "stands in a durable record, so the work survives "
    "any one worker: a second worker, assembled later, "
    "can be handed the same briefcase and continue from "
    "the record rather than from anyone's memory of it. "
    "What has been proven so far is the ground floor of "
    "that design. An assembly can be generated with its "
    "identity and its grants sealed, and the grants are "
    "enforced: a worker can call only what it was "
    "granted, in the scope it was granted. A worker can "
    "pull real source documents through the doorway, "
    "keep what it gathers in front of it across wakes, "
    "and write a deliverable that the office files, with "
    "the filing itself standing in the record. The "
    "record can be replayed and checked independently, "
    "event by event, and the checks derive what the "
    "worker was shown rather than trusting what the "
    "machinery says it showed. The door the worker "
    "delivers through is gated, and the gates correct "
    "rather than merely refuse: a delivery offered "
    "before its evidence stands gathered is set aside "
    "with the missing files named, a delivery under "
    "the declared length is set aside with its count "
    "named, and each correction stands in the record "
    "beside the act it answered, so a later reader "
    "can see not only what was delivered but what was "
    "turned back on the way, and why it was turned "
    "back, and what the worker did next with the "
    "correction in front of him. One worker has "
    "completed "
    "a real assignment end to end in its own office: it "
    "read three real sources and its brief was filed "
    "through the door it was given. What is not proven "
    "is everything above that ground floor. No two "
    "workers have yet collaborated on one piece of "
    "work, changing it in ways that change each other's "
    "next steps; the framework's claim to collaboration, "
    "as against one worker working alone in a well-kept "
    "room, stands untested. The worker's composition "
    "has been exercised only on short briefs, and its "
    "behaviour over long jobs, under failing tools, and "
    "across changes of occupant in the same role is "
    "largely unmeasured. Several doors the design names "
    "are still unbuilt: the worker cannot yet knock and "
    "ask the office a question mid-job, and the process "
    "tree that would show him the whole job with his "
    "own part lit exists as a design, not as machinery. "
    "The honest next step is the smallest one that "
    "tests the framework's actual claim: put a second "
    "worker in the same role's room, on the same files, "
    "with the role's memory carried between them, and "
    "watch whether the work continues from the record "
    "without the first worker's help. Until that runs, "
    "the framework is a well-built office with one "
    "proven tenant, and it should be described as "
    "exactly that and no more than that today.")


def build_script_toolshape():
    """The tool-shape scenario (the calibration): the
    calibrated room under the pointer-rule contract,
    judged TEXT — the GPT-OSS configuration. The
    stand-in walks the stages, reads the first source
    at the task stage, and then reaches for a tool
    natively: the stub answers with the provider's
    refusal body (HTTP 400's shape, code
    tool_use_failed, the failed generation preserved),
    exactly as the live run's wire carried it. The
    gate answers with its correction; the next wake
    carries it, and the stand-in — taught — reads the
    remaining sources in the text shape and delivers
    a brief that stands over the floor: filed,
    completing the run."""
    chat = [
        _identify_step("toolshape"),
        # 1 — the memory stage: acknowledge.
        {"respond": _text_response(
            "toolshape-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 2 — the case stage: acknowledge.
        {"respond": _text_response(
            "toolshape-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        # 3 — the files stage: the stand-in reads the
        # first source — the stage's own pull, in the
        # text shape — so gathering stands underway
        # when the refusal comes at the task stage.
        {"respond": _text_tool_requests(
            "toolshape-read-1", [{
                "tool": "sandbox.read",
                "parameters": {
                    "path": "sources/stock-take.md"}}]),
         "action": None},
        # 4 — the task stage: the native reach. The
        # stub's answer is the provider's refusal body
        # itself, standing on the helper's stdout
        # exactly as an OpenAI-style error body stands
        # there on the live seam.
        {"respond": TOOLSHAPE_ERROR_BODY,
         "action": None},
        # 5 — the first dashboard wake: the correction
        # rides this package. Taught, the stand-in
        # reads the two remaining sources in the text
        # shape, in one response.
        {"respond": _text_tool_requests(
            "toolshape-read-2", [
                {"tool": "sandbox.read",
                 "parameters": {
                     "path": "sources/a3-pass.md"}},
                {"tool": "sandbox.read",
                 "parameters": {
                     "path": "sources/index-tail.md"}}]),
         "action": None},
        # 6 — the contribution: every named address
        # stands read whole in the record, and the
        # text stands over the floor; filed, completing
        # the run.
        {"respond": _text_response(
            "toolshape-contribute",
            json.dumps({
                "outcome": "contribute",
                "text": TOOLSHAPE_BRIEF_TEXT})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_toolshape_refused():
    """The tool-shape scenario's narrowness control:
    the same walk, but the provider's answer at the
    task stage is a rate-limit refusal (429's shape,
    code rate_limit_exceeded). That class is not the
    gate's business: no gate event stands, no
    correction is owed, and the run stalls as a
    provider failure exactly as it always has."""
    chat = [
        _identify_step("toolshape-refused"),
        {"respond": _text_response(
            "tsr-ack-1",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        {"respond": _text_response(
            "tsr-ack-2",
            json.dumps({"outcome": "acknowledge"})),
         "action": None},
        {"respond": _text_tool_requests(
            "tsr-read-1", [{
                "tool": "sandbox.read",
                "parameters": {
                    "path": "sources/stock-take.md"}}]),
         "action": None},
        {"respond": TOOLSHAPE_429_BODY,
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


def build_script_budget():
    def rr(call_id, path, start, end):
        return {"respond": _native_call(
            call_id, "sandbox-read_range",
            {"path": path, "start_line": start,
             "end_line": end}),
            "action": None}

    chat = [
        _identify_step("budget"),
        rr("fc-wb-1", "sources/synth-a.md", 1, 100),
        rr("fc-wb-2", "sources/synth-a.md", 101, 200),
        rr("fc-wb-3", "sources/synth-a.md", 201, 300),
        rr("fc-wb-4", "sources/synth-a.md", 301, 400),
        rr("fc-wb-5", "sources/synth-b.md", 1, 100),
        rr("fc-wb-6", "sources/synth-b.md", 101, 200),
        rr("fc-wb-7", "sources/synth-b.md", 201, 210),
        rr("fc-wb-8", "sources/synth-b.md", 211, 310),
        {"respond": _text_response(
            "yield",
            json.dumps({
                "outcome": "yield",
                "summary": "Pulled eight ranges across "
                           "the two synthetic sources."})),
         "action": None},
    ]
    return {"chat": chat,
            "chat-raw-bounded": _probe_steps()}


STUB_SOURCE = '''#!/usr/bin/env python3
"""The working-set rehearsal's stub helper: stands in
for the NVIDIA connector helper at its own seam.
Invoked exactly as the real helper is — [python,
helper, "chat"|"chat-raw-bounded", model], the request
JSON on stdin — it records the exact request bytes to
the captures file and answers from the script: the
provider JSON itself for "chat"; for
"chat-raw-bounded", the bounded envelope the real
helper frames, wrapping the same provider JSON. No
network, no credential, no provider."""
import base64
import hashlib
import json
import os
import sys


def main():
    mode = sys.argv[1]
    model = sys.argv[2]
    body = sys.stdin.buffer.read()
    with open(os.environ["WS_STUB_SCRIPT"],
              encoding="utf-8") as fh:
        script = json.load(fh)
    state_path = os.environ["WS_STUB_STATE"]
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = {}
    index = int(state.get(mode, 0))
    state[mode] = index + 1
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    with open(os.environ["WS_STUB_CAPTURES"], "a",
              encoding="utf-8") as fh:
        fh.write(json.dumps({
            "mode": mode, "model": model, "index": index,
            "request_sha256": hashlib.sha256(body).hexdigest(),
            "request_bytes": len(body),
            "request_b64": base64.b64encode(body).decode(
                "ascii")}) + "\\n")
    steps = script.get(mode) or []
    if index >= len(steps):
        sys.stderr.write(
            f"working-set stub: script exhausted for "
            f"mode {mode} at index {index}\\n")
        return 3
    payload = json.dumps(
        steps[index]["respond"]).encode("utf-8")
    if mode == "chat-raw-bounded":
        envelope = {
            "phase": "response_received", "status": 200,
            "body_b64": base64.b64encode(payload).decode(
                "ascii"),
            "body_complete": True, "stop_reason": "eof",
            "error_kind": None, "read_error_kind": None}
        sys.stdout.write(json.dumps(envelope))
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _run_scenario(work_dir, *, scenario, brief,
                  manifest_hash, seal_entries, stage_fn,
                  script, grounds, adapter_mode="native",
                  freshness_suspended=False,
                  delivery_declaration=False,
                  delivery_evidence_declaration=False,
                  delivery_floor_declaration=False,
                  presentation_declaration=False):
    """Run one scenario's rehearsal in `work_dir`
    (created fresh; must not already hold a rehearsal).
    Returns the report dict (also written to
    work_dir/report.json)."""
    work_dir = Path(work_dir).resolve()
    if work_dir.exists() and any(work_dir.iterdir()):
        raise RuntimeError(
            f"rehearsal work directory {work_dir} is not "
            f"empty; refusing to overwrite a standing "
            f"rehearsal")
    run_dir = work_dir / "run"
    run_dir.mkdir(parents=True, exist_ok=True)

    stub_path = work_dir / "stub_helper.py"
    stub_path.write_text(STUB_SOURCE, encoding="utf-8")
    stub_path.chmod(0o755)
    script_path = work_dir / "stub_script.json"
    script_path.write_text(
        json.dumps(script, indent=1), encoding="utf-8")
    state_path = work_dir / "stub_state.json"
    state_path.write_text("{}", encoding="utf-8")
    captures_path = work_dir / "captures.jsonl"
    captures_path.write_text("", encoding="utf-8")
    os.environ["WS_STUB_SCRIPT"] = str(script_path)
    os.environ["WS_STUB_STATE"] = str(state_path)
    os.environ["WS_STUB_CAPTURES"] = str(captures_path)

    # COMMISSION — the case under the scenario's brief,
    # the scenario's source set sealed as its boundary.
    store_path = str(run_dir / "run.db")
    store = FrameworkStore(store_path)
    store.insert_run(RUN_ID, CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": RUN_ID,
        "tree": {"part-A": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": brief},
    })
    store.commit()
    doorway = Doorway(store)
    office = Office(doorway)
    gen = Generator(doorway)
    tok = {s: doorway.issue_token(s)
           for s in ("orch-1", "exam-1", "dir-1",
                     "crew-1")}
    _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
        "material_id": f"source-manifest sha256:"
                       f"{manifest_hash}",
        "boundary": ["crew-1"]})
    for entry in seal_entries:
        _act(doorway, tok["orch-1"], "MATERIAL_SEALED", {
            "material_id": f"{entry['path']} "
                           f"sha256:{entry['sha256']}",
            "boundary": ["crew-1"]})
    issued = office.issue_new(tok["orch-1"], "crew-1")
    if not issued.get("ok"):
        raise RuntimeError(
            f"case issue failed: {issued.get('problems')}")
    _act(doorway, tok["exam-1"], "CASE_JUDGED",
         {"case_id": issued["case_id"],
          "version": issued["version"]})
    office.authorise(tok["orch-1"], issued["case_id"],
                     issued["version"])
    content, _version = established_case_content(
        doorway.state(), issued["case_id"])
    boundary = (content or {}).get("evidence_boundary") \
        or []
    if not any(manifest_hash in str(item)
               for item in boundary):
        raise RuntimeError(
            "the issued case's evidence boundary does "
            "not identify the source manifest hash")
    if (content or {}).get("loop_bounds") != BOUNDS:
        raise RuntimeError(
            "the issued case's loop_bounds are not the "
            "scoped bounds")

    # STAGE THE PULL DOOR — the executor sandbox's
    # sources, hash-verified by the staging itself.
    staging_problem = stage_fn(run_dir / "sandbox")
    if staging_problem is not None:
        raise RuntimeError(
            f"sandbox staging failed: {staging_problem}")

    # THE WORKED EXAMPLE (round nine's correction pair,
    # INDEX 548): under the presentation declaration the
    # office performs the demonstration call against the
    # staged sandbox, through the same governed
    # performer a dispatch runs, BEFORE the assembly is
    # generated — the call's real result is what
    # generation seals. Where the call cannot be made
    # (the file is not there to be called on), no
    # example stands and generation proceeds without
    # one. The call is the contract's own (the
    # calibration): under the first contract, the
    # listing of the case's first glossary file; under
    # the pointer-rule successor, a read of the
    # glossary's smallest stocked file, by its staged
    # bytes — the office's choice, so the one stage
    # that shows a whole file stays within the
    # population's package bound.
    worked_example = None
    if presentation_declaration:
        glossary_addresses = []
        for entry in (content or {}).get("glossary") or []:
            if isinstance(entry, dict) and isinstance(
                    entry.get("address"), str):
                glossary_addresses.append(entry["address"])
        example_executor = Executor(
            doorway, str(run_dir / "sandbox"),
            claim_dir=str(run_dir / "claims"),
            deadline=150.0)
        if presentation_declaration == \
                tool_policy.PRESENTATION_CONTRACT_V2:
            chosen = None
            for address in glossary_addresses:
                try:
                    size = len((run_dir / "sandbox"
                                / address).read_bytes())
                except OSError:
                    continue
                if chosen is None or size < chosen[1]:
                    chosen = (address, size)
            if chosen is not None:
                try:
                    example_result = \
                        example_executor.worked_example_read(
                            chosen[0])
                    worked_example = {
                        "tool": "sandbox.read",
                        "path": chosen[0],
                        "result": example_result}
                except Exception:  # noqa: BLE001 — the
                    # call cannot be made: no example.
                    worked_example = None
        elif glossary_addresses:
            first_address = glossary_addresses[0]
            try:
                example_result = \
                    example_executor.worked_example_list(
                        first_address)
                worked_example = {
                    "tool": "sandbox.list",
                    "path": first_address,
                    "result": example_result}
            except Exception:  # noqa: BLE001 — the call
                # cannot be made: no example stands.
                worked_example = None

    # ASSEMBLE — the adapter on the NVIDIA route's seam,
    # its transport the stub helper; generation under the
    # probe contract and the exec catalogue contract,
    # grants the combined set (the working-set contract's
    # population).
    adapter = OpenAICompatibleAdapter(
        endpoint=ENDPOINT, model=MODEL, timeout=300.0,
        route=ROUTE)
    install_connector_transport(
        adapter, str(stub_path), MODEL)
    gen.propose(
        tok["orch-1"], "crew-1", part="part-A",
        role_requirements="a model able to pull source "
                          "documents through the doorway "
                          "and keep what it gathers in "
                          "front of it")
    generated = gen.generate(
        tok["orch-1"], "crew-1", adapter.identify,
        skills=[], grants=GRANTS_COMBINED,
        model_requested=MODEL, probe=True, exec_room=True,
        freshness_suspended=freshness_suspended,
        delivery_declaration=delivery_declaration,
        delivery_evidence_declaration=
        delivery_evidence_declaration,
        delivery_floor_declaration=
        delivery_floor_declaration,
        presentation_declaration=presentation_declaration,
        worked_example=worked_example)
    if not generated.get("ok"):
        raise RuntimeError(
            f"generation failed: "
            f"{generated.get('problems')}")
    assembly_id = generated["assembly_id"]
    sealed = None
    for ev in store.all_events():
        if ev["type"] == "ASSEMBLY_GENERATED" and \
                ev["payload"].get(
                    "assembly_id") == assembly_id:
            sealed = ev["payload"]

    # PROBE — five scripted trials through the real
    # NVIDIA raw-call seam over the stub.
    raw_call = install_nvidia_connector_raw_call(
        helper_path=str(stub_path), model=MODEL)
    probe_result = gen.probe(
        tok["orch-1"], assembly_id, raw_call,
        route=ROUTE, model=MODEL)
    gen.verify(tok["orch-1"], assembly_id)

    # JUDGE — the rehearsal's decision receipt, retained
    # before the judgement is recorded; the judgement
    # binds its canonical hash, as the live phases bind
    # the examiner's.
    probed_payload = None
    for ev in store.all_events():
        if ev["type"] == "ASSEMBLY_PROBED" and \
                ev["payload"].get(
                    "assembly_id") == assembly_id:
            probed_payload = ev["payload"]
    receipt = {
        "run_id": RUN_ID,
        "assembly_id": assembly_id,
        "generated_record_hash":
            probed_payload["generated_record_hash"],
        "probed_seq": probe_result["probed_seq"],
        "probe_evidence_hash":
            probe_result["evidence_hash"],
        "fingerprint": probed_payload["fingerprint"],
        "adapter_mode": adapter_mode,
        "mode_grounds": grounds,
        "examiner": "working-set rehearsal (scripted "
                    "stand-in examiner)",
        "decided_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt_path = work_dir / "decision-receipt.json"
    with open(receipt_path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
        fh.write("\n")
    receipt_hash = _sha256_bytes(canonical(receipt))
    judgement = gen.judgement(
        assembly_id, adapter_mode=adapter_mode,
        mode_grounds=receipt["mode_grounds"],
        decision_receipt_hash=receipt_hash,
        decision_examiner=receipt["examiner"])
    _act(doorway, tok["exam-1"], "ASSEMBLY_JUDGED",
         judgement)
    packed = gen.pack(tok["orch-1"], assembly_id)
    gen.authorise(tok["orch-1"], assembly_id)

    # RUN — the executor holds the staged sandbox (no
    # room: the scripts never call the execution tool);
    # the loop drives the real adapter/doorway path.
    executor = Executor(
        doorway, str(run_dir / "sandbox"),
        claim_dir=str(run_dir / "claims"), deadline=150.0)
    gen.activate(tok["orch-1"], assembly_id)
    result = Loop(doorway, packed["instance_token"],
                  adapter, executor=executor,
                  evidence_store=str(run_dir)).run()

    # COLLECT — the checker, the export, the readout.
    events = store.all_events()
    verdict = run_checker(store)
    export_store(store_path,
                 str(run_dir / "run-export.json"))
    readout_path = work_dir / "terminal-readout.md"
    readout = subprocess.run(
        [sys.executable, str(HERE / "terminal_readout.py"),
         "render", str(run_dir / "run-export.json"),
         "-o", str(readout_path)],
        capture_output=True, text=True)

    report = {
        "scenario": scenario,
        "outcome": result.get("outcome"),
        "iterations": result.get("iterations"),
        "sealed_working_set_contract":
            (sealed or {}).get("working_set_contract"),
        "sealed_freshness_guard":
            (sealed or {}).get("freshness_guard"),
        "sealed_delivery":
            (sealed or {}).get("delivery"),
        "sealed_delivery_evidence":
            (sealed or {}).get("delivery_evidence"),
        "sealed_delivery_floor":
            (sealed or {}).get("delivery_floor"),
        "sealed_presentation_contract":
            (sealed or {}).get("presentation_contract"),
        "sealed_worked_example":
            (sealed or {}).get("worked_example"),
        "sealed_catalogue_contract":
            (sealed or {}).get("catalogue_contract"),
        "manifest_hash": manifest_hash,
        "manifest_sha": {e["path"]: e["sha256"]
                         for e in seal_entries},
        "checker": verdict["checks"],
        "terminal_readout": {
            "rendered": readout.returncode == 0
            and readout_path.exists()},
        "captures": str(captures_path),
        "export": str(run_dir / "run-export.json"),
    }
    with open(work_dir / "report.json", "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    return report


def run_rehearsal(work_dir):
    """Run all eight scenarios under `work_dir` (created
    fresh). Returns {"continuity": report, "budget":
    report, "freedom": report, "batch": report,
    "journal": report, "freshness": report,
    "freshness_control": report, "staged": report}."""
    work_dir = Path(work_dir).resolve()
    if work_dir.exists() and any(work_dir.iterdir()):
        raise RuntimeError(
            f"rehearsal work directory {work_dir} is not "
            f"empty; refusing to overwrite a standing "
            f"rehearsal")
    work_dir.mkdir(parents=True, exist_ok=True)

    # Scenario A — the released source set, verified by
    # stock_demo's own check (no room is stocked; the
    # pull door serves the same verified bytes).
    manifest, manifest_hash, _stock = \
        stock_demo.verify_source_set()
    continuity = _run_scenario(
        work_dir / "continuity",
        scenario="continuity",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY, onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_continuity(),
        grounds="Working-set rehearsal, continuity "
                "scenario: the scripted stand-in's probe "
                "trials settled 5/5 native, and the "
                "combined configuration's judgement is "
                "native. Rehearsal furniture by a "
                "scripted stand-in examiner.")

    # Scenario B — the synthetic oversized gather.
    entries_b = [
        {"path": "sources/synth-a.md",
         "sha256": _sha256_bytes(SYNTH_A)},
        {"path": "sources/synth-b.md",
         "sha256": _sha256_bytes(SYNTH_B)},
    ]
    manifest_b = {"sources": entries_b}
    manifest_hash_b = stock_demo.manifest_hash_of(
        manifest_b)

    def stage_budget(sandbox):
        sandbox = Path(sandbox)
        for rel, data in (("sources/synth-a.md", SYNTH_A),
                          ("sources/synth-b.md", SYNTH_B)):
            dest = sandbox / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            if _sha256_bytes(dest.read_bytes()) != \
                    _sha256_bytes(data):
                return f"the staged {rel} does not hash " \
                    f"to its manifest entry"
        (sandbox / "scratch").mkdir(parents=True,
                                    exist_ok=True)
        return None

    brief_b = {
        "part": "part-A",
        "assignment": ASSIGNMENT_BUDGET,
        "verification_list": list(VERIFICATION_LIST),
        "evidence_boundary":
            f"source manifest sha256:{manifest_hash_b}; "
            "sources: sources/synth-a.md, "
            "sources/synth-b.md",
        "loop_bounds": dict(BOUNDS),
        "glossary": [dict(entry)
                     for entry in GLOSSARY_BUDGET],
        "onboarding": dict(ONBOARDING),
    }
    budget = _run_scenario(
        work_dir / "budget",
        scenario="budget",
        brief=brief_b,
        manifest_hash=manifest_hash_b,
        seal_entries=entries_b,
        stage_fn=stage_budget,
        script=build_script_budget(),
        grounds="Working-set rehearsal, budget scenario: "
                "the scripted stand-in's probe trials "
                "settled 5/5 native, and the combined "
                "configuration's judgement is native. "
                "Rehearsal furniture by a scripted "
                "stand-in examiner.")

    # Scenario C — the freedom-first setup pass: the
    # released source set under the same combined
    # configuration as continuity.
    freedom = _run_scenario(
        work_dir / "freedom",
        scenario="freedom",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY, onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_freedom(),
        grounds="Working-set rehearsal, freedom "
                "scenario (the freedom-first setup "
                "pass): the scripted stand-in's probe "
                "trials settled 5/5 native, and the "
                "combined configuration's judgement is "
                "native. Rehearsal furniture by a "
                "scripted stand-in examiner.")

    # Scenario D — the examiner's repeat correction:
    # the same combined configuration, judged TEXT so
    # one response can carry a batch of identical
    # requests (the native per-response cap admits one
    # call per response; the batch shape is the text
    # contract's). The probe's recommendation stands as
    # evidence; the judgement is the stand-in examiner's
    # decision, as the live phases judge.
    batch = _run_scenario(
        work_dir / "batch",
        scenario="batch",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY, onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_batch(),
        grounds="Working-set rehearsal, batch scenario "
                "(the repeat correction): the scripted "
                "stand-in's probe trials settled 5/5 "
                "native — the recommendation stands as "
                "evidence — and the stand-in examiner "
                "judges TEXT, because the case under "
                "examination is a batch of identical "
                "requests in one response, a shape only "
                "the text contract carries. Rehearsal "
                "furniture by a scripted stand-in "
                "examiner.",
        adapter_mode="text")

    # Scenario E — the orientation pass's journal: the
    # combined configuration, the case designating the
    # worker's notebook.
    journal = _run_scenario(
        work_dir / "journal",
        scenario="journal",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY,
            journal="scratch/journal.md",
            onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_journal(),
        grounds="Working-set rehearsal, journal "
                "scenario (the orientation pass): the "
                "scripted stand-in's probe trials "
                "settled 5/5 native, and the combined "
                "configuration's judgement is native. "
                "Rehearsal furniture by a scripted "
                "stand-in examiner.")

    # Scenario F — the run-6 package's freshness pair
    # (Ben's R31 ruling, 2026-11-24): the run-5
    # contribution shape, judged TEXT — a contribution
    # is the text contract's outcome; the probe's
    # recommendation stands as evidence and the
    # judgement is the stand-in examiner's, as the live
    # phases judge. The declared run seals the
    # suspension; the control run seals nothing.
    freshness = _run_scenario(
        work_dir / "freshness",
        scenario="freshness",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY, onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_contribution("freshness"),
        grounds="Working-set rehearsal, freshness "
                "scenario (the run-6 package; Ben's "
                "R31 ruling): the scripted stand-in's "
                "probe trials settled 5/5 native — the "
                "recommendation stands as evidence — "
                "and the stand-in examiner judges TEXT, "
                "because the case under examination is "
                "a contribution, a shape only the text "
                "contract carries. The generation seals "
                "the freshness guard's suspension under "
                "the director's ruling. Rehearsal "
                "furniture by a scripted stand-in "
                "examiner.",
        adapter_mode="text",
        freshness_suspended=True)
    freshness_control = _run_scenario(
        work_dir / "freshness-control",
        scenario="freshness-control",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY, onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_contribution(
            "freshness-control"),
        grounds="Working-set rehearsal, freshness "
                "control scenario (the run-6 package): "
                "the same contribution shape as the "
                "freshness scenario, judged TEXT for "
                "the same reason, but the generation "
                "seals NO suspension — the control that "
                "proves the rule lives: the same answer "
                "in the same position stands refused "
                "under R31. Rehearsal furniture by a "
                "scripted stand-in examiner.",
        adapter_mode="text")
    # Scenario G — staged onboarding (INDEX 544,
    # Ben's direction, 2026-11-25): the same combined
    # configuration, the generation additionally sealing
    # the presentation contract, the case carrying the
    # role memory, the opening record, the journal
    # designation and the delivery declaration. The
    # scripted stand-in walks the stages: acknowledge
    # (memory), acknowledge (case), list the briefcase
    # himself (files — the stage's real pull), read a
    # source whole (task), read another (dashboard), and
    # complete through the contribution door. The
    # control stands beside it in the same run: every
    # other scenario's generation seals no presentation
    # declaration, and their packages present exactly as
    # they always have.
    staged_brief = _commission_brief(
        ASSIGNMENT_COMBINED, manifest_hash,
        glossary=GLOSSARY,
        journal="scratch/journal.md",
        onboarding=ONBOARDING,
        delivery={"destination": "scratch/brief.md",
                  "route": "contribution-v1"},
        role_memory=ROLE_MEMORY,
        opening={
            "worker_statements": [
                "The job is to read the three "
                "sources and write the brief; the "
                "deliverable is the file "
                "scratch/brief.md."],
            "office_answers": [
                "Confirmed: the sources stand in "
                "sources/, named in the glossary; "
                "the brief is plain prose, at most "
                "~600 words."],
            "settled": [
                "No work product is produced in "
                "the opening; the work happens in "
                "the room."],
            "unresolved": []})
    staged = _run_scenario(
        work_dir / "staged",
        scenario="staged",
        brief=staged_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_staged(),
        grounds="Staged-onboarding rehearsal (INDEX "
                "544): the scripted stand-in's probe "
                "trials settled 5/5 native, and the "
                "combined configuration's judgement is "
                "native. The generation seals the "
                "staged-onboarding presentation "
                "contract under the director's "
                "direction. Rehearsal furniture by a "
                "scripted stand-in examiner.",
        freshness_suspended=True,
        delivery_declaration=True,
        presentation_declaration=True)
    # Round nine's scenarios (INDEX 548 + the INDEX 549
    # fold-in): the stage gate and the worked example,
    # under the same combined configuration and the same
    # staged brief. In the first, the stand-in
    # contributes at the files stage — before his task
    # has been presented — and the gate sets the
    # contribution aside unfiled while the loop
    # continues to an honest completion. In the second,
    # he contributes at the memory stage, the first
    # wake. In the third, the case's glossary leads
    # with a file that is not stocked, so the office's
    # demonstration call cannot be made and no worked
    # example stands in the seal.
    staged_gate_files = _run_scenario(
        work_dir / "staged-gate-files",
        scenario="staged-gate-files",
        brief=staged_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_staged_gate_files(),
        grounds="Stage-gate rehearsal (INDEX 548): "
                "the scripted stand-in's probe trials "
                "settled 5/5 native, and the combined "
                "configuration's judgement is native. "
                "The generation seals the "
                "staged-onboarding presentation "
                "contract and the office's worked "
                "example. Rehearsal furniture by a "
                "scripted stand-in examiner.",
        freshness_suspended=True,
        delivery_declaration=True,
        presentation_declaration=True)
    staged_gate_memory = _run_scenario(
        work_dir / "staged-gate-memory",
        scenario="staged-gate-memory",
        brief=staged_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_staged_gate_memory(),
        grounds="Stage-gate rehearsal (INDEX 548): "
                "the scripted stand-in's probe trials "
                "settled 5/5 native, and the combined "
                "configuration's judgement is native. "
                "The generation seals the "
                "staged-onboarding presentation "
                "contract and the office's worked "
                "example. Rehearsal furniture by a "
                "scripted stand-in examiner.",
        freshness_suspended=True,
        delivery_declaration=True,
        presentation_declaration=True)
    staged_noexample = _run_scenario(
        work_dir / "staged-noexample",
        scenario="staged-noexample",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=[{
                "address": "sources/not-stocked.md",
                "description":
                    "A file the case names but the "
                    "briefcase does not hold."}] + GLOSSARY,
            journal="scratch/journal.md",
            onboarding=ONBOARDING,
            delivery={"destination": "scratch/brief.md",
                      "route": "contribution-v1"},
            role_memory=ROLE_MEMORY,
            opening={
                "worker_statements": [
                    "The job is to read the three "
                    "sources and write the brief; the "
                    "deliverable is the file "
                    "scratch/brief.md."],
                "office_answers": [
                    "Confirmed: the sources stand in "
                    "sources/, named in the glossary; "
                    "the brief is plain prose, at most "
                    "~600 words."],
                "settled": [
                    "No work product is produced in "
                    "the opening; the work happens in "
                    "the room."],
                "unresolved": []}),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_staged_noexample(),
        grounds="Worked-example omission rehearsal "
                "(INDEX 548): the scripted stand-in's "
                "probe trials settled 5/5 native, and "
                "the combined configuration's "
                "judgement is native. The generation "
                "seals the staged-onboarding "
                "presentation contract; the office's "
                "demonstration call could not be made "
                "on the case's first glossary file, so "
                "no worked example stands in the seal. "
                "Rehearsal furniture by a scripted "
                "stand-in examiner.",
        freshness_suspended=True,
        delivery_declaration=True,
        presentation_declaration=True)
    # Round ten's scenarios (INDEX 552). The directory
    # scenario runs in the continuity configuration —
    # sandbox.list's directory form is the performer's
    # and the ceiling's, standing in every population.
    # The evidence scenarios run in the staged
    # configuration with the case additionally carrying
    # the delivery-evidence declaration, sealed at
    # generation: the three sources are the evidence
    # this job's delivery must rest on. Scenario G
    # above stands as the control beside them: its
    # generation seals no evidence declaration, its
    # worker reads two sources whole and only lists
    # the third, and his contribution is adjudicated
    # exactly as it always has been — filed.
    directory = _run_scenario(
        work_dir / "directory",
        scenario="directory",
        brief=_commission_brief(
            ASSIGNMENT_COMBINED, manifest_hash,
            glossary=GLOSSARY, onboarding=ONBOARDING),
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_directory(),
        grounds="Directory-form rehearsal (INDEX 552): "
                "the scripted stand-in's probe trials "
                "settled 5/5 native, and the combined "
                "configuration's judgement is native. "
                "Rehearsal furniture by a scripted "
                "stand-in examiner.")
    evidence_brief = _commission_brief(
        ASSIGNMENT_COMBINED, manifest_hash,
        glossary=GLOSSARY,
        journal="scratch/journal.md",
        onboarding=ONBOARDING,
        delivery={"destination": "scratch/brief.md",
                  "route": "contribution-v1"},
        role_memory=ROLE_MEMORY,
        opening={
            "worker_statements": [
                "The job is to read the three "
                "sources and write the brief; the "
                "deliverable is the file "
                "scratch/brief.md."],
            "office_answers": [
                "Confirmed: the sources stand in "
                "sources/, named in the glossary; "
                "the brief is plain prose, at most "
                "~600 words."],
            "settled": [
                "No work product is produced in "
                "the opening; the work happens in "
                "the room."],
            "unresolved": []},
        delivery_evidence=DELIVERY_EVIDENCE)
    evidence_grounds = (
        "Delivery-evidence rehearsal (INDEX 552): the "
        "scripted stand-in's probe trials settled 5/5 "
        "native, and the combined configuration's "
        "judgement is native. The generation seals the "
        "staged-onboarding presentation contract and "
        "the case's delivery-evidence declaration. "
        "Rehearsal furniture by a scripted stand-in "
        "examiner.")
    evidence_gates = _run_scenario(
        work_dir / "evidence-gates",
        scenario="evidence-gates",
        brief=evidence_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_evidence_gates(),
        grounds=evidence_grounds,
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        presentation_declaration=True)
    evidence_listed = _run_scenario(
        work_dir / "evidence-listed",
        scenario="evidence-listed",
        brief=evidence_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_evidence_listed(),
        grounds=evidence_grounds,
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        presentation_declaration=True)
    evidence_whole = _run_scenario(
        work_dir / "evidence-whole",
        scenario="evidence-whole",
        brief=evidence_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_evidence_whole(),
        grounds=evidence_grounds,
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        presentation_declaration=True)
    # The third gate's scenarios (INDEX 557). The
    # length scenarios run in the staged configuration
    # with the case additionally carrying the
    # delivery-length declaration beside the evidence
    # declaration, sealed at generation: the brief must
    # arrive with at least the declared floor of words
    # before the door files it. The evidence scenarios
    # above stand as the control beside them: their
    # generation seals no length declaration, their
    # worker's short brief is adjudicated exactly as it
    # always has been — filed once its evidence stands.
    length_brief = _commission_brief(
        ASSIGNMENT_COMBINED, manifest_hash,
        glossary=GLOSSARY,
        journal="scratch/journal.md",
        onboarding=ONBOARDING,
        delivery={"destination": "scratch/brief.md",
                  "route": "contribution-v1"},
        role_memory=ROLE_MEMORY,
        opening={
            "worker_statements": [
                "The job is to read the three "
                "sources and write the brief; the "
                "deliverable is the file "
                "scratch/brief.md."],
            "office_answers": [
                "Confirmed: the sources stand in "
                "sources/, named in the glossary; "
                "the brief is plain prose, at most "
                "~600 words."],
            "settled": [
                "No work product is produced in "
                "the opening; the work happens in "
                "the room."],
            "unresolved": []},
        delivery_evidence=DELIVERY_EVIDENCE,
        delivery_floor=DELIVERY_FLOOR)
    length_grounds = (
        "Delivery-length rehearsal (INDEX 557): the "
        "scripted stand-in's probe trials settled 5/5 "
        "native, and the combined configuration's "
        "judgement is native. The generation seals the "
        "staged-onboarding presentation contract, the "
        "case's delivery-evidence declaration and its "
        "delivery-length declaration. Rehearsal "
        "furniture by a scripted stand-in examiner.")
    length_gate = _run_scenario(
        work_dir / "length-gate",
        scenario="length-gate",
        brief=length_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_length_gate(),
        grounds=length_grounds,
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        delivery_floor_declaration=True,
        presentation_declaration=True)
    length_order_evidence = _run_scenario(
        work_dir / "length-order-evidence",
        scenario="length-order-evidence",
        brief=length_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_length_order_evidence(),
        grounds=length_grounds,
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        delivery_floor_declaration=True,
        presentation_declaration=True)
    length_order_stage = _run_scenario(
        work_dir / "length-order-stage",
        scenario="length-order-stage",
        brief=length_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_length_order_stage(),
        grounds=length_grounds,
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        delivery_floor_declaration=True,
        presentation_declaration=True)
    # The pointer-rule scenario (INDEX 568): the
    # evidence brief under the successor presentation
    # contract — the same case, the same declarations,
    # the same sources; only the presentation of the
    # working set changes. The v1 scenarios above stand
    # as its control: their seals, packages and counts
    # are exactly what they were.
    pointer = _run_scenario(
        work_dir / "pointer",
        scenario="pointer",
        brief=evidence_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_pointer(),
        grounds="Pointer-rule rehearsal (INDEX 568): "
                "the scripted stand-in's probe trials "
                "settled 5/5 native, and the combined "
                "configuration's judgement is native. "
                "The generation seals the pointer-rule "
                "presentation contract "
                "(staged-onboarding-v2) and the case's "
                "delivery-evidence declaration, under "
                "the director's direction. Rehearsal "
                "furniture by a scripted stand-in "
                "examiner.",
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        presentation_declaration="staged-onboarding-v2")
    # The calibration's scenarios: the pointer-rule
    # room with the length declaration standing (the
    # length brief), judged TEXT — the GPT-OSS
    # configuration, whose worker's debrief is the
    # calibration's blueprint. In the first, the
    # stand-in's native reach at the task stage meets
    # the provider's tool-shape refusal and the gate
    # answers it; in the second, the same position
    # meets a rate-limit refusal and the run stalls as
    # it always has — the gate's narrowness, witnessed
    # beside its firing.
    toolshape_grounds = (
        "Tool-shape rehearsal (the calibration): the "
        "scripted stand-in's probe trials settled 5/5 "
        "native — the recommendation stands as "
        "evidence — and the stand-in examiner judges "
        "TEXT, the GPT-OSS configuration's judgement "
        "(Vane's INDEX 300 judgement, under which the "
        "live GPT-OSS runs ran): no native tools are "
        "offered, so a native reach is the provider's "
        "to refuse. The generation seals the "
        "pointer-rule presentation contract and the "
        "case's delivery, delivery-evidence and "
        "delivery-length declarations. Rehearsal "
        "furniture by a scripted stand-in examiner.")
    toolshape = _run_scenario(
        work_dir / "toolshape",
        scenario="toolshape",
        brief=length_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_toolshape(),
        grounds=toolshape_grounds,
        adapter_mode="text",
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        delivery_floor_declaration=True,
        presentation_declaration="staged-onboarding-v2")
    toolshape_refused = _run_scenario(
        work_dir / "toolshape-refused",
        scenario="toolshape-refused",
        brief=length_brief,
        manifest_hash=manifest_hash,
        seal_entries=manifest["sources"],
        stage_fn=lambda sandbox: _stage_sandbox_sources(
            sandbox, manifest),
        script=build_script_toolshape_refused(),
        grounds=toolshape_grounds,
        adapter_mode="text",
        freshness_suspended=True,
        delivery_declaration=True,
        delivery_evidence_declaration=True,
        delivery_floor_declaration=True,
        presentation_declaration="staged-onboarding-v2")
    return {"continuity": continuity, "budget": budget,
            "freedom": freedom, "batch": batch,
            "journal": journal, "freshness": freshness,
            "freshness_control": freshness_control,
            "staged": staged,
            "staged_gate_files": staged_gate_files,
            "staged_gate_memory": staged_gate_memory,
            "staged_noexample": staged_noexample,
            "directory": directory,
            "evidence_gates": evidence_gates,
            "evidence_listed": evidence_listed,
            "evidence_whole": evidence_whole,
            "length_gate": length_gate,
            "length_order_evidence":
                length_order_evidence,
            "length_order_stage": length_order_stage,
            "pointer": pointer,
            "toolshape": toolshape,
            "toolshape_refused": toolshape_refused}
