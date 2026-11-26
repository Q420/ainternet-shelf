"""The bounded loop — Piece A3 (scope Rev 5, PASSED).

The loop is the piece that turns a generated instance into a
working agent: it repeatedly presents the work to a model
callable and effects what the model returns, until the work
yields, the model declines, or a bound stops it — and every
stop a bound produces is a recorded stop, never a silent one
(R49–R51).

The shape, as the scope settles it:

- The loop is activation-bound. It runs against one standing
  activation of one generated instance, under the instance's
  own credential, and its bounds — a step ceiling and a
  deadline in seconds — live in the issued case the assembly
  record pins. No bounds, no loop: an activation whose pinned
  case carries no bounds is not run, and the refusal happens
  before any model call. The bounds are the pinned version's
  for the whole activation; a later case version's bounds
  govern nothing here. Since INDEX 219 the budget the loop
  supplies governs the callable's calls exclusively — no
  per-call limit at the adapter tightens it either.
- The deadline begins at activation, not at loop start: the
  doorway holds a monotonic anchor established at activation,
  and the loop inherits whatever budget remains. A loop that
  starts late spends the delay; one that starts after expiry
  cannot begin. The activation's remaining budget reaches the
  callable as a call parameter, outside the model-visible
  prompt; the activation deadline is the governing limit and
  any per-call limit is only tighter. Since INDEX 222 the
  loop ALSO propagates the doorway's ABSOLUTE deadline — the
  anchor-derived monotonic instant itself, identical at every
  read — alongside the budget at every invocation: the budget
  is a duration sampled at invocation time and keeps the
  response-acceptance role, but the callable's cancellation
  boundary follows the original point verbatim, never a
  reconstruction that drifts by the sampling-to-invocation
  interval.
- Each iteration runs in an exact order: (i) the bounds and
  deadline are checked; (ii) a package is constructed and
  frozen from a snapshot of the record — the pinned case view
  (the driver's rendering, boundary-narrowed per R11), the
  record delta since the loop's cursor, the settled tool
  results that delta carries (an uncertain outcome presented
  as uncertain, never upgraded), the instance's full standing
  dispatch state, and its bounds state; (iii) the iteration
  is recorded (LOOP_ITERATION, carrying the package's exact
  cursor range) — before the call, so every call, fruitful or
  bare, is accounted; (iv) the callable is invoked with the
  frozen package; (v) the whole response is validated before
  anything is effected — validation is all-or-nothing — and
  adjudication is then per act and per request: a doorway
  refusal of one act or request discards nothing independent
  of it and crashes nothing.
- Responses are terminal-exclusive: a response is proposals
  (record acts and tool requests may mix — they are distinct
  kinds of act, not rival terminals), a yield (a summary
  only), or a decline (a reason only). A combination is
  rejected whole by validation and lands as a
  malformed_response stall.
- A decline is caller-reported: it ends the loop as an
  outcome the caller states, and nothing is recorded for it —
  there is no act to record. A yield likewise ends the loop
  as a caller-reported outcome; the yield ACT — a record
  event with downstream meaning — is Piece A5's and is not
  built here.
- A stall is recorded (LOOP_STALLED) under exactly one
  ground — step_ceiling, deadline, provider_failure,
  malformed_response, runtime_failure — and only after
  in-flight dispatch accounting has closed for the
  activation: every dispatch the loop set in flight holds an
  attributable outcome (an uncertain outcome is accounted,
  not resolved; reconciliation is the examiner's and is never
  waited for). Where the record mechanism itself is
  unavailable, the loop fails closed and does not claim a
  stall was recorded.
- Tool request identity is the loop's, not the model's:
  assigned deterministically (activation, iteration,
  ordinal) and bound to the request's contents at
  presentation, so a replay of a request resolves against
  its standing dispatch and never re-executes (R47/R48).
- Every package carries the worker-facing tool catalogue
  (Piece A3-CAT): derived at construction from the
  instance's own sealed assembly record — the grants the
  doorway enforces — joined with the registry's
  worker-facing descriptions and parameter schemas, so the
  worker is told the exact names, parameters and limits of
  the tools it holds. The catalogue describes authority; it
  creates none. A granted, registered tool the registry
  cannot completely describe fails the package's
  construction closed — an attributable runtime_failure
  stall, no model call — rather than send a worker in with
  its tools unnamed. The iteration event records the
  catalogue's canonical hash and the registry version, and
  the independent checker reconstructs the expected
  catalogue from the sealed grants and its own registry
  copy and compares.
- The retrieval piece (RETRIEVAL-SCOPE Rev 5) rides on the
  assembly's declared contract: an assembly declaring the
  retrieval contract is catalogued under registry v3 (the
  version its iterations record and its dispatches are
  governed by) — per grant, not per tool, so the two
  authority paths' scopes both stand advertised (the
  attempt-7 release correction, INDEX 257) — and its
  retrieval results are carried
  exactly once per package — in tool_results, with their
  provenance — while the delta's rendering of the same
  outcome carries the provenance without the content
  (single carriage, INDEX 249). The record itself retains
  every outcome in full. A result is presented in the one
  package the cursor mechanism already gives it — the first
  package built after it settled — and never re-presented:
  the retention rule is the cursor's, stated explicitly.
  Assemblies declaring anything else keep their catalogue
  version and their outcomes' presentation whole.
- Timing evidence (INDEX 217/219 — Ben's flags): the loop
  measures each iteration's package construction directly,
  times the callable's invocation, and collects the stage
  timings the chain exposes — the adapter's prompt
  rendering and, where the transport provides them, its
  stages — into the result's call_timings, one entry per
  iteration. Stages are measured, never mined from
  iteration timestamps; a stage the chain cannot measure
  stands in the entry as None — unknown, not estimated —
  and a stage the interface cannot separate is labelled
  inseparable in the transport's own data.
- The loop's context is a local object, held for the run and
  dropped at return. Evidenced disposal is Piece A5's; here
  the context simply does not outlive the call.
- The native adapter piece (NATIVE-ADAPTER-SCOPE Rev 3,
  PASSED) adds the second entrance to this same corridor:
  under an assembly judged native, a response's native
  tool calls arrive as per-call extraction records (the
  adapter's native_calls outcome) and run N20's three
  phases here — (i) every individuable call is classified
  in emitted order: call-ID integrity (N6), closed-world
  resolution against THIS package's catalogue (N7), the
  pure schema validation (N8), and the per-response cap
  (N22, CALL_CAP above); (ii) the complete decision set is
  persisted as the translation record — a distinct record
  event bound to the iteration's response-evidence
  artifact hash — before any dispatch, and if it cannot
  be persisted nothing from the response is dispatched;
  (iii) the converted requests are dispatched in emitted
  order through the ordinary adjudication below, so from
  conversion onward a native iteration is indistinguishable
  from its text-mode twin (N9). A refusal at translation
  consumes no dispatch, no grant bound and no step beyond
  its iteration, and is not a stall (N18/N19); refusals
  and outcomes alike are presented in the next package's
  tool-results carriage in provider call order, under the
  provider call ID that proposed them (N24/N26), the
  refusals in the examined N16 error form. The text path
  is untouched: a text-judged assembly's packages and
  requests are exactly as before.

The loop never touches the seat Driver: the Driver's
contract — wake, acknowledge, one response — is a different
shape from an activation's bounded run, and stands unchanged.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import time
from pathlib import Path

from fabric.canonical import canonical, sha256_hex

from . import evidence as _evidence
from . import road as _road
from . import schema_validator as _schema_validator
from . import tool_policy as _tool_policy
from .adapter import AdapterFailure
from .bubble import render_view
from .doorway import (LOOP_ITERATION_DEADLINE_GROUND,
                      DoorwayRefusal)
from .record import EVENT_TYPES, fold

__all__ = ["Loop"]

# The per-response call cap (native adapter piece, N22):
# the largest count of individuable calls one response may
# present to classification and possible dispatch. Its
# value is fixed by the build brief's §3 derivation under
# Ben's ruling (2026-11-24): CAP = 1 — the margin is a
# cushion, not a wall. Calls beyond the cap, in emitted
# order, are refused call_cap_exceeded with their identity
# and ordinal recorded and their arguments never processed.
CALL_CAP = 1

# The translation refusal classes of the native adapter
# piece (§3, with the fifth at N22): a call refused at
# translation is recorded under exactly one of these, in
# its translation record, before any package presents it.
_TRANSLATION_REFUSALS = ("unknown_tool", "malformed_call",
                         "invalid_arguments",
                         "call_cap_exceeded")


def _resolve_against_catalogue(by_name, name):
    """The classification-stage catalogue determination
    (native adapter piece, N7; the examiner's ordering
    ruling, INDEX 408): whether a call's name resolves
    against this package's catalogue, decided from the
    name alone. It stands in _classify_native after
    call-ID integrity (N6) and the per-response cap
    (N22) and before argument parsing (N32) — a call
    refused on either earlier ground never reaches it,
    and for a call that does reach it, no argument work
    precedes the decision. Returns the catalogue entry,
    or None where the name is unknown to the catalogue."""
    return by_name.get(name)


def _parse_arguments_string(raw):
    """The classification-stage parse of a string-form
    arguments value (native adapter piece, build-
    examination correction INDEX 406): the one place the
    loop parses a provider call's arguments. Extraction
    is structural only and parses nothing; this parse is
    reached only by a call that has survived call-ID
    integrity (N6) and the per-response cap (N22) in
    _classify_native, and stands after the catalogue
    determination (N7, INDEX 408) — a call refused on
    either earlier ground never has its arguments
    parsed, so the work the cap bounds is the work
    actually performed. Raises ValueError where the
    string cannot be read as JSON."""
    return json.loads(raw)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


class _CatalogueError(Exception):
    """The tool catalogue for a package cannot be honestly
    derived (Piece A3-CAT): a granted, registered tool whose
    registry entry carries no complete worker-facing layer.
    Raised inside package construction, so the loop's answer
    is its attributable runtime_failure stall — never a
    package that leaves a granted tool unnamed."""


class _EvidenceFailure(Exception):
    """The response-evidence mechanism itself failed for
    an entered iteration (response-evidence piece, R8-2):
    the artifact could not be persisted or read-back-
    verified, or the disposition could not be committed.
    Carries the failed operation (persist / verify /
    commit), which the evidence failure terminal names.

    terminal_recordable (build examination, INDEX 314):
    False where a failed disposition commit could not be
    returned to a known transaction state — the failure
    terminal may not then be attempted, because a partial
    disposition left pending could be committed alongside
    it; the run stops claiming nothing, and CALL_ENTERED
    stands outstanding for the checker."""

    def __init__(self, operation, detail,
                 terminal_recordable=True):
        super().__init__(detail)
        self.operation = operation
        self.detail = detail
        self.terminal_recordable = terminal_recordable


def _derive_catalogue(grants, version=None, per_grant=False):
    """The worker-facing tool catalogue for a sealed grants
    list (Piece A3-CAT): one entry per granted tool — the
    first grant of each tool, as the doorway's own grant
    lookup reads the sealed record — in canonical tool
    order, carrying the grant's own scope ceiling, bound and
    side-effect class copied (advertised limits are the
    grant's values, not a restatement), joined with the
    registry's worker-facing description and parameter
    schema under the current registry version. A grant
    naming an unregistered tool advertises nothing — the
    doorway refuses such tools, and there is nothing lawful
    to describe; the distinction from a registered tool with
    missing metadata stays explicit: that is a registry
    defect and raises _CatalogueError.

    The retrieval piece adds the version parameter: an
    assembly declaring the retrieval contract is catalogued
    under v3 — the version its dispatches are governed by —
    and any other assembly under the current version,
    exactly as before.

    The attempt-7 release correction (INDEX 257, blocker
    1) adds the per_grant parameter, passed only for a
    retrieval-governed assembly: the retrieval regime's two
    authority paths grant the same tools twice — once under
    the sources scope, once under the scratch scope — and
    the doorway enforces both, so a first-grant-only
    catalogue would advertise only one of the two scopes
    the worker actually holds (which one depending on
    sealed order). Under per_grant the derivation emits one
    entry per grant — the tool joined with that grant's own
    ceiling, bound and side-effect class — so both
    authorised scopes stand in the catalogue, in canonical
    tool order (grants of one tool in sealed order, as the
    doorway reads them). Every other assembly keeps the
    first-grant derivation exactly as it stood."""
    if version is None:
        version = _tool_policy.REGISTRY_VERSION
    entries = []
    seen = set()
    for grant in grants or []:
        if not isinstance(grant, dict):
            continue
        tool = grant.get("tool")
        if not isinstance(tool, str) or not tool:
            continue
        if not per_grant:
            if tool in seen:
                continue
            seen.add(tool)
        if not _tool_policy.registered(tool, version):
            continue
        facing = _tool_policy.worker_facing(tool, version)
        if facing is None:
            raise _CatalogueError(
                f"the registry entry for granted tool "
                f"{tool!r} carries no complete worker-facing "
                f"description and parameter schema under "
                f"{version}; the catalogue cannot honestly "
                f"describe the worker's tools (Piece A3-CAT)")
        entries.append({
            "tool": tool,
            "description": facing["description"],
            "parameters": facing["parameters"],
            "scope_ceiling": copy.deepcopy(
                grant.get("scope_ceiling")),
            "bound": copy.deepcopy(grant.get("bound")),
            "side_effect_class":
                grant.get("side_effect_class"),
        })
    entries.sort(key=lambda entry: entry["tool"])
    return entries


def _tool_purpose(tool, description):
    """One line of plain purpose for the wake package's
    tool list (the orientation pass, Ben's rulings on the
    worker consultation, 2026-11-24): the registry
    description's first sentence — except the execution
    tool, whose line also states the first-class fact
    the consultation established was invisible while it
    stood buried in prose: a shell command in his room
    can read a whole file at once."""
    first = (description or "").split(". ")[0].strip()
    if first and not first.endswith("."):
        first += "."
    if tool == "container.exec":
        first = (first + " A shell command there is a "
                 "first-class way to work: cat <path> "
                 "reads a whole file at once, and "
                 "commands can copy, combine and write "
                 "files in your scratch.").strip()
    return first


def _derive_tool_list(catalogue):
    """The wake package's explicit tool list (the
    orientation pass): one entry per catalogue entry —
    the catalogue derives from the sealed grants, so
    the list IS the grant set (names, scopes, count),
    never a hardcoded restatement that could drift from
    it — each entry carrying its grant's scope and a
    one-line purpose in plain words."""
    out = []
    for entry in catalogue or []:
        ceiling = entry.get("scope_ceiling")
        out.append({
            "tool": entry.get("tool"),
            "scope": ceiling.get("path_prefix")
            if isinstance(ceiling, dict) else None,
            "purpose": _tool_purpose(
                entry.get("tool"),
                entry.get("description")),
        })
    return out


def _menu_example(phase, tool, scope):
    """A short example for one tool-menu entry (the
    run-6 package): what a call to this tool looks like
    in the phase it stands in, in the same plain terms
    as the purposes. Illustrative only — the grant set
    and the doorway decide what may actually be called."""
    if tool == "container.exec":
        if phase == "Gather":
            return ("e.g. the command [\"cat\", "
                    "\"<path>\"] reads that whole file "
                    "at once.")
        return ("e.g. commands in your room can copy "
                "and combine files, and write drafts "
                "in your scratch.")
    if tool == "sandbox.write":
        return ("e.g. sandbox.write with a path under "
                "your scratch and the text to store "
                "writes that file.")
    where = f"{scope}/" if scope else ""
    if tool == "sandbox.list":
        return (f"e.g. sandbox.list on {where} lists "
                f"what stands there — each file's size "
                f"and line count.")
    if tool == "sandbox.search":
        return (f"e.g. sandbox.search in {where} for a "
                f"phrase returns the passages that "
                f"carry it, with their file and line "
                f"numbers.")
    if tool == "sandbox.read_range":
        return (f"e.g. sandbox.read_range on a file in "
                f"{where}, lines 1 to 4, pulls just "
                f"those lines.")
    if tool == "sandbox.read":
        return (f"e.g. sandbox.read on a file in "
                f"{where} pulls the whole file at "
                f"once.")
    return None


def _derive_tool_menu(catalogue, deliverable=None):
    """The wake package's tool list as a step-driven
    menu (the run-6 package; the worker's briefcase
    consultation, Q5 — his tools grouped by the job's
    phases, each a card with a label, a description and
    an example): the flat per-grant list grouped under
    Gather, Compose, Deliver, in that order. Grouping
    is presentation only: every entry derives per grant
    from the same flat derivation the tool list has
    always used, no tool is invented and none is
    dropped — the set of (tool, scope) pairs across the
    groups is exactly the sealed grant set. The
    execution tool stands in Gather (a way to read) and
    in Compose (a way to work); the write tool stands
    in Compose and in Deliver, where its entry names
    the deliverable — the case's own deliverable
    statement, where the case carries one — and the
    group names the yield outcome: the assignment
    completes by the deliverable file standing, and
    the yield is how he says so. A phase with no
    granted tool does not stand."""
    flat = _derive_tool_list(catalogue)
    by_pair = {}
    for entry in flat:
        by_pair.setdefault(
            (entry["tool"], entry["scope"]), entry)

    def pick(tool, scope, phase, purpose_suffix=None):
        base = by_pair.get((tool, scope))
        if base is None:
            return None
        entry = {"tool": tool, "scope": scope,
                 "purpose": base["purpose"]}
        if purpose_suffix:
            entry["purpose"] = (
                entry["purpose"] + " " + purpose_suffix)
        example = _menu_example(phase, tool, scope)
        if example:
            entry["example"] = example
        return entry

    gather = []
    compose = []
    deliver = []
    for entry in flat:
        tool, scope = entry["tool"], entry["scope"]
        if tool in _tool_policy.RETRIEVAL_TOOLS or \
                tool == "container.exec":
            picked = pick(tool, scope, "Gather")
            if picked is not None:
                gather.append(picked)
        if tool in ("container.exec", "sandbox.write"):
            picked = pick(tool, scope, "Compose")
            if picked is not None:
                compose.append(picked)
        if tool == "sandbox.write":
            suffix = None
            if deliverable:
                suffix = ("This is the deliverable "
                          f"door: the deliverable is "
                          f"{deliverable}.")
            picked = pick(tool, scope, "Deliver",
                          purpose_suffix=suffix)
            if picked is not None:
                deliver.append(picked)
    groups = []
    if gather:
        groups.append({"phase": "Gather",
                       "tools": gather})
    if compose:
        groups.append({"phase": "Compose",
                       "tools": compose})
    if deliver:
        groups.append({
            "phase": "Deliver",
            "tools": deliver,
            "note": "When the deliverable stands "
                    "written, answer with the yield "
                    "outcome — the file standing is "
                    "the completed assignment."})
    return groups


def _catalogue_hash(catalogue):
    """The catalogue's canonical hash: SHA-256 over the
    fabric canonical form of the catalogue itself — the
    commitment LOOP_ITERATION records (Piece A3-CAT), which
    the checker verifies by independent reconstruction from
    the sealed grants and its own registry copy."""
    return sha256_hex(canonical(catalogue))


# Working-set carriage (the run-3 correction, examiner's
# ruling 2026-11-24): under the working-set contract, a wake
# package presents the successful retrieval material the
# worker has gathered so far in the run — accumulated, not
# latest-only — because the record retaining an outcome is
# not the worker remembering it: run 3's worker re-read two
# sources in alternation to the step ceiling because each
# wake carried only his most recent result. The set is
# derived here from the record's own outcome events, never
# from an in-memory cache, and the iteration records its
# commitment hash for the checker's independent
# reconstruction. The wording the worker reads with it:
WORKING_SET_NOTE = (
    "Your working set: the material you have gathered "
    "with your retrieval tools so far in this run, carried "
    "forward from wake to wake so it stays in front of "
    "you. An entry marked content_carried: false did not "
    "fit the working-set budget; its provenance stands "
    "here and its full content stands in the run's "
    "record — retrieve it again with your retrieval "
    "tools when you need it.")


def _working_set_served(tool, result):
    """The served descriptor of one retrieval result: the
    range or window actually retrieved, in the result's own
    recorded terms — a range read stands as the range it
    served, never expanded into the whole file; a search
    stands by its query and totals, its passages bound by
    their hash (the passages themselves are the entry's
    content)."""
    if tool == "sandbox.read_range":
        return {"kind": "range",
                "start_line": result.get("start_line"),
                "end_line": result.get("end_line"),
                "byte_start": result.get("byte_start"),
                "byte_end": result.get("byte_end"),
                "heading": result.get("heading")}
    if tool == "sandbox.search":
        return {"kind": "search",
                "query": result.get("query"),
                "total_matches": result.get("total_matches"),
                "returned": result.get("returned"),
                "continuation_offset":
                    result.get("continuation_offset"),
                "passages_sha256": sha256_hex(canonical(
                    result.get("passages")))}
    if tool == "sandbox.list":
        return {"kind": "list",
                "size_bytes": result.get("size_bytes"),
                "line_count": result.get("line_count")}
    if tool == "sandbox.read":
        return {"kind": "whole"}
    return {"kind": "result"}


def _derive_working_set(events, dispatches, instance_id,
                        head):
    """The working set a package at `head` presents: every
    successful retrieval outcome of the instance standing in
    the record at or before the head, in outcome order,
    deduplicated on (tool, path, served descriptor, content
    hash) — a repeated read of identical content adds no
    second entry, and the entry keeps the first gathering
    dispatch's identity. Content and provenance travel
    together: each entry carries its source path, authority
    path, content hash and size, the served range or window
    actually retrieved, and its dispatch identity. The
    aggregate content budget (tool_policy) is applied in
    gather order: an entry that fits is carried with its
    content; one that does not fit stands by its provenance
    alone, marked not carried, with the reason named —
    never silently truncated, never pretended present."""
    entries = []
    seen = set()
    remaining = _tool_policy.WORKING_SET_CONTENT_BUDGET
    carried_bytes = 0
    for ev in events:
        if ev["event_seq"] > head or \
                ev["type"] != "TOOL_OUTCOME":
            continue
        payload = ev["payload"]
        if payload.get("outcome") != "result":
            continue
        dispatch = dispatches.get(payload.get("dispatch_id"))
        if dispatch is None or \
                dispatch.get("instance_id") != instance_id:
            continue
        tool = dispatch.get("tool")
        if tool not in _tool_policy.RETRIEVAL_TOOLS:
            continue
        result = payload.get("result")
        if not isinstance(result, dict) or \
                "content" not in result:
            continue
        served = _working_set_served(tool, result)
        key = canonical([tool, result.get("path"), served,
                         result.get("content_sha256")])
        if key in seen:
            continue
        seen.add(key)
        size = result.get("content_bytes")
        if not isinstance(size, int) or \
                isinstance(size, bool):
            size = len(result["content"].encode("utf-8"))
        entry = {
            "tool": tool,
            "path": result.get("path"),
            "authority_path": result.get("authority_path"),
            "content_sha256": result.get("content_sha256"),
            "content_bytes": size,
            "served": served,
            "dispatch_id": payload.get("dispatch_id"),
            "request_id": payload.get("request_id"),
            "outcome_event_seq": ev["event_seq"],
        }
        if size <= remaining:
            entry["content"] = result["content"]
            entry["content_carried"] = True
            remaining -= size
            carried_bytes += size
        else:
            entry["content_carried"] = False
            entry["not_carried_reason"] = \
                "working_set_budget"
        entries.append(entry)
    return {
        "budget_bytes":
            _tool_policy.WORKING_SET_CONTENT_BUDGET,
        "content_bytes": carried_bytes,
        "note": WORKING_SET_NOTE,
        "entries": entries,
    }


def _working_set_hash(working_set):
    """The working set's commitment: SHA-256 over the
    canonical form of its budget and entries — the
    commitment LOOP_ITERATION records for an assembly under
    the working-set contract, which the checker verifies by
    independent reconstruction from the recorded outcomes.
    The note is package wording, not committed content."""
    return sha256_hex(canonical({
        "budget_bytes": working_set["budget_bytes"],
        "entries": working_set["entries"]}))


def _pointer_line_count(entry, outcome_result):
    """A pointer entry's line count, where the record
    knows one: the served descriptor's own line count
    where it carries one (a listing names its file's
    lines); a served range's span where the descriptor
    names its lines; otherwise the recorded content's
    own lines. None where the record knows none — the
    pointer then stands without the field."""
    served = entry.get("served")
    if isinstance(served, dict):
        line_count = served.get("line_count")
        if isinstance(line_count, int):
            return line_count
        start = served.get("start_line")
        end = served.get("end_line")
        if isinstance(start, int) and isinstance(end, int):
            return end - start + 1
    if isinstance(outcome_result, dict):
        content = outcome_result.get("content")
        if isinstance(content, str):
            return len(content.splitlines())
    return None


def _presented_working_set_pointers(working_set, events,
                                    assembly_id, catalogue):
    """The working set's pointer presentation (INDEX
    568, the pointer rule applied to the set itself):
    the record-side set rendered for a wake under the
    successor contract. Each entry stands as a pointer
    — its address and authority path, the tool that
    gathered it and the step it was gathered at (the
    iteration whose outcomes precede it in the record),
    its size in bytes and lines where the record knows
    them, its content hash, its served descriptor, its
    dispatch and outcome identity, its content_carried
    standing (and the reason where it did not carry),
    the access call that pulls it again where a granted
    call covers the address, and one plain sentence
    naming the room, the address and the standing of
    the office's record. No entry's content stands
    here: content is presented exactly once, in the
    first wake after the gather, as part of that wake's
    newest results. The component's budget and content
    figures keep their record meanings — they are the
    office's carriage accounting for the set the
    iteration's working_set_hash commits, not a claim
    about this package's size. A pure function of the
    record-side set, the record and the catalogue; the
    checker's own copy derives the same form whole."""
    outcomes = {}
    steps = {}
    for ev in events:
        payload = ev.get("payload") or {}
        if ev.get("type") == "TOOL_OUTCOME":
            outcomes[ev.get("event_seq")] = payload
        elif ev.get("type") == "LOOP_ITERATION" \
                and payload.get("assembly_id") == assembly_id \
                and isinstance(payload.get("iteration"), int):
            steps[ev.get("event_seq")] = payload["iteration"]
    entries = []
    for entry in working_set["entries"]:
        outcome = outcomes.get(entry["outcome_event_seq"]) or {}
        gathered_step = 0
        for seq, iteration in steps.items():
            if isinstance(seq, int) \
                    and seq < entry["outcome_event_seq"] \
                    and iteration > gathered_step:
                gathered_step = iteration
        pointer = {
            "tool": entry["tool"],
            "path": entry["path"],
            "authority_path": entry["authority_path"],
            "content_sha256": entry["content_sha256"],
            "content_bytes": entry["content_bytes"],
        }
        line_count = _pointer_line_count(
            entry, outcome.get("result"))
        if line_count is not None:
            pointer["line_count"] = line_count
        pointer["served"] = copy.deepcopy(entry["served"])
        pointer["dispatch_id"] = entry["dispatch_id"]
        pointer["request_id"] = entry["request_id"]
        pointer["outcome_event_seq"] = \
            entry["outcome_event_seq"]
        pointer["gathered_step"] = gathered_step
        pointer["content_carried"] = entry["content_carried"]
        if "not_carried_reason" in entry:
            pointer["not_carried_reason"] = \
                entry["not_carried_reason"]
        way = _staged_access_way(catalogue, entry["path"])
        if way is not None:
            pointer["access"] = way
            pointer["note"] = STAGED_POINTER_SENTENCE.format(
                path=entry["path"], tool=way["tool"])
        else:
            pointer["note"] = \
                STAGED_POINTER_SENTENCE_NO_WAY.format(
                    path=entry["path"])
        entries.append(pointer)
    return {
        "budget_bytes": working_set["budget_bytes"],
        "content_bytes": working_set["content_bytes"],
        "note": WORKING_SET_POINTER_NOTE,
        "entries": entries,
    }


def _carriage_stub(result, presented_in):
    """The single-carriage stub of a retrieval result: the
    provenance stands (path, authority path, content hash
    and size, served range or window, search totals); the
    content-bearing fields are replaced by the marker
    naming where the content is presented."""
    stub = {key: value for key, value in result.items()
            if key not in ("content", "passages",
                           "headings")}
    stub["single_carriage"] = True
    stub["presented_in"] = presented_in
    return stub


# Staged onboarding (INDEX 544, Ben's direction,
# 2026-11-25): under the sealed presentation contract the
# wake package stops carrying the whole briefcase at once.
# The finding it answers (INDEX 542/543): the package
# carried the sealed case verbatim AND the labelled
# components built on top of it — the same content twice,
# ~49 KB on the wire before the worker could look out the
# window — and what was carried unlabelled stood as
# scenery. So the onboarding walks in stages across the
# first wakes, each stage introduced in plain words:
# (1) a short cover and his memory, alone, framed as his
# own knowledge; (2) his case's essentials — the frame,
# the evidence boundary, the delivery declaration, the
# freshness position, and the opening record where one
# stands; (3) his files as pointers — the briefcase's map
# and his journal's designation, never contents — with
# his tools offered from this wake on, so the files stage
# is a real pull: he can list the briefcase himself and
# see it standing; (4) his task — the assignment text and
# the phase-grouped tool menu — where the work begins.
# After onboarding, a dashboard wake: the cover line, his
# position, the newest results, the working set, any gate
# correction, and pointers back into the briefcase he can
# pull from as he works. The verbatim case dump, the view
# and the delta leave his packages entirely in this
# population, and no content item stands twice in any
# package. The stage a wake presents is a pure function
# of its iteration number; every value in a staged package
# derives from the record (the pinned case, the sealed
# declarations, the recorded outcomes), so the iteration
# record's presentation hash commits the exact structure
# and the checker re-derives it whole. The wording below
# is the presentation's own; the checker's copies stand in
# checker.py, as its other copies do.
STAGED_COVER_FIRST = (
    "You are {seat}, the {role} in this office, "
    "assembled for one job. The shape of the work here "
    "is simple: you are woken with a package, you act, "
    "and the record keeps everything. Your onboarding "
    "comes in stages — first your memory, then your "
    "case, then your files, then your task — so nothing "
    "is dumped on you all at once. The job: {headline}. "
    "The deliverable: {deliverable}.")
STAGED_MEMORY_INTRO = (
    "This is your memory — what this role knows from "
    "before you were woken: how the work has gone, what "
    "the office has told you, and the routes to what you "
    "need. It is presented to you as your own knowledge "
    "because in this role it is yours to work from; the "
    "office keeps its own honest account of where each "
    "item came from, behind the scenes. If the list "
    "below is empty, this role carries no standing "
    "memory yet.")
STAGED_FILES_INTRO = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is "
    "carried forward in front of you at later wakes, "
    "so you never need to pull the same thing twice. "
    "Your tools are offered from this wake on. Below "
    "the map, one call stands worked as an example — "
    "a real call the office made on the first file "
    "while your briefcase was being stocked, with "
    "what came back; yours will look like this.")
STAGED_FILES_INTRO_NO_EXAMPLE = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is "
    "carried forward in front of you at later wakes, "
    "so you never need to pull the same thing twice. "
    "Your tools are offered from this wake on — if "
    "you want, list a file from the map now and see "
    "its shape standing.")
STAGED_EXAMPLE_LABEL = (
    "A worked example — the office's own call, made "
    "while your briefcase was stocked: a real call, "
    "and what came back. It is an example of your "
    "next move, not your work and not material you "
    "have gathered; the file's contents are still "
    "yours to pull.")
# The room-proof line (the calibration, from the
# GPT-OSS worker's debrief): one line standing beside
# the worked example under the pointer-rule contract,
# answering the doubt his testimony named — that the
# JSON door might be "just a protocol" over some
# other real engine. The example is a real call the
# office made in his room, through the same performer
# his own calls run; his tools answer the same way
# when he calls them in the shape shown.
STAGED_EXAMPLE_PROOF = (
    "This example is a real call the office made in "
    "your room, on a file from your own briefcase; "
    "your tools answer the same way when you call "
    "them in the shape shown.")
STAGED_SNAPSHOT_NOTE = (
    "Where you stand: before you were woken, an "
    "opening conversation settled what stands below. "
    "It is recorded work state — what was settled "
    "before you arrived — not your memory; your "
    "memory follows it.")
STAGED_SNAPSHOT_EMPTY = (
    "Where you stand: nothing was settled before "
    "this wake — no settled results of an opening "
    "conversation stand in your case. What precedes "
    "you is this role's standing memory, below.")
STAGED_STAGE_GATE_INSTRUCTION = (
    "Nothing was filed. Delivery opens with your "
    "task: your task has not been presented yet — "
    "it arrives at the fourth wake of your "
    "onboarding (stage 4: your task), and from "
    "that wake on your contribution is the "
    "deliverable's arrival and the office files "
    "it. What is needed until then is the work "
    "itself: walk the stages as they come, pull "
    "what your task needs, and contribute once "
    "your task stands in front of you. The text "
    "you sent stands in the record, set aside "
    "unfiled; if it is the brief you mean to "
    "deliver, send it again after your task has "
    "been presented.")
STAGED_JOURNAL_POINTER = (
    "your journal — your notebook: notes, decisions, "
    "where you left off. Yours to write and rewrite; "
    "orientation, not record and not memory. Its "
    "contents are not carried in your packages — pull "
    "it when you want it.")
# The journal's contract under the pointer-rule
# successor (the calibration, from the GPT-OSS
# worker's debrief): the same pointer, with the
# directive he asked for stated in it — what to log
# and when, in what shape; why (the office reads the
# journal at every wake when it builds his package —
# the journal component reads it from its resting
# place each time — and the director may audit it);
# and the truth that nothing parses it: it is read as
# he wrote it, never checked or scored. The first
# contract's note stands exactly as it stood.
STAGED_JOURNAL_POINTER_V2 = (
    "your journal — your notebook: notes, decisions, "
    "where you left off. Yours to write and rewrite; "
    "orientation, not record and not memory. Keep it "
    "as you work: after each file you read, log its "
    "name and the key points you took from it, in "
    "one or two plain lines. The office reads your "
    "journal at every wake to resume you, and the "
    "director may audit it; nothing parses it — it "
    "is read as you wrote it. Its contents are not "
    "carried in your packages — pull it when you "
    "want it.")
# The delivery-evidence gate (round ten, INDEX 552):
# where the case declares the evidence a delivery must
# rest on, a contribution offered before that evidence
# stands gathered is set aside unfiled and answered with
# this correction — in the INDEX 475 shape the other
# gates use: what arrived, what is missing (each address
# named, with its way in, as the files stage states
# them), and the route onward. The wording is a pure
# function of the gate event's own payload and the
# catalogue, so the checker re-derives it byte-exact
# from the record; its copy stands in checker.py.
STAGED_EVIDENCE_GATE_WHAT_ARRIVED = (
    "a contribution, offered as your delivery, before "
    "the evidence your case names for a delivery stood "
    "gathered in front of you")
STAGED_EVIDENCE_GATE_INSTRUCTION_HEAD = (
    "Nothing was filed. Your case names the evidence "
    "a delivery must rest on: the whole content of "
    "each named file must stand gathered in your "
    "working set before your contribution can be "
    "filed as the deliverable. Still missing:")
STAGED_EVIDENCE_GATE_INSTRUCTION_TAIL = (
    "Gather what is missing, then offer your "
    "contribution again. Listing a file shows its "
    "shape, not its contents — a listing does not "
    "gather it; pull the whole file, or pull ranges "
    "that together cover the whole file. The text "
    "you sent stands in the record, set aside "
    "unfiled.")


def _evidence_gate_instruction(catalogue, missing):
    """The evidence gate correction's instruction: the
    fixed head, one line per missing address naming its
    way in (the files stage's own access way for that
    address, from the catalogue), and the fixed tail. A
    pure function of the missing list and the catalogue,
    so the loop's package and the checker's re-derivation
    agree byte for byte."""
    lines = [STAGED_EVIDENCE_GATE_INSTRUCTION_HEAD]
    for address in missing:
        way = _staged_access_way(catalogue, address)
        if way is not None:
            lines.append(
                f"- {address}: {way['tool']} on {address} "
                f"pulls the whole file.")
        else:
            lines.append(
                f"- {address}: no tool you hold reaches "
                f"it — say so in your yield, and the "
                f"office will stock a route.")
    lines.append(STAGED_EVIDENCE_GATE_INSTRUCTION_TAIL)
    return "\n".join(lines)


def _evidence_gate_correction(catalogue, contribution_seq,
                              text_sha256, missing):
    """The correction a delivery-evidence gate leaves for
    the next wake's package, derived from the gate
    event's facts: what arrived, the contribution it
    names, what is missing, and the instruction."""
    return {
        "what_arrived": STAGED_EVIDENCE_GATE_WHAT_ARRIVED,
        "contribution_seq": contribution_seq,
        "text_sha256": text_sha256,
        "missing": list(missing),
        "instruction": _evidence_gate_instruction(
            catalogue, missing)}


# The delivery-length gate's texts (the third gate,
# INDEX 557): what arrived names the count the
# contribution arrived with; the instruction names
# what is needed — the floor the case declares, with
# the target standing where the job sets it — and what
# to do. Both are pure functions of the gate event's
# own payload, so the checker re-derives them
# byte-exact from the record; its copies stand in
# checker.py. The task stage's floor statement is the
# same shape: the floor drawn in his task before it
# can bite, as the evidence gate's edge is drawn by
# the case that names it.
def _length_gate_what_arrived(word_count):
    return (f"a contribution of {word_count} words, "
            f"offered as your delivery")


STAGED_LENGTH_GATE_INSTRUCTION = (
    "Nothing was filed. Your contribution arrived at "
    "{word_count} words; the deliverable must run to "
    "at least {min_words} words — the target stands "
    "at about 600 words, and the floor is a minimum, "
    "not the aim. Write to the full length from the "
    "sources you have gathered, then offer your "
    "contribution again. The text you sent stands in "
    "the record, set aside unfiled.")
STAGED_TASK_FLOOR_STATEMENT = (
    "The deliverable must run to at least {min_words} "
    "words. A contribution shorter than that is set "
    "aside unfiled, and you will be told the count "
    "yours arrived with.")
# The task stage's deliverable statement under the
# pointer-rule successor (the calibration, from the
# GPT-OSS worker's debrief): the figures stand where
# he plans, before any refusal can — the target the
# job sets and the floor the door enforces, in one
# statement. He had compressed "short" to under 250
# words; the number was in his case all along, but
# never where he formed his plan. The first
# contract's statement stands exactly as it stood.
STAGED_TASK_FLOOR_STATEMENT_V2 = (
    "The brief runs to about 600 words, and the "
    "door will not file a brief under {min_words} "
    "words. A contribution shorter than that is set "
    "aside unfiled, and you will be told the count "
    "yours arrived with.")


def _length_gate_correction(contribution_seq,
                            text_sha256, word_count,
                            min_words):
    """The correction a delivery-length gate leaves
    for the next wake's package, derived from the gate
    event's facts: what arrived (with its count), the
    contribution it names, the count and the floor,
    and the instruction."""
    return {
        "what_arrived": _length_gate_what_arrived(
            word_count),
        "contribution_seq": contribution_seq,
        "text_sha256": text_sha256,
        "word_count": word_count,
        "min_words": min_words,
        "instruction": STAGED_LENGTH_GATE_INSTRUCTION
        .format(word_count=word_count,
                min_words=min_words)}


# The tool-shape gate's texts (the calibration, from
# the GPT-OSS worker's debrief): where the provider
# refuses a generation for the tool-use shape — the
# worker reached for a tool natively in a room whose
# tools are called in the text shape, and the
# provider refused the whole answer — the refusal is
# a gate under Ben's ruling (INDEX 475), answered
# with a correction in the family's shape: what
# arrived (the native call, named), what is needed
# (the text shape), one concrete well-formed example,
# and the instruction. Both texts are pure functions
# of the gate event's facts and the case's first
# glossary address, so the checker re-derives the
# correction byte-exact from the record; its copies
# stand in checker.py.
def _tool_shape_what_arrived(tool_name):
    return (f"a native tool call — your answer named "
            f"{tool_name} in the provider's own "
            f"tool-call shape, and the provider refused "
            f"the whole answer for it (its refusal "
            f"carries the code tool_use_failed). No "
            f"tool ran, and nothing from that answer "
            f"was carried out")


TOOL_SHAPE_GATE_WHAT_IS_NEEDED = (
    "In this room your tools are called in the text "
    "shape: your answer is one JSON object whose "
    "outcome is \"tool_requests\", with a requests "
    "list naming each call — the tool's name and its "
    "parameters — as the example shows. Only calls "
    "in that shape reach your tools; a native tool "
    "call cannot be carried out here.")
TOOL_SHAPE_GATE_INSTRUCTION = (
    "Nothing was filed, and nothing was lost: your "
    "gathered work stands as it stood. Make the call "
    "again in the text shape and carry on with the "
    "job. The refusal cost this one step and nothing "
    "else.")


def _tool_shape_gate_correction(tool_name,
                                example_address):
    """The correction a tool-shape gate leaves for the
    next wake's package, derived from the gate event's
    facts: what arrived (the native call, named), what
    is needed (the text shape), one concrete
    well-formed tool_requests example — a read of the
    case's first glossary file — and the instruction."""
    return {
        "what_arrived": _tool_shape_what_arrived(
            tool_name),
        "what_is_needed": TOOL_SHAPE_GATE_WHAT_IS_NEEDED,
        "example": {
            "outcome": "tool_requests",
            "requests": [{
                "tool": "sandbox.read",
                "parameters": {"path": example_address}}]},
        "instruction": TOOL_SHAPE_GATE_INSTRUCTION}


def _tool_shape_failure(failure, seam):
    """The tool-shape refusal's facts, where this
    provider failure is one (the calibration): the
    provider refused the generation for the tool-use
    shape — an HTTP 400 (or a seam that observed no
    status) whose error body carries the code
    tool_use_failed (or the refusal's own words, that
    a tool was called while the tool choice is none)
    and preserves the failed generation, which parses
    to a call naming its tool. Returns the facts the
    gate event records, or None where the failure is
    any other kind — rate limits, byte ceilings,
    timeouts and server errors are not this gate's
    business and stall as provider failures exactly
    as they always have. The body is read from the
    seam's own captured bytes, the same evidence the
    disposition settled."""
    if failure.kind != "provider_error":
        return None
    if not isinstance(seam, dict):
        return None
    status = seam.get("http_status")
    if status is not None and status != 400:
        return None
    body = seam.get("l1_bytes")
    if isinstance(body, (bytes, bytearray)):
        try:
            body = bytes(body).decode("utf-8")
        except UnicodeDecodeError:
            return None
    if not isinstance(body, str):
        return None
    try:
        parsed = json.loads(body)
    except ValueError:
        return None
    error = parsed.get("error") \
        if isinstance(parsed, dict) else None
    if not isinstance(error, dict):
        return None
    code = error.get("code")
    message = error.get("message")
    if code != "tool_use_failed" and not (
            isinstance(message, str)
            and "model called a tool" in message):
        return None
    failed = error.get("failed_generation")
    if not isinstance(failed, str) or not failed:
        return None
    try:
        generation = json.loads(failed)
    except ValueError:
        return None
    name = generation.get("name") \
        if isinstance(generation, dict) else None
    if not isinstance(name, str) or not name:
        return None
    return {
        "http_status": status,
        "error_code": code
        if isinstance(code, str) else "tool_use_failed",
        "error_message": message
        if isinstance(message, str) else "",
        "tool_name": name,
        "failed_generation": failed}


def _evidence_address_stands(entries, requested, address):
    """Whether one named address's whole content stands
    in the working set, from the set's entries and the
    record's requested parameters alone (round ten,
    INDEX 552). An address stands where a whole-file
    read of it stands carried, or where carried line
    ranges together cover the file's whole line range.
    The whole line range is itself a record fact,
    established one of two ways: a listing outcome for
    the address recording its line count, or a range
    request whose asked end_line the performer clamped
    — the performer clamps only at the file's end, so
    the served end of a clamped range IS the file's
    last line. A byte-window range never counts (a
    window of one line is not the line's whole content,
    and the record cannot show the window spans the
    line); a listing or a search never counts as
    content (shape is not substance); an entry standing
    by provenance alone, its content not carried, never
    counts — the content does not stand in front of the
    worker. container.exec outcomes never enter the
    working set at all — the execution tool is not a
    retrieval tool, and its room result is stdout
    carrying no recorded binding to a path — so no exec
    carriage can stand here: the record cannot attribute
    it, and the gate does not invent attribution."""
    mine = [e for e in entries
            if e.get("path") == address]
    for entry in mine:
        if entry.get("tool") == "sandbox.read" and \
                entry.get("content_carried"):
            return True
    total = None
    for entry in mine:
        if entry.get("tool") == "sandbox.list":
            line_count = (entry.get("served") or {}).get(
                "line_count")
            if isinstance(line_count, int) and \
                    not isinstance(line_count, bool):
                total = line_count
    intervals = []
    for entry in mine:
        if entry.get("tool") != "sandbox.read_range" or \
                not entry.get("content_carried"):
            continue
        served = entry.get("served") or {}
        if served.get("byte_start") is not None:
            continue
        start = served.get("start_line")
        end = served.get("end_line")
        if not isinstance(start, int) or \
                isinstance(start, bool) or \
                not isinstance(end, int) or \
                isinstance(end, bool):
            continue
        intervals.append((start, end))
        if total is None:
            asked = (requested.get(
                entry.get("request_id")) or {}).get(
                    "end_line")
            if isinstance(asked, int) and \
                    not isinstance(asked, bool) and \
                    asked > end:
                total = end
    if total is None or total < 1 or not intervals:
        return False
    covered_to = 0
    for start, end in sorted(intervals):
        if start > covered_to + 1:
            return False
        covered_to = max(covered_to, end)
        if covered_to >= total:
            return True
    return covered_to >= total


def _delivery_evidence_missing(events, dispatches,
                               instance_id, head,
                               addresses, block_map=None):
    """The declared delivery evidence that does not
    stand at `head`, in the declaration's own order:
    the working set is derived at the head from the
    record, and each named address is weighed by
    _evidence_address_stands. The requested parameters
    the computation reads stand in the record's
    TOOL_REQUESTED events, keyed by request identity —
    the computation is reconstructible from the recorded
    dispatches and outcomes alone, and the checker
    derives the same list from its own copies.

    Under the office-cycle contract (a sealed block
    map given), an address also stands where every
    sealed block of that address stands carried under
    the block rule: the cycle walk gathers a file
    block by block, in exact ranges, and that coverage
    is the file's evidence — the standing computation
    alone cannot see it, because an exact range read
    never establishes the file's total line count."""
    working_set = _derive_working_set(
        events, dispatches, instance_id, head)
    requested = {}
    for ev in events:
        if ev["event_seq"] > head or \
                ev["type"] != "TOOL_REQUESTED":
            continue
        payload = ev["payload"]
        parameters = payload.get("parameters")
        if isinstance(parameters, dict):
            requested[payload.get("request_id")] = parameters
    entries = working_set["entries"]

    def stands(address):
        if _evidence_address_stands(
                entries, requested, address):
            return True
        if block_map is not None:
            mine = [block for block in block_map
                    if block.get("address") == address]
            if mine and all(
                    _block_read_facts(entries, block)[0]
                    for block in mine):
                return True
        return False

    return [address for address in addresses
            if not stands(address)]


def _missing_blocks(events, dispatches, instance_id,
                    head, block_map, addresses):
    """The sealed blocks of the named addresses whose
    read does not stand carried at `head`, in map
    order, as {block_id, address} pairs — the cycle
    contract's delivery corrections name incomplete
    cycles explicitly, as blocks mapped to their
    files (the plan §7)."""
    if block_map is None:
        return []
    working_set = _derive_working_set(
        events, dispatches, instance_id, head)
    entries = working_set["entries"]
    return [{"block_id": block["block_id"],
             "address": block["address"]}
            for block in block_map
            if block.get("address") in addresses
            and not _block_read_facts(entries, block)[0]]


# ------------------------------------------------------------
# The process-tree contract (the room rebuild, Ben's
# "Make it so" 2026-11-25 15:02 MST; presentation
# contract process-tree-v1). One opening package — no
# staged acknowledge wakes — then one package per step
# of the office-authored tree sealed in the case:
# ORIENT → one GATHER step per declared source, in
# declaration order → COMPOSE → DELIVER, root the brief
# filed at the delivery destination. Every value in a
# tree package derives from the record alone — the
# pinned case's components, the sealed declarations,
# the recorded outcomes — so the checker re-derives the
# package whole, exactly as it re-derives the staged
# contracts'. The wording below is the presentation's
# own; the checker's copies stand in checker.py.
TREE_COVER_FIRST = (
    "You are {seat}, the {role} in this office, "
    "assembled for one job. The shape of the work here "
    "is simple: you are woken with a package, you act, "
    "and the record keeps everything. This package is "
    "your whole opening — your memory, your case, your "
    "files, your tools and your journal, all of it once "
    "— and the process tree below walks the job step by "
    "step from here: one step in front of you at a "
    "time, each step's content presented at its step "
    "and never twice. Nothing needs acknowledging; "
    "your first answer is work. The job: {headline}. "
    "The deliverable: {deliverable}.")
TREE_DIRECTION_OPENING = (
    "Your opening package: everything in it is "
    "presented once, here — your memory, the process "
    "tree that walks this job, your case's essentials, "
    "your files with their ways in, your tool "
    "catalogue, and your journal with its contract. "
    "Begin work in your first answer.")
TREE_DIRECTION_STEP = (
    "A step package: the tree as it stands, your "
    "current step spelled out, your journal as you "
    "left it, and at most this step's fresh content — "
    "presented once, at its step. Everything else "
    "stands as pointers.")
TREE_FILES_INTRO = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The tree walks them one "
    "at a time: when a file's gather step is current, "
    "read it whole, and its content is presented to "
    "you at that step, once. What you pull is yours "
    "from your room at any time — the tree governs "
    "what stands in front of you, not what you may "
    "reach for.")
# The journal's contract under the tree contract: the
# calibration's contract text, with the carriage truth
# of this contract — under the tree the journal rides
# in every package verbatim, exactly as he left it,
# because the journal is the method: the brief is
# compiled from its entries at COMPOSE.
TREE_JOURNAL_LABEL = (
    "your journal — your notebook: notes, decisions, "
    "where you left off. Yours to write and rewrite; "
    "orientation, not record and not memory. Keep it "
    "as you work: after each file you read, log its "
    "name and the key points you took from it, in "
    "one or two plain lines. The office reads your "
    "journal at every wake to resume you, and the "
    "director may audit it; nothing parses it — it "
    "is read as you wrote it. It rides in every "
    "package, exactly as you left it, below.")
TREE_COMPOSE_POINTS = [
    "what this framework is",
    "what has actually been proven",
    "what has not been proven",
    "what remains to be built"]
TREE_COMPOSE_INSTRUCTION = (
    "Compile the brief from your journal entries — "
    "the bits you logged at each gather step are the "
    "brief's substance, in your own words. Your "
    "journal stands above, verbatim. Cover the four "
    "points: what this framework is; what has "
    "actually been proven; what has not been proven; "
    "what remains to be built. Stay accurate to what "
    "you gathered; invent nothing; where the sources "
    "disagree with each other, say so. Pull a source "
    "again only if a gap shows in your entries — its "
    "pointer stands in your working set. When the "
    "brief is ready, move to DELIVER: your "
    "contribution is the delivery.")
TREE_DELIVER_INSTRUCTION = (
    "Deliver now: answer with outcome \"contribute\" "
    "and the brief's text as its text. The "
    "contribution is the delivery — the office files "
    "it at {destination}. The standing gates "
    "adjudicate it as they stand: the evidence (every "
    "gather step's source read and standing in the "
    "record) and the length floor the figures name. "
    "Nothing else is asked of you at this step.")
TREE_DELIVER_AGAIN_INSTRUCTION = (
    "A contribution stands in the record, set aside "
    "unfiled by a gate — its correction stands in "
    "this package. Deliver again: answer with outcome "
    "\"contribute\" and the brief's text as its text. "
    "The contribution is the delivery — the office "
    "files it at {destination}.")
TREE_ORIENT_INSTRUCTION = (
    "Take this opening in — it is the whole of it, "
    "and nothing in it will be presented again. Your "
    "first step is the tree's first gather step: "
    "read {address} whole, then log its journal "
    "bits. You may begin that work in your first "
    "answer; no acknowledgement is asked or needed.")
TREE_GATHER_INSTRUCTION = (
    "Read {address} whole: {tool} on {address} pulls "
    "the whole file. Read it, don't list it — a "
    "listing gives you its shape, not its words. "
    "Then log the journal bits for this file: a "
    "sandbox.write to {journal} carrying your "
    "journal as it stands plus one or two plain "
    "lines naming this file and the key points you "
    "took from it. When the read stands carried and "
    "the journal bits stand after it, this step is "
    "done and the tree moves on.")
TREE_GATHER_READ_STANDS_INSTRUCTION = (
    "{address} stands read — its content is in front "
    "of you at this step, once. What this step still "
    "needs is the journal move: a sandbox.write to "
    "{journal} carrying your journal as it stands "
    "plus one or two plain lines naming this file "
    "and the key points you took from it. When the "
    "journal bits stand after the read, this step is "
    "done and the tree moves on.")
# The step gate's texts (the room rebuild): where the
# current GATHER step stands incomplete at a wake and
# the record shows it partly done or work standing
# ahead of it, the wake's package carries this
# correction, in the INDEX 475 shape the family's
# gates use — what arrived, what the step still
# needs, and the instruction. Both texts are pure
# functions of the gate event's own payload, so the
# checker re-derives them byte-exact from the record;
# its copies stand in checker.py.
def _step_gate_what_arrived(missing, address,
                            ahead_address):
    if "read" in missing:
        return (f"work ahead of the tree — "
                f"{ahead_address} stands gathered — "
                f"while this step's file, {address}, "
                f"has not been read")
    if ahead_address is not None:
        return (f"your read of {address} — the whole "
                f"file stands gathered in the record — "
                f"and work ahead of the tree: "
                f"{ahead_address} stands gathered too, "
                f"before this step completed")
    return (f"your read of {address} — the whole file "
            f"stands gathered in the record")


STEP_GATE_INSTRUCTION = (
    "Nothing was refused, and nothing is lost: every "
    "call you made stands executed in the record. "
    "Presentation walks the tree one step at a time, "
    "and this step is still current — it completes "
    "when {needs}. Then the tree moves on and the "
    "next step's content stands in front of you. "
    "Work already gathered for later steps stands in "
    "the record and will be presented at its step, "
    "once; you do not need to pull it again.")


def _step_gate_needs(missing, address, journal_path):
    parts = []
    if "read" in missing:
        parts.append(
            f"the read of {address} stands carried "
            f"(read the file whole — a listing gives "
            f"its shape, not its words)")
    if "journal" in missing:
        parts.append(
            f"the journal bits for {address} stand "
            f"in {journal_path} after that read (one "
            f"or two plain lines naming the file and "
            f"the key points you took from it)")
    return " and ".join(parts)


def _step_gate_correction(step, address, missing,
                          ahead_address, journal_path):
    """The correction a step gate leaves for the
    wake's package, derived from the gate event's
    facts: what arrived, the step it names, what the
    step still needs, and the instruction."""
    return {
        "what_arrived": _step_gate_what_arrived(
            missing, address, ahead_address),
        "step": step,
        "address": address,
        "missing": list(missing),
        "instruction": STEP_GATE_INSTRUCTION.format(
            needs=_step_gate_needs(
                missing, address, journal_path))}


# The stage gate's texts under the tree contract: the
# contribution door opens at DELIVER, and a
# contribution offered while the tree stands at an
# earlier step is set aside unfiled and answered with
# this correction — the stage gate's function, in the
# tree's own words. Pure functions of the gate
# event's payload, as the family's are.
def _tree_stage_gate_what_arrived(stage):
    if stage.startswith("gather:"):
        return (f"a contribution, offered while the "
                f"tree stood at the gather step for "
                f"{stage[len('gather:'):]}, before "
                f"the tree reached the delivery step")
    return (f"a contribution, offered while the tree "
            f"stood at the {stage} step, before the "
            f"tree reached the delivery step")


TREE_STAGE_GATE_INSTRUCTION = (
    "Nothing was filed. The contribution door opens "
    "when the tree reaches DELIVER: walk the steps — "
    "read each file the tree names whole, log its "
    "journal bits, and the tree moves on; at COMPOSE "
    "you compile the brief from your journal "
    "entries, and at DELIVER your contribution is "
    "the delivery and the office files it. The text "
    "you sent stands in the record, set aside "
    "unfiled; if it is the brief you mean to "
    "deliver, send it again when the tree reaches "
    "DELIVER.")


def _cycle_stage_gate_what_arrived(stage):
    return (f"a contribution, offered while the walk "
            f"stood at {stage}, before every cycle "
            f"stood complete")


def _cycle_stage_gate_what_arrived_v8(stage):
    return (f"a contribution, offered while the walk "
            f"stood at {stage}, before every file "
            f"stood complete")


# The file-grain successor's stage-gate instruction
# (office-cycle-v8): the standing instruction in
# the job's own units — the door opens when every
# FILE stands complete, and the files still
# incomplete stand named below, as files.
CYCLE_STAGE_GATE_INSTRUCTION_V8 = (
    "Nothing was filed. The contribution door opens "
    "when every file stands complete and the walk "
    "reaches SUMMARIZE: walk the files — read each "
    "file, append your summary of it to your "
    "journal — and at SUMMARIZE you read your "
    "journal whole, assemble the brief from it, and "
    "your contribution is the delivery and the "
    "office files it. The files still incomplete "
    "stand named below. The text you sent stands in "
    "the record, set aside unfiled; if it is the "
    "brief you mean to deliver, send it again at "
    "SUMMARIZE.")


CYCLE_STAGE_GATE_INSTRUCTION = (
    "Nothing was filed. The contribution door opens "
    "when every cycle stands complete and the walk "
    "reaches SUMMARIZE: walk the cycles — pull each "
    "block at its cycle, read it, append its bits to "
    "your journal — and at SUMMARIZE you read your "
    "journal whole, compile the brief from it, and "
    "your contribution is the delivery and the office "
    "files it. The blocks still incomplete stand "
    "named below, as blocks mapped to their files. "
    "The text you sent stands in the record, set "
    "aside unfiled; if it is the brief you mean to "
    "deliver, send it again at SUMMARIZE.")


def _tree_nodes(content):
    """The sealed process tree's node list, from the
    pinned case's own process_tree component (the room
    rebuild): the office-authored tree the case
    carries — a root (the brief's destination) and the
    steps in order: orient, one gather step per
    declared source, compose, deliver. Returns
    {"root": root, "nodes": [{"id", "kind",
    "address"?}, ...]} where the component stands
    well-formed in exactly the sealed shape, and None
    anywhere else — a case carrying no tree, or a
    misshapen one, stands under no tree, and an
    assembly sealed under the tree contract without
    one cannot be generated (the generator's
    preflight) or presented (the loop fails closed)."""
    tree = (content or {}).get("process_tree")
    if not isinstance(tree, dict):
        return None
    if set(tree) != {"root", "steps"}:
        return None
    root = tree.get("root")
    steps = tree.get("steps")
    if not isinstance(root, str) or not root:
        return None
    if not isinstance(steps, list) or not steps:
        return None
    nodes = []
    for step in steps:
        if not isinstance(step, dict):
            return None
        kind = step.get("node")
        if kind in ("orient", "compose", "deliver"):
            if set(step) != {"node"}:
                return None
            nodes.append({"id": kind, "kind": kind})
        elif kind == "gather":
            if set(step) != {"node", "address"}:
                return None
            address = step.get("address")
            if not isinstance(address, str) or \
                    not address:
                return None
            nodes.append({"id": f"gather:{address}",
                          "kind": "gather",
                          "address": address})
        else:
            return None
    kinds = [node["kind"] for node in nodes]
    if kinds[0] != "orient" or \
            kinds[-2:] != ["compose", "deliver"] or \
            any(kind != "gather"
                for kind in kinds[1:-2]) or \
            "gather" not in kinds:
        return None
    return {"root": root, "nodes": nodes}


def _tree_requested(events, head):
    """The record's requested parameters at a head,
    keyed by request identity — the same record fact
    the evidence computation reads."""
    requested = {}
    for ev in events:
        if ev["event_seq"] > head or \
                ev["type"] != "TOOL_REQUESTED":
            continue
        payload = ev["payload"]
        parameters = payload.get("parameters")
        if isinstance(parameters, dict):
            requested[payload.get("request_id")] = \
                parameters
    return requested


def _tree_read_stands(entries, requested, address):
    """Whether one address's whole content stands
    carried at the head, and the position of the read
    that stands: the standing evidence computation
    (_evidence_address_stands) weighed over the
    working set's entries, with the satisfying read's
    outcome position returned beside the verdict — a
    whole read's own position, or, where carried
    ranges together cover the file, the latest of the
    covering ranges' positions. (False, None) where
    the content does not stand."""
    mine = [entry for entry in entries
            if entry.get("path") == address]
    for entry in mine:
        if entry.get("tool") == "sandbox.read" and \
                entry.get("content_carried"):
            return True, entry.get("outcome_event_seq")
    if not _evidence_address_stands(
            entries, requested, address):
        return False, None
    seqs = [entry.get("outcome_event_seq")
            for entry in mine
            if entry.get("tool") == "sandbox.read_range"
            and entry.get("content_carried")
            and isinstance(
                entry.get("outcome_event_seq"), int)
            and not isinstance(
                entry.get("outcome_event_seq"), bool)]
    return True, (max(seqs) if seqs else None)


def _tree_journal_writes(events, dispatches, requested,
                         instance_id, head, journal_path):
    """The journal's standing writes at a head: every
    successful sandbox.write outcome of the instance
    addressed to the journal's path, in outcome order,
    as (outcome position, content) pairs — the write's
    content standing in the record's requested
    parameters, exactly as the executor wrote it (the
    write performer replaces the file with the
    parameter's content whole). The journal's content
    at the head is the last pair's content, or empty
    where no write stands."""
    writes = []
    for ev in events:
        if ev["event_seq"] > head or \
                ev["type"] != "TOOL_OUTCOME":
            continue
        payload = ev["payload"]
        if payload.get("outcome") != "result":
            continue
        dispatch = dispatches.get(
            payload.get("dispatch_id"))
        if dispatch is None or \
                dispatch.get("instance_id") != \
                instance_id or \
                dispatch.get("tool") != "sandbox.write":
            continue
        parameters = requested.get(
            payload.get("request_id")) or {}
        if parameters.get("path") != journal_path:
            continue
        content = parameters.get("content")
        writes.append((ev["event_seq"],
                       content if isinstance(
                           content, str) else ""))
    return writes


def _tree_state(events, dispatches, instance_id, head,
                content, iteration):
    """The tree's state at one package head, derived
    from the record alone: each node's state (done /
    current / pending), the current node, the gather
    facts the step gate weighs, the journal's content
    as it stands, and the working set the derivation
    weighed. Returns None where the case carries no
    well-formed tree.

    The derivation, in the tree's order: ORIENT is
    current at the first wake and done at every later
    one. A GATHER step is done iff its source's read
    stands carried (the standing evidence computation)
    AND a journal write stands after that read — the
    writes consumed in step order, one write closing
    at most one step, so a single write after a batch
    of reads cannot close two steps and skip a step's
    presentation. COMPOSE is done where a contribution
    of the instance stands (and the gathers stand
    done); DELIVER is done where the office's filing
    stands. The current node is the first node not
    done, in the tree's order."""
    tree = _tree_nodes(content)
    if tree is None:
        return None
    nodes = tree["nodes"]
    working_set = _derive_working_set(
        events, dispatches, instance_id, head)
    entries = working_set["entries"]
    requested = _tree_requested(events, head)
    journal_path = _staged_journal_path(content)
    writes = _tree_journal_writes(
        events, dispatches, requested, instance_id,
        head, journal_path) \
        if journal_path is not None else []
    gather_facts = {}
    consumed = 0
    for node in nodes:
        if node["kind"] != "gather":
            continue
        stands, read_seq = _tree_read_stands(
            entries, requested, node["address"])
        journal_stands = False
        if stands and read_seq is not None:
            for write_seq, _written in writes:
                if write_seq > max(read_seq, consumed):
                    journal_stands = True
                    consumed = write_seq
                    break
        gather_facts[node["id"]] = {
            "read_stands": stands,
            "read_seq": read_seq,
            "journal_stands": journal_stands}
    gathers_done = all(
        gather_facts[node["id"]]["read_stands"]
        and gather_facts[node["id"]]["journal_stands"]
        for node in nodes if node["kind"] == "gather")
    contribution_stands = any(
        ev["type"] == "CONTRIBUTION"
        and ev["event_seq"] <= head
        and (ev["payload"].get("contribution_id")
             == instance_id
             or instance_id in (ev.get("affected")
                                or []))
        for ev in events)
    filed = any(
        ev["type"] == "DELIVERABLE_FILED"
        and ev["event_seq"] <= head
        and ev["payload"].get("instance_id")
        == instance_id
        for ev in events)
    states = {}
    current = None
    for node in nodes:
        kind = node["kind"]
        if kind == "orient":
            done = iteration > 1
        elif kind == "gather":
            facts = gather_facts[node["id"]]
            done = facts["read_stands"] and \
                facts["journal_stands"]
        elif kind == "compose":
            done = gathers_done and contribution_stands
        else:
            done = filed
        states[node["id"]] = "done" if done else "pending"
        if not done and current is None:
            current = node
            states[node["id"]] = "current"
    journal_content = writes[-1][1] if writes else ""
    return {
        "root": tree["root"],
        "nodes": nodes,
        "states": states,
        "current": current,
        "gather_facts": gather_facts,
        "journal_path": journal_path,
        "journal_content": journal_content,
        "working_set": working_set,
        "entries": entries,
        "requested": requested}


def _tree_step_gate_owed(state):
    """What the step gate owes at a wake, from the
    derived tree state: (step id, address, missing,
    ahead address) where the current node is a GATHER
    step standing incomplete AND the record shows work
    standing ahead of it — a later gather step's read
    stands carried. The correction names what the
    current step still needs: the journal bits alone
    where its own read already stands, the read and
    then the journal bits where it does not. None
    anywhere else (the brief's own condition: the
    correction answers work requested ahead of the
    current step): a step just reached, or a step
    whose read stands with nothing ahead of it, is
    instructed by its step's own text in the ordinary
    walk, not corrected — the honest path carries no
    gate events."""
    current = state["current"]
    if current is None or \
            current["kind"] != "gather":
        return None
    facts = state["gather_facts"][current["id"]]
    if facts["read_stands"] and facts["journal_stands"]:
        return None
    ahead = None
    seen_current = False
    for node in state["nodes"]:
        if node["id"] == current["id"]:
            seen_current = True
            continue
        if not seen_current or \
                node["kind"] != "gather":
            continue
        if state["gather_facts"][node["id"]][
                "read_stands"]:
            ahead = node["address"]
            break
    if ahead is None:
        return None
    missing = ["journal"] if facts["read_stands"] \
        else ["read", "journal"]
    return (current["id"], current["address"],
            missing, ahead)


def _tree_presented_addresses(events, dispatches,
                              instance_id, content,
                              iteration_numbers):
    """The gather addresses whose content has already
    been presented at an earlier wake of this run,
    derived from the record alone: for each earlier
    iteration (its number and its package head, from
    the record's iteration events), the tree state at
    that head — where the iteration's current node was
    a gather step whose read stood, that step's
    content stood in front of the worker at that
    wake, presented once, at its step. The current
    wake presents its own step's content only where
    the address does not stand in this set."""
    presented = set()
    for number, head in iteration_numbers:
        earlier = _tree_state(
            events, dispatches, instance_id, head,
            content, number)
        if earlier is None:
            continue
        current = earlier["current"]
        if current is None or \
                current["kind"] != "gather":
            continue
        facts = earlier["gather_facts"][current["id"]]
        if facts["read_stands"]:
            presented.add(current["address"])
    return presented


# The office-cycle contract (the plan,
# PLAN-OFFICE-CYCLE-2026-11-25, approved by the
# director INDEX 582 and by the examiner INDEX 584;
# presentation contract office-cycle-v1). One opening
# package — his identity and role memory as his own
# knowledge, the task, the cycle poster (the job's
# shape in words and the sealed block map with an
# access way per block), the journal's designated
# address and its contract, and his position — then
# one package per cycle of the job's repeating shape:
# pull one block, read it, append his bits to the
# journal, gate, next block; and when every cycle
# stands complete, a SUMMARIZE package: read the
# journal whole and compile the brief from it. A
# block's content is presented once, at its cycle, and
# stands as a pointer after. The journal stands in NO
# package — no component, no excerpt; it is a file in
# his room, read + append, never carried — and the
# office's journal of record is the accepted chain of
# exact-prefix transitions over the sealed empty
# baseline. The tool catalogue rides no package as
# presented matter: the package's tools are the OFFER
# SET (the current cycle's tools plus the journal
# tools), while name resolution runs against the
# sealed grant-derived catalogue in the record — a
# granted call resolves whether or not it was offered;
# an ungranted call is refused at the doorway exactly
# as before. Every value in a cycle package derives
# from the record alone, so the checker re-derives the
# package whole, exactly as it re-derives the other
# contracts'. The wording below is the presentation's
# own; the checker's copies stand in checker.py.
CYCLE_COVER_FIRST = (
    "You are {seat}, the {role} in this office, "
    "assembled for one job. The shape of the work here "
    "is simple: you are woken with a package, you act, "
    "and the record keeps everything. This package is "
    "your whole opening — your memory, your task, the "
    "map of the job's cycles, your journal's address "
    "and its contract, and your position — all of it "
    "once, and nothing in it needs acknowledging: your "
    "first answer is work. The job walks in cycles, "
    "one block of the briefcase at a time: pull the "
    "block, read it, append the bits you took from it "
    "to your journal, and the next cycle begins. The "
    "job: {headline}. The deliverable: {deliverable}.")
CYCLE_DIRECTION_OPENING = (
    "Your opening package: everything in it is "
    "presented once, here — your memory, the task, "
    "the cycle poster with the briefcase's blocks and "
    "each block's way in, your journal's contract, and "
    "your position at cycle 1. Begin work in your "
    "first answer.")
CYCLE_DIRECTION_CYCLE = (
    "A cycle package: where the walk stands, this "
    "cycle's block and its way in, and — the first "
    "time its read stands — its content, presented "
    "once. Every other block stands as a pointer. "
    "Your journal is not carried; it stands in your "
    "room, at its address, to read and append.")
CYCLE_DIRECTION_SUMMARIZE = (
    "The summarize package: every cycle stands "
    "complete. Read your journal whole and compile "
    "the brief from it — the journal is the brief's "
    "substance. No source content rides this package; "
    "the sources stand as pointers, and the journal "
    "stands in your room at its address.")
CYCLE_POSTER_INTRO = (
    "The job walks in cycles, one block at a time. "
    "The office has portioned your briefcase's files "
    "into blocks — the blocks below, in order — and "
    "each cycle is one block: pull it by its way in, "
    "read it, and append the bits you took from it to "
    "your journal (its name and the key points, in one "
    "or two plain lines). A cycle completes when its "
    "block's read stands in the record and your "
    "journal append stands after it. A block's "
    "content is presented to you once, at its cycle; "
    "after that it stands as a pointer — its address, "
    "its range, its hash — and you can pull it again "
    "at any time. When every cycle stands complete, "
    "the walk ends in SUMMARIZE: you read your "
    "journal whole and compile the brief from it.")
CYCLE_JOURNAL_CONTRACT = (
    "your journal — your notebook, at the address "
    "below. It is a file in your room, and it is "
    "never carried in your packages: what you write "
    "there is yours, read back by you whenever you "
    "pull it. The rule of the journal is: entries "
    "stand; add, never rewrite. Each entry is an "
    "append — write the journal as it stands, plus "
    "your new bits at the end, in one sandbox.write "
    "to its address. A write that replaces what "
    "stands is not counted, and the walk does not "
    "advance on it. Keep it as you work: after each "
    "block you read, log its name and the key points "
    "you took from it, in one or two plain lines — "
    "at the end of the walk you compile the brief "
    "from these entries, so the bits are the brief's "
    "substance. Nothing parses it; it is read as you "
    "wrote it.")
CYCLE_PULL_INSTRUCTION = (
    "Cycle {cycle} of {total}: block {block_id} — "
    "{address}{range_text}. Pull it by the access "
    "call below, read it, then append the bits you "
    "took from it to your journal at {journal}: the "
    "journal as it stands, plus your new bits, in "
    "one sandbox.write. Its content is presented at "
    "the next wake, once; this cycle completes when "
    "its read stands and your append stands after "
    "it.")
CYCLE_READ_STANDS_INSTRUCTION = (
    "Cycle {cycle} of {total}: block {block_id} — "
    "{address}{range_text}. Its read stands, and its "
    "content stands presented above, once. Append "
    "the bits you took from it to your journal at "
    "{journal}: the journal as it stands, plus your "
    "new bits, in one sandbox.write — that append "
    "completes this cycle.")
CYCLE_WORKAROUND = (
    "If a range read fails or returns less than the "
    "block, read the whole file with sandbox.read "
    "instead — the block still counts, presented at "
    "its cycle. If a call fails, its result in your "
    "next package says why, in plain terms, with "
    "the working shape beside it.")
CYCLE_SUMMARIZE_INSTRUCTION = (
    "Every cycle stands complete — the walk is at "
    "SUMMARIZE. Read your journal whole, with "
    "sandbox.read at {journal}, and compile the "
    "brief from its entries: the bits you logged at "
    "each cycle are the brief's substance, in your "
    "own words. Cover the four points below. Stay "
    "accurate to what you gathered; invent nothing; "
    "where the sources disagree with each other, say "
    "so. When the brief is ready, deliver it: answer "
    "with outcome \"contribute\" and the brief's text "
    "as its text — the contribution is the delivery, "
    "and the office files it at {deliverable}.")
CYCLE_TASK_INTRO = (
    "Your task, whole, in this one place: the "
    "assignment, the deliverable, the four points "
    "the brief must cover, and the figures it runs "
    "to. It is presented once, here; your cycle "
    "packages carry your position against it, not "
    "the task again.")
# The split-on-return successor's room knowledge
# (office-cycle-v2): the room's rules, stated once
# in the opening as standing knowledge — the
# per-call budget in plain figures, the one-block-
# per-wake return, and the consequence for pulling
# ahead. Awareness by default; the office enforces
# the budget regardless, and no package repeats
# these lines or asks him to count. The figure in
# the text is the sealed budget's own (4,000
# estimated tokens, the plan §6 figure the tool
# policy seals); it is stated, not formatted from
# the constant, so the two copies — this one and
# the checker's — stand or fall together as one
# wording, exactly as the contract's other texts.
CYCLE_ROOM_KNOWLEDGE = (
    "The room's rules, once: every package the "
    "office sends you is kept under a budget of "
    "4,000 estimated tokens, and the office enforces "
    "that itself — it is never yours to count. Your "
    "results return one block per wake: however many "
    "blocks you pull in one answer, the next wake "
    "presents the current cycle's block, and every "
    "other block you have gathered stands as a "
    "pointer until its own cycle comes. Pulling "
    "ahead costs you nothing and gains you nothing "
    "in presentation — the walk moves at the "
    "cycle's pace, and nothing you have gathered is "
    "ever lost: it stands in the record, and its "
    "content is presented when its cycle comes.")
# The draft-page successor's texts (office-cycle-
# v3; the director's ruling of 2026-11-25 21:16
# MST, ordered after demo-gptoss6's fixation
# failure): the seven journal-defining wordings of
# the cycle presentation, exchanged whole. Every
# mechanism stands as under v1 and v2 — the same
# derivation selects these texts when the sealed
# contract is office-cycle-v3 and the standing
# texts otherwise, so a v1 or v2 package derives
# byte-identically to before. What changes is only
# what a journal entry IS: not the block's name and
# key points logged as research, but the draft of
# the part of the brief the block feeds, written in
# his own words as numbered steps in the journal
# contract — the brief created gradually in the
# journal, and SUMMARIZE the assembling of the
# draft that stands there.
CYCLE_COVER_FIRST_V3 = (
    "You are {seat}, the {role} in this office, "
    "assembled for one job. The shape of the work here "
    "is simple: you are woken with a package, you act, "
    "and the record keeps everything. This package is "
    "your whole opening — your memory, your task, the "
    "map of the job's cycles, your journal's address "
    "and its contract, and your position — all of it "
    "once, and nothing in it needs acknowledging: your "
    "first answer is work. The job walks in cycles, "
    "one block of the briefcase at a time: pull the "
    "block, read it, append your draft for it "
    "to your journal, and the next cycle begins. The "
    "job: {headline}. The deliverable: {deliverable}.")
CYCLE_DIRECTION_SUMMARIZE_V3 = (
    "The summarize package: every cycle stands "
    "complete. Read your journal whole and assemble "
    "the brief from the draft that stands in it — "
    "the journal holds the brief itself, in draft. "
    "No source content rides this package; "
    "the sources stand as pointers, and the journal "
    "stands in your room at its address.")
CYCLE_POSTER_INTRO_V3 = (
    "The job walks in cycles, one block at a time. "
    "The office has portioned your briefcase's files "
    "into blocks — the blocks below, in order — and "
    "each cycle is one block: pull it by its way in, "
    "read it, and append the bits you took from it to "
    "your journal (the draft of the part of the brief "
    "this block feeds, in your own words — the journal "
    "is your draft page, and the brief grows there). "
    "A cycle completes when its "
    "block's read stands in the record and your "
    "journal append stands after it. A block's "
    "content is presented to you once, at its cycle; "
    "after that it stands as a pointer — its address, "
    "its range, its hash — and you can pull it again "
    "at any time. When every cycle stands complete, "
    "the walk ends in SUMMARIZE: you read your "
    "journal whole and assemble the brief from the "
    "draft that stands in it.")
CYCLE_JOURNAL_CONTRACT_V3 = (
    "your journal — your draft page, at the address "
    "below. It is a file in your room, and it is never "
    "carried in your packages: what you write there is "
    "yours, read back by you whenever you pull it. The "
    "brief is built in this journal, gradually, as you "
    "work — the journal is not a copy of your research. "
    "Work each block in these steps: (1) read the "
    "block; (2) in your journal, write the draft of "
    "the part of the brief this block feeds — full "
    "sentences, in your own words, the very words the "
    "brief will use; never copy the block's own text "
    "into the journal, because a copy is not a draft; "
    "(3) when that draft stands in the journal, the "
    "cycle is complete and the next block comes. The "
    "rule of the journal is: entries stand; add, never "
    "rewrite. Each entry is an append — write the "
    "journal as it stands, plus your new draft at the "
    "end, in one sandbox.write to its address. A write "
    "that replaces what stands is not counted, and the "
    "walk does not advance on it. At the end of the "
    "walk you assemble the brief from the draft that "
    "stands in the journal — the brief is already "
    "written there, in draft; finishing it is joining "
    "and smoothing, not starting over. Nothing parses "
    "it; it is read as you wrote it.")
CYCLE_PULL_INSTRUCTION_V3 = (
    "Cycle {cycle} of {total}: block {block_id} — "
    "{address}{range_text}. Pull it by the access "
    "call below, read it, then append your draft for "
    "this block to your journal at {journal}: the "
    "journal as it stands, plus your draft — the part "
    "of the brief this block feeds, in your own words, "
    "in one sandbox.write. Its content is presented at "
    "the next wake, once; this cycle completes when "
    "its read stands and your append stands after "
    "it.")
CYCLE_READ_STANDS_INSTRUCTION_V3 = (
    "Cycle {cycle} of {total}: block {block_id} — "
    "{address}{range_text}. Its read stands, and its "
    "content stands presented above, once. Append "
    "your draft for this block to your journal at "
    "{journal}: the journal as it stands, "
    "plus your draft — the part of the brief this "
    "block feeds, in your own words, in one "
    "sandbox.write — that append "
    "completes this cycle.")
CYCLE_SUMMARIZE_INSTRUCTION_V3 = (
    "Every cycle stands complete — the walk is at "
    "SUMMARIZE. Read your journal whole, with "
    "sandbox.read at {journal}, and assemble the "
    "brief from the draft that stands in its "
    "entries: the draft you wrote at each cycle is "
    "the brief itself, in draft — join the parts, "
    "smooth the joins, in your own words. Cover "
    "the four points below. Stay "
    "accurate to what you gathered; invent nothing; "
    "where the sources disagree with each other, say "
    "so. When the brief is ready, deliver it: answer "
    "with outcome \"contribute\" and the brief's text "
    "as its text — the contribution is the delivery, "
    "and the office files it at {deliverable}.")
# The cleaned-opening successor's standing texts
# (office-cycle-v4; the director's orders of
# 2026-11-25 21:33 and 21:36 MST): the director's
# own cleaned structure of the opening package,
# rendered from the sealed case — his sections in
# his order, his compressed lines for the standing
# assignment's fixed wording, with the brief's
# resolutions applied: the deliverable line set to
# the contribute door the machinery honours (his
# option-A ruling), the memory's contribute line
# corrected to name that door, the memory's shell
# line removed (the package offers no shell), and
# the working method's leftover key-points line
# removed (the draft line supersedes it). The
# tools' one-liners are his, word for word.
CYCLE_OPENING_TOOLS_V4 = (
    "- `sandbox.read` — full text file "
    "(sources only)",
    "- `sandbox.read_range` — line range or "
    "heading section (sources only)",
    "- `sandbox.write` — write/replace file "
    "(scratch only)")
CYCLE_OPENING_MEMORY_V4 = (
    "Prefers plain prose delivery.",
    "Reaches for the contribute outcome as his "
    "delivery route — for this job that is the "
    "correct door: the office files it at the "
    "deliverable's destination.",
    "Wants sources, style preferences, and "
    "word-count target stated clearly up front.",
    "Target ~600 words (±10); previous attempt "
    "was only ~405 words.",
    "Journal purpose must be stated explicitly "
    "or it is ignored.",
    "If something is missing from the briefcase, "
    "explicitly ask or pull via the stated route "
    "— do not improvise silently.")


def _cycle_opening_text_v4(*, seat, role,
                           instance_id, case_id,
                           case_version, destination,
                           points, min_words, blocks,
                           catalogue, journal_path,
                           total,
                           contract=_tool_policy
                           .PRESENTATION_CONTRACT_V7):
    """The v4 opening's plain-text structure (the
    director's cleaned opening, rendered from the
    sealed case): his sections in his order — role
    and identity; the task, its deliverable line
    set to the contribute door and its content
    requirements from the case's points and
    figures; the sources, one line per block from
    the sealed block map; the working method; the
    three tools; the standing memory in his
    compressed lines; and his position. No JSON
    component assembly stands in the opening under
    this contract, and no catalogue JSON. The
    contract line names the sealed contract — a
    rendered fact of the seal, as the destination
    and the figures are — so the carryover
    successor (office-cycle-v5), whose opening is
    this text whole, names its own seal there and
    nothing else in the text moves."""
    lines = [f"Opening package — {seat}", "",
             "Role & identity",
             f"- Seat: {seat} (role: {role})",
             f"- Instance: {instance_id}",
             f"- Case: {case_id} "
             f"(version {case_version})",
             f"- Contract: {contract}",
             "- Package type: opening", "",
             "Task",
             "Deliverable: the brief is delivered "
             "as the \"contribute\" outcome at the "
             "end of the walk; the office files it "
             f"at {destination}; only a filed brief "
             "completes the assignment."]
    figures = "about 600 words"
    if min_words is not None:
        figures += (
            f" (minimum {min_words}; the door will "
            f"not file a brief under {min_words} "
            "words)")
    lines.append(
        "Content requirements: a plain-language "
        f"brief of {figures}. A newcomer should be "
        "able to understand:")
    lines.append("; ".join(
        f"({i}) {point}" for i, point in
        enumerate(points, 1)) + ".")
    addresses = []
    for block in blocks:
        if block["address"] not in addresses:
            addresses.append(block["address"])
    count_words = {1: "one", 2: "two", 3: "three",
                   4: "four"}
    count = count_words.get(
        len(addresses), str(len(addresses)))
    lines.append(
        "Stay strictly accurate to the "
        f"{count} source documents. Note any "
        "disagreements between them. Invent "
        "nothing.")
    lines += ["", "Sources (must all be read)"]
    for block in blocks:
        way = _cycle_access(block, catalogue)
        tool = way["tool"] if way is not None \
            else "no access way stands"
        span = "full file" \
            if block["line_start"] is None else \
            f"lines {block['line_start']}-" \
            f"{block['line_end']}"
        lines.append(
            f"- {block['block_id']}: "
            f"{block['address']} — {tool} — {span}")
    lines.append(
        "Evidence boundary hashes are given for "
        "verification.")
    lines += ["", "Working method (cycles)",
              f"- {total} cycles, one block each.",
              "- For each block: read it, then "
              "append a draft section to your "
              "journal — your own words, full "
              "sentences: the draft of the part of "
              "the brief this block feeds.",
              f"- Journal: {journal_path}. Append "
              "only — never rewrite what stands. "
              "Each append is the journal as it "
              "stands, plus your new draft at the "
              "end, in one sandbox.write.",
              "- When all cycles are done, "
              "assemble the final brief from the "
              "journal draft and deliver it as the "
              "\"contribute\" outcome — the office "
              f"files it at {destination}. Then "
              "yield.", "",
              "Tools available (only these)"]
    lines += CYCLE_OPENING_TOOLS_V4
    lines += ["", "Standing memory (role knowledge)"]
    lines += [f"- {line}"
              for line in CYCLE_OPENING_MEMORY_V4]
    lines += ["", "Position",
              f"Cycle 1 of {total}. Nothing settled "
              "yet. First answer is work (no "
              "acknowledgement needed)."]
    return "\n".join(lines)


def _cycle_opening_text_v8(*, seat, role,
                           instance_id, case_id,
                           case_version, destination,
                           points, min_words, files,
                           catalogue, journal_path,
                           total,
                           contract=_tool_policy
                           .PRESENTATION_CONTRACT_V11):
    """The v8 opening's plain-text structure: the
    director's cleaned opening (v4's text) rendered
    at the file grain — his sections in his order,
    and wherever the v4 rendering stated blocks or
    six cycles, this rendering states the file
    facts instead (the brief §2.1): the sources,
    one line per FILE, a file that arrives in parts
    noted as arriving in parts with its ranges; the
    working method as the file rhythm — read the
    file, append your summary of it, next file —
    and the position counting files. The parts are
    named only inside their file's line, as the
    plumbing they are; no section of the opening
    lists them as work."""
    lines = [f"Opening package — {seat}", "",
             "Role & identity",
             f"- Seat: {seat} (role: {role})",
             f"- Instance: {instance_id}",
             f"- Case: {case_id} "
             f"(version {case_version})",
             f"- Contract: {contract}",
             "- Package type: opening", "",
             "Task",
             "Deliverable: the brief is delivered "
             "as the \"contribute\" outcome at the "
             "end of the walk; the office files it "
             f"at {destination}; only a filed brief "
             "completes the assignment."]
    figures = "about 600 words"
    if min_words is not None:
        figures += (
            f" (minimum {min_words}; the door will "
            f"not file a brief under {min_words} "
            "words)")
    lines.append(
        "Content requirements: a plain-language "
        f"brief of {figures}. A newcomer should be "
        "able to understand:")
    lines.append("; ".join(
        f"({i}) {point}" for i, point in
        enumerate(points, 1)) + ".")
    count_words = {1: "one", 2: "two", 3: "three",
                   4: "four"}
    count = count_words.get(
        total, str(total))
    lines.append(
        "Stay strictly accurate to the "
        f"{count} source documents. Note any "
        "disagreements between them. Invent "
        "nothing.")
    lines += ["", "Sources (must all be read)"]
    for entry in files:
        blocks = entry["blocks"]
        if len(blocks) == 1:
            block = blocks[0]
            way = _cycle_access(block, catalogue)
            tool = way["tool"] if way is not None \
                else "no access way stands"
            lines.append(
                f"- {entry['file_id']}: "
                f"{entry['address']} — {tool} — "
                f"full file")
        else:
            ranges = ", ".join(
                f"lines {block['line_start']}-"
                f"{block['line_end']}"
                for block in blocks)
            lines.append(
                f"- {entry['file_id']}: "
                f"{entry['address']} — arrives in "
                f"parts ({ranges}), read part by "
                f"part inside this file's step")
    lines.append(
        "Evidence boundary hashes are given for "
        "verification.")
    lines += ["", "Working method (files)",
              f"- {total} files, one at a time.",
              "- For each file: read it, then "
              "append a draft section to your "
              "journal — your own words, full "
              "sentences: the draft of the part of "
              "the brief this file feeds. A file "
              "that arrives in parts is read part "
              "by part inside its step; the summary "
              "is appended once, when the file "
              "stands whole.",
              f"- Journal: {journal_path}. Append "
              "only — never rewrite what stands. "
              "Each append is the journal as it "
              "stands, plus your new draft at the "
              "end, in one sandbox.write.",
              "- When all files are done, "
              "assemble the final brief from the "
              "journal draft and deliver it as the "
              "\"contribute\" outcome — the office "
              f"files it at {destination}. Then "
              "yield.", "",
              "Tools available (only these)"]
    lines += CYCLE_OPENING_TOOLS_V4
    lines += ["", "Standing memory (role knowledge)"]
    lines += [f"- {line}"
              for line in CYCLE_OPENING_MEMORY_V4]
    lines += ["", "Position",
              f"File 1 of {total}. Nothing settled "
              "yet. First answer is work (no "
              "acknowledgement needed)."]
    return "\n".join(lines)


# The carryover successor's texts (office-cycle-
# v5; the director's orders of 2026-11-25 22:09
# MST, after demo-gptoss8): the cycle package's
# direction can no longer say the journal is not
# carried — under this contract it rides at the
# package's centre as his draft so far — and the
# summarize direction says the same. The label
# the draft component carries, and the one next
# step the cycle instruction states, are the
# contract's other two wordings; everything else
# in the cycle presentation is v4's whole.
CYCLE_DIRECTION_CYCLE_V5 = (
    "A cycle package: where the walk stands, this "
    "cycle's block and its way in, and — the first "
    "time its read stands — its content, presented "
    "once. Every other block stands as a pointer. "
    "Your journal rides in this package as your "
    "draft so far — the brief you are building, "
    "carried at its centre, so each next step is "
    "taken from your own words.")
CYCLE_DIRECTION_SUMMARIZE_V5 = (
    "The summarize package: every cycle stands "
    "complete. Your journal rides in this package "
    "as your draft so far — assemble the brief "
    "from the draft that stands in it. No source "
    "content rides this package; the sources stand "
    "as pointers.")
CYCLE_JOURNAL_DRAFT_LABEL_V5 = (
    "Your draft so far — your journal as it "
    "stands, the brief you are building. It rides "
    "at the centre of every package under this "
    "contract; your next append extends this "
    "text.")
# The zero-carryover successor's direction
# (office-cycle-v6; the director's ruling of
# 2026-11-25 22:29 MST, reversing the carryover
# above): the standing truth stated again in the
# job's plain words — the journal is not carried;
# it stands in his scratch at its own address, and
# he reads it when he needs it, a pull like any
# other. The address is the case's own, formatted
# in at the package's build, as the next step
# below formats it.
CYCLE_DIRECTION_CYCLE_V6 = (
    "A cycle package: where the walk stands, this "
    "cycle's block and its way in, and — the first "
    "time its read stands — its content, presented "
    "once. Every other block stands as a pointer. "
    "Your journal is not carried; it stands in "
    "your scratch at {journal}, and you read it "
    "when you need it — a sandbox.read of the "
    "journal is a pull like any other.")


def _cycle_next_step_v5(block, journal_path):
    """The one next step a v5 cycle package states,
    in the job's plain words (the director's own
    statement of the job, 2026-11-25 22:08 MST:
    read the file, write the summary in the
    journal, repeat, then combine), derived from
    the current cycle's state at presentation:
    where the block's read does not yet stand, the
    step is the read and the append it feeds;
    where the read stands, the step is the append
    alone, and it completes the cycle. The append
    is named in its counted form — the journal as
    it stands, plus the new part at the end, in
    one sandbox.write — the same form the journal
    gate's correction names."""
    address = block["address"]
    if block["read_stands"]:
        return (
            f"Next: append your summary of "
            f"{address} to your journal at "
            f"{journal_path} — the journal as it "
            f"stands, plus your summary at the "
            f"end, in one sandbox.write. That "
            f"append completes this cycle.")
    if block["line_start"] is not None:
        span = (f" lines {block['line_start']}–"
                f"{block['line_end']}")
    else:
        span = " — the whole file"
    return (
        f"Next: read {address}{span}, then append "
        f"your summary of it to your journal at "
        f"{journal_path} — the journal as it "
        f"stands, plus your summary at the end, "
        f"in one sandbox.write.")


def _cycle_next_line_v7(block, journal_path, *,
                        refused=False):
    """The Next line an office-cycle-v7 package
    opens with (the director's order of
    2026-11-25 22:41 MST, after he watched
    demo-gptoss9's packages describe state and
    leave the deciding to the worker): the
    imperative first, one line, before any state —
    derived at presentation time from the current
    cycle state, never canned text that can go
    stale against the state it opens. Where the
    block's read does not yet stand, the step is
    the read and the append it feeds; where the
    read stands — or a gate refusal stands against
    the last move, whose passing step is the
    append in its counted form — the step is the
    append alone. On the summarize package (no
    current block) the step is the combine: read
    the journal, combine its summaries into the
    brief, deliver by the contribute outcome. The
    gate's correction, where one stands, follows
    the line unmerged: the correction explains,
    the Next line commands."""
    if block is None:
        return (
            f"Next: read your journal at "
            f"{journal_path}, combine its "
            f"summaries into the brief (about "
            f"600 words), and deliver the brief "
            f"as your contribute outcome.")
    address = block["address"]
    if refused or block["read_stands"]:
        return (
            f"Next: append your summary of "
            f"{address} to your journal — the "
            f"standing journal plus your new "
            f"part at the end, in one write.")
    if block["line_start"] is not None:
        span = (f"lines {block['line_start']}–"
                f"{block['line_end']}")
    else:
        span = "in full"
    return (
        f"Next: read {address} {span}. Then "
        f"append your summary of it to your "
        f"journal.")


# The file-grain successor's direction
# (office-cycle-v8; the director's orders of
# 2026-11-25 23:03 MST): the cycle direction in
# the job's own units — this file, its way in,
# its content presented once as it stands read
# (a file that arrives in parts presents each
# part once, as it lands; every other part and
# every other file stands as a pointer) — and
# the zero-carryover truth, as v6 states it.
# The address is the case's own, formatted in
# at the package's build, as the next step
# below formats it.
CYCLE_DIRECTION_CYCLE_V8 = (
    "A cycle package: where the walk stands, this "
    "file and its way in, and — the first time "
    "its read stands — its content, presented "
    "once. A file that arrives in parts presents "
    "each part once, as it lands; every other "
    "part and every other file stands as a "
    "pointer. Your journal is not carried; it "
    "stands in your scratch at {journal}, and "
    "you read it when you need it — a sandbox."
    "read of the journal is a pull like any "
    "other.")


def _cycle_next_line_v8(file, journal_path, *,
                        refused=False):
    """The Next line an office-cycle-v8 package
    opens with: v7's rule (the imperative first,
    derived at presentation from the state it
    opens) at the file grain — the walk's unit is
    the file, so the line derives from the FILE's
    state. Where the file's read stands whole —
    or a gate refusal stands against the last
    move, whose passing step is the append — the
    step is the append alone, in v7's own wording.
    Where the file is one whole-file block not
    yet read, the step is v7's read form. Where
    the file arrives in parts and a part is still
    owed, the step is the next part alone — no
    append is promised after a part, because no
    append is asked between a file's parts: the
    append comes when the file stands whole. On
    the summarize package (no current file) the
    step is v7's combine line, unchanged."""
    if file is None:
        return _cycle_next_line_v7(
            None, journal_path)
    address = file["address"]
    if refused or file["read_stands"]:
        return (
            f"Next: append your summary of "
            f"{address} to your journal — the "
            f"standing journal plus your new "
            f"part at the end, in one write.")
    blocks = file["blocks"]
    if len(blocks) == 1:
        return _cycle_next_line_v7(
            blocks[0], journal_path)
    nxt = next(block for block in blocks
               if not block["read_stands"])
    return (
        f"Next: read {address} lines "
        f"{nxt['line_start']}–{nxt['line_end']} "
        f"— the next part of the file.")


def _cycle_next_step_v8(file, journal_path):
    """The one next step a v8 cycle package's
    current-file component states, in the fuller
    form (v5's next-step shape at the file grain):
    where the file's read stands, the append
    alone, completing the file; where a part is
    still owed, the next part — and the append
    the whole file feeds, named as the step's
    end, not as a step between parts."""
    address = file["address"]
    if file["read_stands"]:
        return (
            f"Next: append your summary of "
            f"{address} to your journal at "
            f"{journal_path} — the journal as it "
            f"stands, plus your summary at the "
            f"end, in one sandbox.write. That "
            f"append completes this file.")
    blocks = file["blocks"]
    if len(blocks) == 1:
        return (
            f"Next: read {address} — the whole "
            f"file, then append your summary of "
            f"it to your journal at "
            f"{journal_path} — the journal as it "
            f"stands, plus your summary at the "
            f"end, in one sandbox.write.")
    nxt = next(block for block in blocks
               if not block["read_stands"])
    return (
        f"Next: read {address} lines "
        f"{nxt['line_start']}–{nxt['line_end']} "
        f"— the next part of the file. The "
        f"file's parts are plumbing inside this "
        f"step: no summary is appended between "
        f"parts; when every part stands read, "
        f"append your summary of the whole file "
        f"to your journal at {journal_path} — "
        f"the journal as it stands, plus your "
        f"summary at the end, in one "
        f"sandbox.write.")


def _cycle_gate_correction_v8(gate, journal_path,
                              files):
    """The correction a cycle gate leaves for the
    wake's package under the file grain, derived
    from the gate event's facts in the job's own
    units (the standing correction's shape, the
    files named as files): a later file's read
    stands while the walk stands on an earlier
    file, and the walk stays on the earlier file
    until its read stands and its journal append
    stands. The gate payload names the current
    file's number as its cycle and anchors both
    files by their first blocks; the file ids are
    read from the derived file state."""
    def _file_id(address, block_id):
        for entry in files or []:
            if entry["address"] == address or \
                    block_id in entry["block_ids"]:
                return entry["file_id"]
        return None

    cycle = gate.get("cycle")
    address = gate.get("address")
    ahead_address = gate.get("ahead_address")
    mine_id = _file_id(address, gate.get("block_id"))
    ahead_id = _file_id(
        ahead_address, gate.get("ahead_block_id"))
    mine = (f"file {mine_id} ({address})"
            if mine_id else f"the file {address}")
    ahead = (f"file {ahead_id} ({ahead_address})"
             if ahead_id else
             f"the file {ahead_address}")
    return {
        "cycle": cycle,
        "file_id": mine_id,
        "address": address,
        "ahead_file_id": ahead_id,
        "ahead_address": ahead_address,
        "what_arrived": (
            f"The read of {ahead} stands in the "
            f"record — your work arrived and it "
            f"stands: nothing is refused, nothing "
            f"is lost, and {ahead} will be "
            f"presented at its own step."),
        "instruction": (
            f"The walk is still on {mine}: it "
            f"completes when its read stands and "
            f"your journal holds your summary of "
            f"it. Append your summary at "
            f"{journal_path} — the journal as it "
            f"stands, plus the new part at the "
            f"end, in one sandbox.write — and "
            f"the walk moves on."),
        "example": (
            f"For example: sandbox.write with "
            f"{{\"path\": \"{journal_path}\", "
            f"\"content\": \"<your journal as it "
            f"stands, plus your summary of "
            f"{address}>\"}}.")}


def _cycle_gate_correction(gate, journal_path):
    """The correction a cycle gate leaves for the
    wake's package, derived from the gate event's
    facts (Ben's gate ruling, INDEX 475 — what
    arrived, what is needed, an example; nothing
    refused, nothing lost): a later block's read
    stands while an earlier cycle stands incomplete,
    and the walk stays on the earlier cycle until its
    journal append stands."""
    cycle = gate.get("cycle")
    block_id = gate.get("block_id")
    address = gate.get("address")
    ahead_id = gate.get("ahead_block_id")
    ahead_address = gate.get("ahead_address")
    return {
        "cycle": cycle,
        "block_id": block_id,
        "address": address,
        "ahead_block_id": ahead_id,
        "ahead_address": ahead_address,
        "what_arrived": (
            f"The read of block {ahead_id} "
            f"({ahead_address}) stands in the record — "
            f"your work arrived and it stands: nothing "
            f"is refused, nothing is lost, and block "
            f"{ahead_id} will be presented at its own "
            f"cycle."),
        "instruction": (
            f"The walk is still on cycle {cycle}: "
            f"block {block_id} ({address}) completes "
            f"when your journal holds the bits you "
            f"took from it. Append them at "
            f"{journal_path} — the journal as it "
            f"stands, plus the new bits, in one "
            f"sandbox.write — and the walk moves on."),
        "example": (
            f"For example: sandbox.write with "
            f"{{\"path\": \"{journal_path}\", "
            f"\"content\": \"<your journal as it "
            f"stands, plus the bits from block "
            f"{block_id}>\"}}.")}


def _journal_gate_correction(gate, journal_path):
    """The correction a journal gate leaves for the
    wake's package, derived from the gate event's
    facts (the same ruling's shape): a write to the
    journal rewrote instead of adding, so it is not
    counted as a transition and the accepted journal
    did not move — the correction names the rule and
    the way back."""
    return {
        "what_arrived": (
            f"A write to your journal at "
            f"{journal_path} stands in the record "
            f"whose content did not begin with your "
            f"journal as it stands — it rewrote "
            f"instead of adding. The write executed, "
            f"and it stands as your work; it is not "
            f"counted as a journal entry, and the "
            f"journal of record did not move."),
        "instruction": (
            f"The rule of the journal is: entries "
            f"stand; add, never rewrite. Read your "
            f"journal back with sandbox.read at "
            f"{journal_path}, and write it again "
            f"whole — what stands, plus your new bits "
            f"appended at the end — in one "
            f"sandbox.write. That append is counted, "
            f"and the walk advances on it."),
        "example": (
            f"For example: sandbox.read with "
            f"{{\"path\": \"{journal_path}\"}}, then "
            f"sandbox.write with {{\"path\": "
            f"\"{journal_path}\", \"content\": \"<the "
            f"journal as it stands, plus your new "
            f"bits>\"}}.")}


def _cycle_blocks(content, generated):
    """The sealed block map the cycle contract
    honours: the generated record's block map, where
    it stands well-formed against the case's declared
    delivery evidence (the seal's own preflight rule),
    else None — no cycle state derives from a map that
    does not stand."""
    if not isinstance(generated, dict):
        return None
    evidence = (content or {}).get("delivery_evidence")
    declared = evidence.get("addresses") \
        if isinstance(evidence, dict) else None
    block_map = generated.get("block_map")
    if _tool_policy.block_map_problem(
            block_map, declared) is not None:
        return None
    return block_map


def _block_read_facts(entries, block):
    """Whether one block's read stands carried, and
    the dispatch completing it (the cycle gate's rule,
    the plan §5): for a range block, a carried
    read_range serving exactly its sealed range, or a
    carried whole read of its file; for a whole-file
    block, a carried whole read, or carried pure-line
    ranges together covering the file's lines [1..T]
    (T standing in a carried listing of the file, as
    the standing evidence computation reads it).
    Returns (stands, completing outcome seq, the
    establishing entry) — the entry whose provenance
    the block's pointer carries: the completing
    dispatch's own entry."""
    address = block["address"]
    mine = [entry for entry in entries
            if entry.get("path") == address
            and entry.get("tool") in (
                "sandbox.read", "sandbox.read_range")
            and entry.get("content_carried")
            and "content" in entry]
    if block.get("line_start") is not None:
        for entry in mine:
            if entry.get("tool") == "sandbox.read" and \
                    (entry.get("served") or {}).get(
                        "kind") == "whole":
                return True, \
                    entry.get("outcome_event_seq"), entry
        for entry in mine:
            served = entry.get("served") or {}
            if entry.get("tool") == "sandbox.read_range" \
                    and served.get("kind") == "range" \
                    and served.get("byte_start") is None \
                    and served.get("start_line") == \
                    block["line_start"] \
                    and served.get("end_line") == \
                    block["line_end"]:
                return True, \
                    entry.get("outcome_event_seq"), entry
        return False, None, None
    for entry in mine:
        if entry.get("tool") == "sandbox.read" and \
                (entry.get("served") or {}).get(
                    "kind") == "whole":
            return True, entry.get("outcome_event_seq"), \
                entry
    total = None
    for entry in entries:
        if entry.get("path") == address and \
                entry.get("tool") == "sandbox.list":
            served = entry.get("served") or {}
            if isinstance(served.get("line_count"), int) \
                    and not isinstance(
                        served.get("line_count"), bool):
                total = served["line_count"]
    if total is None:
        return False, None, None
    covered_to = 0
    for entry in mine:
        served = entry.get("served") or {}
        if entry.get("tool") != "sandbox.read_range" \
                or served.get("kind") != "range" \
                or served.get("byte_start") is not None:
            continue
        start = served.get("start_line")
        end = served.get("end_line")
        if not isinstance(start, int) or \
                not isinstance(end, int):
            continue
        if start <= covered_to + 1:
            covered_to = max(covered_to, end)
            if covered_to >= total:
                return True, \
                    entry.get("outcome_event_seq"), entry
    return False, None, None


def _block_content(entries, block):
    """A block's content, assembled from the working
    set's carried entries — the content its cycle
    presents, exactly the bytes its read carried: for
    a range block, its exact range entry's content, or
    its whole-read entry's content sliced to the
    block's lines; for a whole-file block, its whole
    read's content, or its covering ranges' contents
    joined in line order. None where the block's read
    does not stand."""
    address = block["address"]
    mine = [entry for entry in entries
            if entry.get("path") == address
            and entry.get("tool") in (
                "sandbox.read", "sandbox.read_range")
            and entry.get("content_carried")
            and "content" in entry]
    if block.get("line_start") is not None:
        for entry in mine:
            served = entry.get("served") or {}
            if entry.get("tool") == "sandbox.read_range" \
                    and served.get("kind") == "range" \
                    and served.get("byte_start") is None \
                    and served.get("start_line") == \
                    block["line_start"] \
                    and served.get("end_line") == \
                    block["line_end"]:
                return entry["content"]
        for entry in mine:
            if entry.get("tool") == "sandbox.read" and \
                    (entry.get("served") or {}).get(
                        "kind") == "whole":
                lines = _tool_policy.split_lines(
                    entry["content"].encode("utf-8"))
                part = b"".join(lines[
                    block["line_start"] - 1:
                    block["line_end"]])
                return part.decode("utf-8")
        return None
    for entry in mine:
        if entry.get("tool") == "sandbox.read" and \
                (entry.get("served") or {}).get(
                    "kind") == "whole":
            return entry["content"]
    stands, _seq, _entry = _block_read_facts(
        entries, block)
    if not stands:
        return None
    parts = []
    for entry in mine:
        served = entry.get("served") or {}
        if entry.get("tool") == "sandbox.read_range" \
                and served.get("kind") == "range" \
                and served.get("byte_start") is None \
                and isinstance(
                    served.get("start_line"), int):
            parts.append((served["start_line"],
                          entry["content"]))
    parts.sort(key=lambda part: part[0])
    return "".join(content for _start, content in parts)


def _journal_chain(writes):
    """The office's journal of record over the
    journal's standing writes ((outcome seq, content)
    pairs in outcome order, _tree_journal_writes'
    collection): the accepted chain of transitions
    from the sealed baseline — the empty string. A
    write is an accepted transition where its content
    holds the accepted content as an exact prefix and
    is longer; it is a refusal where its content does
    not hold the accepted content as a prefix (it
    rewrote, or replaced); a write repeating the
    accepted content exactly is neither — nothing
    added, nothing rewritten away. The accepted
    content after the chain is the journal of record;
    the room's file may hold something else (a refused
    write executed there), and every derivation reads
    the accepted chain, stated honestly: the prefix
    rule proves continuity between accepted states —
    it is not a cryptographic authenticity system."""
    accepted = ""
    transitions = []
    refusals = []
    for write_seq, content in writes:
        if content == accepted:
            continue
        if content.startswith(accepted):
            transitions.append({
                "write_seq": write_seq,
                "before_sha256": sha256_hex(
                    accepted.encode("utf-8")),
                "after_sha256": sha256_hex(
                    content.encode("utf-8")),
                "added_bytes": len(
                    content.encode("utf-8")) - len(
                    accepted.encode("utf-8")),
                "content_after": content})
            accepted = content
        else:
            refusals.append({
                "write_seq": write_seq,
                "accepted_sha256": sha256_hex(
                    accepted.encode("utf-8")),
                "attempted_sha256": sha256_hex(
                    content.encode("utf-8"))})
    return {"accepted": accepted,
            "transitions": transitions,
            "refusals": refusals}


def _cycle_state(events, dispatches, instance_id, head,
                 content, generated, iteration):
    """The cycle walk's state at one package head,
    derived from the record alone: each block's state
    (done / current / pending), the current cycle, the
    journal chain over the accepted baseline, and the
    working set the derivation weighed. Returns None
    where the sealed block map does not stand or the
    case designates no journal.

    The derivation, in the map's order: a block's
    cycle is done iff its read stands carried (the
    block rule) AND an accepted journal transition
    stands after the dispatch completing the read —
    transitions consumed in cycle order, one
    transition closing at most one cycle, so a single
    append after a batch of reads cannot close two
    cycles. A transition is attributed to the earliest
    cycle it closes; a transition closing none (it
    stands before its cycle's read, or after every
    cycle stands done) is attributed to the cycle
    current at its writing, or to none where the walk
    already stood complete. The current cycle is the
    first cycle not done; where none stands, the walk
    is at SUMMARIZE."""
    block_map = _cycle_blocks(content, generated)
    journal_path = _staged_journal_path(content)
    if block_map is None or journal_path is None:
        return None
    working_set = _derive_working_set(
        events, dispatches, instance_id, head)
    entries = working_set["entries"]
    requested = _tree_requested(events, head)
    writes = _tree_journal_writes(
        events, dispatches, requested, instance_id,
        head, journal_path)
    chain = _journal_chain(writes)
    facts = {}
    for index, block in enumerate(block_map):
        stands, read_seq, entry = _block_read_facts(
            entries, block)
        facts[block["block_id"]] = {
            "read_stands": stands,
            "read_seq": read_seq,
            "entry": entry,
            "cycle": index + 1}
    closed = {}
    attribution = {}
    for transition in chain["transitions"]:
        target = None
        for block in block_map:
            if block["block_id"] in closed:
                continue
            block_facts = facts[block["block_id"]]
            if block_facts["read_stands"] and \
                    block_facts["read_seq"] is not None \
                    and block_facts["read_seq"] < \
                    transition["write_seq"]:
                target = block
                break
        if target is not None:
            closed[target["block_id"]] = transition
            attribution[transition["write_seq"]] = \
                facts[target["block_id"]]["cycle"]
        else:
            following = next(
                (block for block in block_map
                 if block["block_id"] not in closed),
                None)
            attribution[transition["write_seq"]] = \
                facts[following["block_id"]]["cycle"] \
                if following is not None else None
    blocks = []
    current = None
    for index, block in enumerate(block_map):
        done = block["block_id"] in closed
        if done:
            state_name = "done"
        elif current is None:
            state_name = "current"
            current = index + 1
        else:
            state_name = "pending"
        blocks.append(dict(
            block, state=state_name,
            read_stands=facts[
                block["block_id"]]["read_stands"],
            read_seq=facts[block["block_id"]]["read_seq"],
            entry=facts[block["block_id"]]["entry"],
            cycle=index + 1))
    return {
        "block_map": block_map,
        "blocks": blocks,
        "current": current,
        "journal_path": journal_path,
        "writes": writes,
        "chain": chain,
        "attribution": attribution,
        "working_set": working_set,
        "entries": entries,
        "requested": requested}


def _cycle_files(content, generated):
    """The sealed file grouping the file-grain
    contract honours: the generated record's file
    map, where it stands well-formed against the
    sealed block map (the seal's own rule, in
    tool_policy), else None — no file-grain state
    derives from a grouping that does not stand."""
    if not isinstance(generated, dict):
        return None
    block_map = _cycle_blocks(content, generated)
    if block_map is None:
        return None
    file_map = generated.get("file_map")
    if _tool_policy.file_map_problem(
            file_map, block_map) is not None:
        return None
    return file_map


def _cycle_state_v8(events, dispatches, instance_id,
                    head, content, generated,
                    iteration):
    """The cycle walk's state at one package head
    under the file grain (office-cycle-v8), derived
    from the record alone: the same working set,
    journal chain and per-block read facts the
    standing derivation weighs — the blocks remain
    the evidence and carriage units — grouped
    under their files, the walk's unit. A file's
    read stands iff every one of its blocks' reads
    stands carried (the block rule, per block);
    its read completes at the last completing
    dispatch among its blocks. A file is done iff
    its read stands AND an accepted journal
    transition stands after its read completed —
    transitions consumed in file order, one
    transition closing at most one file, so a
    single append after a batch of reads cannot
    close two files, and no append between a
    file's parts can close the file before its
    read stands whole. A transition closing no
    file is attributed to the file current at its
    writing, or to none where the walk already
    stood complete. The current file is the first
    file not done; where none stands, the walk is
    at SUMMARIZE. Returns None where the sealed
    block map or file grouping does not stand or
    the case designates no journal."""
    block_map = _cycle_blocks(content, generated)
    file_map = _cycle_files(content, generated)
    journal_path = _staged_journal_path(content)
    if block_map is None or file_map is None or \
            journal_path is None:
        return None
    working_set = _derive_working_set(
        events, dispatches, instance_id, head)
    entries = working_set["entries"]
    requested = _tree_requested(events, head)
    writes = _tree_journal_writes(
        events, dispatches, requested, instance_id,
        head, journal_path)
    chain = _journal_chain(writes)
    facts = {}
    for index, block in enumerate(block_map):
        stands, read_seq, entry = _block_read_facts(
            entries, block)
        facts[block["block_id"]] = {
            "read_stands": stands,
            "read_seq": read_seq,
            "entry": entry,
            "cycle": index + 1}
    blocks = []
    for index, block in enumerate(block_map):
        blocks.append(dict(
            block,
            read_stands=facts[
                block["block_id"]]["read_stands"],
            read_seq=facts[block["block_id"]][
                "read_seq"],
            entry=facts[block["block_id"]]["entry"],
            cycle=index + 1))
    blocks_by_id = {block["block_id"]: block
                    for block in blocks}
    files = []
    for number, group in enumerate(file_map, 1):
        mine = [blocks_by_id[block_id]
                for block_id in group["block_ids"]]
        read_stands = all(
            block["read_stands"] for block in mine)
        completion_seq = max(
            (block["read_seq"] for block in mine),
            default=None) if read_stands else None
        files.append({
            "file_id": group["file_id"],
            "address": group["address"],
            "block_ids": list(group["block_ids"]),
            "blocks": mine,
            "read_stands": read_stands,
            "completion_seq": completion_seq,
            "number": number})
    closed = {}
    attribution = {}
    for transition in chain["transitions"]:
        target = None
        for entry in files:
            if entry["number"] in closed:
                continue
            if entry["read_stands"] and \
                    entry["completion_seq"] is not None \
                    and entry["completion_seq"] < \
                    transition["write_seq"]:
                target = entry
                break
        if target is not None:
            closed[target["number"]] = transition
            attribution[transition["write_seq"]] = \
                target["number"]
        else:
            following = next(
                (entry for entry in files
                 if entry["number"] not in closed),
                None)
            attribution[transition["write_seq"]] = \
                following["number"] \
                if following is not None else None
    current = None
    for entry in files:
        entry["done"] = entry["number"] in closed
        if entry["done"]:
            entry["state"] = "done"
        elif current is None:
            entry["state"] = "current"
            current = entry["number"]
        else:
            entry["state"] = "pending"
        if entry["state"] == "current" and \
                not entry["read_stands"] and \
                len(entry["blocks"]) > 1:
            # A multi-part file mid-step names its
            # standing parts inside its state line —
            # state, not a task list: the parts are
            # plumbing, and the count is where the
            # file stands, nothing more.
            parts_read = sum(
                1 for block in entry["blocks"]
                if block["read_stands"])
            entry["state"] = (
                f"current ({parts_read} of "
                f"{len(entry['blocks'])} parts read)")
        # Each part stands in its file's state: the
        # flat block list carries the standing state
        # word of its file, so every consumer of the
        # block list reads a state under this
        # contract too.
        for block in entry["blocks"]:
            block["state"] = entry["state"]
    return {
        "block_map": block_map,
        "blocks": blocks,
        "file_map": file_map,
        "files": files,
        "current": current,
        "journal_path": journal_path,
        "writes": writes,
        "chain": chain,
        "attribution": attribution,
        "working_set": working_set,
        "entries": entries,
        "requested": requested}


def _tree_computation(tree, cstate, iteration,
                      deliverable_filed):
    """The sealed tree's node states at one package
    head (office-cycle-v9, the build scope of
    2026-11-26 as amended): derived from the SAME
    derivation the cycle packages stand on — the
    file-grain cycle state over the record — never a
    second reading of the record. One computation;
    the package's tree block and the speaking
    refusal both render from it, so the two can
    never disagree (the plan's anti-interlacing
    rule). A node stands done only on its recorded
    act: a gather node on its read standing whole
    AND its journal transition standing (the settled
    method, INDEX 575 — read everything but
    journaled nothing is NOT finished gathering);
    summarize and deliver on the brief standing
    filed. A pending node whose dependency stands
    unfilled is blocked, and its fact names the
    unfilled dependency."""
    files = {entry["address"]: entry
             for entry in cstate["files"]}
    states = {}
    nodes = []
    for node in tree["nodes"]:
        kind = node["kind"]
        facts = []
        state_name = "pending"
        if kind == "onboarding":
            state_name = "done" if iteration > 1 \
                else "current"
        elif kind == "gather":
            entry = files.get(node["source"])
            if entry is None:
                facts.append(
                    "this source stands outside the "
                    "sealed file map; the office "
                    "cannot derive its state")
            else:
                if entry["done"]:
                    state_name = "done"
                elif str(entry["state"]).startswith(
                        "current"):
                    state_name = "current"
                if entry["read_stands"]:
                    facts.append(
                        f"you hold this source whole "
                        f"({len(entry['blocks'])} "
                        f"part(s))")
                    if entry["done"]:
                        facts.append(
                            "its journal bit stands "
                            "written")
                    else:
                        facts.append(
                            "reads of it are closed; "
                            "your next act is to write "
                            "its journal bit from what "
                            "you hold")
                else:
                    read_parts = sum(
                        1 for block in entry["blocks"]
                        if block["read_stands"])
                    if read_parts:
                        facts.append(
                            f"{read_parts} of "
                            f"{len(entry['blocks'])} "
                            f"parts read so far")
        elif kind in ("summarize", "deliver"):
            if deliverable_filed:
                state_name = "done"
            elif node["depends_on"] and all(
                    states.get(dep) == "done"
                    for dep in node["depends_on"]):
                state_name = "current"
        states[node["id"]] = state_name
        nodes.append({"id": node["id"],
                      "label": node["label"],
                      "kind": kind,
                      "state": state_name,
                      "facts": facts,
                      "workaround":
                          node.get("workaround") or ""})
    labels = {node["id"]: node["label"]
              for node in tree["nodes"]}
    for node, computed in zip(tree["nodes"], nodes):
        if computed["state"] != "pending":
            continue
        # Blocked names a dependency that itself
        # stands unstarted or blocked; a dependency
        # standing current is the work in hand, and
        # this node is simply next.
        unfilled = [dep for dep in node["depends_on"]
                    if states.get(dep) in
                    ("pending", "blocked")]
        if unfilled:
            computed["state"] = "blocked"
            states[node["id"]] = "blocked"
            computed["facts"].append(
                "waiting on: " + "; ".join(
                    labels[dep] for dep in unfilled))
    return {"title": tree["title"], "nodes": nodes}


def _tree_text(computation):
    """The tree as the worker reads it: one line per
    node with its state, its facts beneath it, and a
    node's workaround where the node stands current
    or blocked and carries one (INDEX 572: the
    workaround rides on the node it answers)."""
    marks = {"done": "[done]", "current": "[current]",
             "pending": "[pending]",
             "blocked": "[blocked]"}
    lines = [f"Process tree — {computation['title']}"]
    for node in computation["nodes"]:
        lines.append(
            f"{marks[node['state']]} {node['label']}")
        for fact in node["facts"]:
            lines.append(f"    {fact}")
        if node["workaround"] and \
                node["state"] in ("current", "blocked"):
            lines.append(
                f"    Workaround: {node['workaround']}")
    return "\n".join(lines)


def _tree_speaking_refusals(tool_results, computation):
    """The speaking refusal (office-cycle-v9): where
    a doorway refusal in this package's results names
    an exhausted bound for a read tool, the refusal
    gains the correction the tree computation
    derives — the sources the worker already holds
    whole, and, where a held source's journal bit
    stands unwritten, the next act (Amendment 2:
    the correction names the next action, not only
    the state). The doorway's ground itself is
    untouched; this is presentation, from the one
    shared computation."""
    held = [node for node in computation["nodes"]
            if node["kind"] == "gather" and any(
                fact.startswith("you hold this source")
                for fact in node["facts"])]
    if not held:
        return
    unjournaled = [node for node in held if any(
        "next act is to write its journal bit" in fact
        for fact in node["facts"])]
    for entry in tool_results:
        if entry.get("outcome") != "refused" or \
                entry.get("refusal_class") != \
                "doorway_refused":
            continue
        error = entry.get("error") or ""
        if "bound for tool" not in error or \
                "exhausted" not in error or not any(
                    tool in error for tool in
                    ("sandbox.read", "sandbox.read_range")):
            continue
        names = "; ".join(node["label"] for node in held)
        correction = (
            f" You already hold, whole: {names}. "
            f"Another read is unnecessary.")
        if unjournaled:
            correction += (
                " Your next act is to write the "
                "journal bit for the held source that "
                "lacks one, from what you hold.")
        entry["error"] = error + correction


def _cycle_gate_owed_v8(cstate):
    """What the cycle gate owes at a wake under the
    file grain, from the derived file state:
    (file number, current file, ahead file) where
    the current file stands incomplete AND a later
    FILE's read stands carried in whole or in part
    — work ran ahead of the file it belongs to.
    None anywhere else: reads of the current file's
    own parts, however many land at once, owe no
    gate — the parts are plumbing inside the file's
    step, and the honest path owes none either."""
    if cstate is None or cstate["current"] is None:
        return None
    current = cstate["current"]
    for entry in cstate["files"]:
        if entry["number"] > current and \
                any(block["read_stands"]
                    for block in entry["blocks"]):
            mine = cstate["files"][current - 1]
            return current, mine, entry
    return None


def _cycle_gate_owed(cstate):
    """What the cycle gate owes at a wake, from the
    derived cycle state: (cycle, block, ahead block)
    where the current cycle stands incomplete AND a
    later block's read stands carried — work ran ahead
    of the cycle it belongs to. None anywhere else:
    the honest path, which pulls each block at its own
    cycle, owes no gate."""
    if cstate is None or cstate["current"] is None:
        return None
    current = cstate["current"]
    for block in cstate["blocks"]:
        if block["cycle"] > current and \
                block["read_stands"]:
            mine = cstate["blocks"][current - 1]
            return current, mine, block
    return None


def _cycle_presented_block_ids(events, dispatches,
                               instance_id, content,
                               generated,
                               iteration_heads):
    """The block ids whose content has already been
    presented at an earlier wake of this run, derived
    from the record alone: for each earlier iteration
    (its number and its package head, from the
    record's iteration events), the cycle state at
    that head — where the iteration's current block's
    read stood, that block's content stood in front of
    the worker at that wake, presented once, at its
    cycle. (A block re-pulled in the response just
    before a wake is presented again in that wake's
    own results carriage, as that response's newest
    result — a presentation of the pull, not of the
    cycle, and no bar to the cycle's own presentation
    where the block is a later one: a later block's
    content is never presented before its cycle.)"""
    presented = set()
    for number, head in iteration_heads:
        earlier = _cycle_state(
            events, dispatches, instance_id, head,
            content, generated, number)
        if earlier is None or \
                earlier["current"] is None:
            continue
        block = earlier["blocks"][earlier["current"] - 1]
        if block["read_stands"]:
            presented.add(block["block_id"])
    return presented


def _v8_current_part(cstate, presented):
    """The part whose content a v8 cycle package
    presents: of the current file's blocks, those
    whose read stands, whose content stands
    carriable and which no earlier package has
    presented — the one whose read completed last
    (the most recent part to land). None where no
    part qualifies: the file unread, or every
    standing part already presented once."""
    if cstate is None or cstate["current"] is None:
        return None
    current_file = cstate["files"][
        cstate["current"] - 1]
    candidates = [
        block for block in current_file["blocks"]
        if block["read_stands"]
        and block["block_id"] not in presented
        and _block_content(
            cstate["entries"], block) is not None]
    if not candidates:
        return None
    return max(candidates,
               key=lambda block: block["read_seq"]
               if block["read_seq"] is not None
               else -1)


def _v8_presented_parts(events, dispatches,
                        instance_id, content,
                        generated, iteration_heads):
    """The block ids whose content has already been
    presented at an earlier wake of this run under
    the file grain, derived from the record alone:
    the earlier heads walked in order, the file
    state re-derived at each, and the part the
    selection rule would have presented there
    marked presented — so a part's content stands
    in front of the worker exactly once, at the
    first wake after its read stands within its
    file's step, and never again."""
    presented = set()
    for number, head in iteration_heads:
        earlier = _cycle_state_v8(
            events, dispatches, instance_id, head,
            content, generated, number)
        if earlier is None or \
                earlier["current"] is None:
            continue
        part = _v8_current_part(earlier, presented)
        if part is not None:
            presented.add(part["block_id"])
    return presented


def _cycle_split_carriage_v8(tool_results, dispatches,
                             cstate, current,
                             block_content_part):
    """The split-on-return carriage at the file
    grain (office-cycle-v8): the standing rule
    with the file as its unit. A read result of
    the CURRENT FILE rides: stubbed to the
    block_content component where its part is the
    part presented there, and dropped to its
    pointer where it is any other part of the
    file — an earlier part stands as its pointer
    in the file's state, its content presented
    when it landed and not again. A read result
    of any other file does not ride: its file
    stands as its pointer in the files component,
    and its content is presented within its own
    step. Pulling several parts of the current
    file in one answer is presented exactly this
    way — in sequence inside the step, the most
    recent part's content at the package's centre
    — and is neither punished nor rewarded. The
    journal's reads stand as they arrived, and
    listings, searches, writes, failures and
    refusals stand as they arrived."""
    dispatch_tools = {
        did: d.get("tool")
        for did, d in dispatches.items()}
    current_file = cstate["files"][current - 1] \
        if current is not None else None
    carried = []
    for entry in copy.deepcopy(tool_results):
        if entry.get("outcome") != "result":
            carried.append(entry)
            continue
        tool = dispatch_tools.get(
            entry.get("dispatch_id"))
        if tool not in ("sandbox.read",
                        "sandbox.read_range"):
            carried.append(entry)
            continue
        result = entry.get("result")
        if not isinstance(result, dict):
            carried.append(entry)
            continue
        path = result.get("path")
        if path == cstate["journal_path"]:
            carried.append(entry)
            continue
        if current_file is None or \
                path != current_file["address"]:
            continue
        if block_content_part is not None:
            served = _working_set_served(tool, result)
            part = block_content_part
            if served.get("kind") == "whole" and \
                    part["line_start"] is None:
                entry["result"] = _carriage_stub(
                    result, "block_content")
                carried.append(entry)
                continue
            if served.get("kind") == "range" and \
                    served.get("start_line") == \
                    part["line_start"] and \
                    served.get("end_line") == \
                    part["line_end"]:
                entry["result"] = _carriage_stub(
                    result, "block_content")
                carried.append(entry)
                continue
            continue
        if "content" not in result:
            # No part stands presented in this
            # package: a re-pull of a part of the
            # current file whose content already
            # stood presented is answered with its
            # content, restored from the working
            # set's carried entry for the same
            # content — the standing split rule's
            # re-pull answer, at the file grain.
            restored = None
            for candidate in cstate["entries"]:
                if candidate.get("path") == path and \
                        candidate.get(
                            "content_sha256") == \
                        result.get("content_sha256") \
                        and "content" in candidate:
                    restored = candidate["content"]
                    break
            if restored is not None:
                presented_result = {
                    key: value
                    for key, value in result.items()
                    if key not in (
                        "single_carriage",
                        "presented_in")}
                presented_result["content"] = restored
                entry["result"] = presented_result
        carried.append(entry)
    return carried


def _cycle_split_carriage(tool_results, dispatches,
                          cstate, current,
                          block_content_stands):
    """The split-on-return carriage (office-cycle-
    v2): the newest response's results, carried only
    where the wake presents them. A block read's
    result — a read or range read of a briefcase
    block's file — rides only where its block is the
    current cycle's: stubbed to the block_content
    component where the content stands there (the
    block freshly read), or answered with its
    content where the pull is a re-pull of the
    current block after its cycle presentation (the
    content restored from the working set's carried
    entry for the same content, where that entry
    stands; the recorded result's own provenance
    stands either way). Every other block's read
    result does not ride — its block stands as its
    pointer in the blocks component, and its content
    is presented when its cycle comes; the pull is
    neither punished nor rewarded. The journal's
    reads stand as they arrived (his pull of his own
    notebook is answered), and listings, searches,
    writes, failures and refusals are not block
    contents: they stand as they arrived. A pure
    function of cycle position: the same response
    answered at a different position carries
    differently, and no arrival grouping survives
    into the carriage."""
    dispatch_tools = {
        did: d.get("tool")
        for did, d in dispatches.items()}
    blocks_by_address = {}
    for block in cstate["blocks"]:
        blocks_by_address.setdefault(
            block["address"], []).append(block)
    carried = []
    for entry in copy.deepcopy(tool_results):
        if entry.get("outcome") != "result":
            carried.append(entry)
            continue
        tool = dispatch_tools.get(
            entry.get("dispatch_id"))
        if tool not in ("sandbox.read",
                        "sandbox.read_range"):
            carried.append(entry)
            continue
        result = entry.get("result")
        if not isinstance(result, dict):
            carried.append(entry)
            continue
        path = result.get("path")
        if path == cstate["journal_path"]:
            carried.append(entry)
            continue
        served = _working_set_served(tool, result)
        cycles = set()
        for block in blocks_by_address.get(path, []):
            if served.get("kind") == "whole":
                cycles.add(block["cycle"])
            elif served.get("kind") == "range" and \
                    isinstance(
                        served.get("start_line"), int) \
                    and isinstance(
                        served.get("end_line"), int):
                first = block["line_start"] \
                    if block["line_start"] is not None \
                    else 1
                last = block["line_end"] \
                    if block["line_end"] is not None \
                    else served["end_line"]
                if served["start_line"] <= last and \
                        first <= served["end_line"]:
                    cycles.add(block["cycle"])
        if not cycles:
            carried.append(entry)
            continue
        if current is None or current not in cycles:
            continue
        if block_content_stands:
            if "content" in result or \
                    result.get("presented_in") == \
                    "working_set":
                entry["result"] = _carriage_stub(
                    result, "block_content")
            carried.append(entry)
            continue
        if "content" not in result:
            restored = None
            for candidate in cstate["entries"]:
                if candidate.get("path") == path and \
                        candidate.get(
                            "content_sha256") == \
                        result.get("content_sha256") \
                        and "content" in candidate:
                    restored = candidate["content"]
                    break
            if restored is not None:
                presented = {
                    key: value
                    for key, value in result.items()
                    if key not in (
                        "single_carriage",
                        "presented_in")}
                presented["content"] = restored
                entry["result"] = presented
        carried.append(entry)
    return carried


def _cycle_access(block, catalogue):
    """A block's way in: the exact call that pulls it,
    read from the catalogue the record derives, so the
    way names a tool the worker actually holds over
    that block's file — sandbox.read_range with the
    block's sealed range where read_range is granted
    over the file (a range block's own call), else
    sandbox.read of the whole file where read is
    granted (a whole-file block's call, and a range
    block's fallback — the block still counts read
    whole). None where no granted call pulls the
    block: the poster and the cycle then carry no way
    rather than a call the worker cannot make."""
    address = block["address"]

    def granted(tool):
        for entry in catalogue or []:
            if not isinstance(entry, dict) or \
                    entry.get("tool") != tool:
                continue
            ceiling = entry.get("scope_ceiling")
            prefix = ceiling.get("path_prefix") \
                if isinstance(ceiling, dict) else None
            if isinstance(prefix, str) and (
                    address == prefix
                    or address.startswith(prefix + "/")):
                return True
        return False

    if block.get("line_start") is not None and \
            granted("sandbox.read_range"):
        return {"tool": "sandbox.read_range",
                "parameters": {
                    "path": address,
                    "start_line": block["line_start"],
                    "end_line": block["line_end"]}}
    if granted("sandbox.read"):
        return {"tool": "sandbox.read",
                "parameters": {"path": address}}
    return None


def _cycle_offer_set(catalogue, cstate, summarize):
    """The wire's offer set (the plan §5): the tools
    the current package offers — the current cycle's
    tools (the block pulls: sandbox.read and
    sandbox.read_range) plus the journal tools
    (sandbox.write, the append; sandbox.read, the
    read-back) — as catalogue entries, one per tool
    name, in catalogue order. At SUMMARIZE the offer
    is the journal tools alone (read + write). The
    offer governs the wire only: name resolution runs
    against the full sealed catalogue in the record,
    so a granted call resolves whether or not it was
    offered, and an ungranted call is refused at the
    doorway exactly as before — the offer never widens
    or narrows the grant boundary."""
    if summarize:
        wanted = ("sandbox.read", "sandbox.write")
    else:
        wanted = ("sandbox.read", "sandbox.read_range",
                  "sandbox.write")
    offered = []
    seen = set()
    for entry in catalogue or []:
        name = entry.get("tool")
        if name in wanted and name not in seen:
            seen.add(name)
            offered.append(copy.deepcopy(entry))
    return offered


STAGED_DIRECTIONS = {
    "memory": (
        "Onboarding stage 1 of 4: your memory. Nothing "
        "is asked of you at this wake but to take it "
        "in — no work is produced during onboarding. "
        "Answer {\"outcome\": \"acknowledge\"} and your "
        "next wake brings your case."),
    "case": (
        "Onboarding stage 2 of 4: your case — the frame "
        "of the job you were assembled for. Take it in; "
        "no work is produced during onboarding. Answer "
        "{\"outcome\": \"acknowledge\"} and your next "
        "wake brings your files."),
    "files": (
        "Onboarding stage 3 of 4: your files. These are "
        "pointers to pull from, not the files "
        "themselves. Your task arrives at the next "
        "wake."),
    "task": (
        "Onboarding stage 4 of 4: your task. This is "
        "the work. Your tool menu below is grouped by "
        "the job's phases — Gather, Compose, Deliver. "
        "Begin."),
    "dashboard": (
        "Your onboarding is complete. This is your "
        "dashboard wake: where you stand, your newest "
        "results, everything you have gathered so far, "
        "and pointers back into your briefcase."),
}

# The pointer-rule successor's wording (INDEX 568): the
# same stages and furniture as v1, with the two texts
# that describe the package's own shape telling the
# pointer truth — a pull's content is shown once, in
# the wake right after the pull, and stands as a
# pointer after; the files-stage introduction says so
# where v1 promised the content would be carried
# forward in front of him, and the dashboard direction
# names pointers where v1 named everything gathered.
STAGED_FILES_INTRO_V2 = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is shown "
    "to you whole in the wake right after you pull "
    "it, and after that it stands in your working set "
    "as a pointer — its address, its size, and the "
    "office's record of your having pulled it — so "
    "pull it again whenever you need its words in "
    "front of you. "
    "Your tools are offered from this wake on. Below "
    "the map, one call stands worked as an example — "
    "a real call the office made on one of the files "
    "in the map while your briefcase was being "
    "stocked, with what came back; yours will look "
    "like this.")
STAGED_FILES_INTRO_NO_EXAMPLE_V2 = (
    "Your briefcase holds the job's files — the files "
    "your task needs. What stands below are pointers, "
    "not contents: each file's address, what it is, "
    "and its way in — the exact call that pulls it, "
    "naming a tool you hold. The contents are yours "
    "to pull when the work needs them, through the "
    "doorway tools (sandbox.list shows a file's size, "
    "line count and headings — or, on a directory "
    "such as sources itself, the entries standing in "
    "it; sandbox.read pulls a whole file) or the "
    "shell in your room. That is "
    "how the briefcase works: what you pull is shown "
    "to you whole in the wake right after you pull "
    "it, and after that it stands in your working set "
    "as a pointer — its address, its size, and the "
    "office's record of your having pulled it — so "
    "pull it again whenever you need its words in "
    "front of you. "
    "Your tools are offered from this wake on — if "
    "you want, list a file from the map now and see "
    "its shape standing.")
STAGED_DIRECTIONS_V2 = {
    "memory": STAGED_DIRECTIONS["memory"],
    "case": STAGED_DIRECTIONS["case"],
    "files": STAGED_DIRECTIONS["files"],
    "task": STAGED_DIRECTIONS["task"],
    "dashboard": (
        "Your onboarding is complete. This is your "
        "dashboard wake: where you stand, your newest "
        "results, pointers to everything you have "
        "gathered so far, and pointers back into your "
        "briefcase."),
}

# The pointer working set's own note (INDEX 568): the
# component the dashboard carries in place of the
# content-carrying set — orientation, not a data dump.
WORKING_SET_POINTER_NOTE = (
    "What you have gathered so far, standing as "
    "pointers: each entry's content was shown to you "
    "whole in the wake right after you gathered it, "
    "and the material itself stands in your room at "
    "its address — pull it again when you need its "
    "words in front of you. The office's record of "
    "what you have read stands in full behind these "
    "pointers; an entry marked content_carried: false "
    "did not fit the working-set budget when it was "
    "gathered, and its provenance stands here the "
    "same way.")

# One plain sentence per pointer entry (INDEX 568):
# the material is in his room at that address, he can
# pull it again with the named access call when he
# needs the words, and the office's record of his
# having read it stands regardless. Where no granted
# call covers the address, the sentence says that
# instead of naming a call he does not hold.
STAGED_POINTER_SENTENCE = (
    "It stands in your room at {path} — pull it "
    "again with {tool} on that address when you need "
    "its words in front of you; the office's record "
    "of your having read it stands regardless of "
    "what any later package carries.")
STAGED_POINTER_SENTENCE_NO_WAY = (
    "It stands in your room at {path}; no tool you "
    "hold pulls it directly, and the office's record "
    "of your having read it stands regardless of "
    "what any later package carries.")


def _staged_stage(iteration):
    """The onboarding stage a wake presents, as a pure
    function of its 1-based iteration number: the first
    four wakes walk memory, case, files, task; every
    later wake is a dashboard."""
    stages = _tool_policy.PRESENTATION_STAGES
    if 1 <= iteration <= 4:
        return stages[iteration - 1]
    return stages[4]


def _staged_onboarding(content):
    """The case's onboarding component under the same
    well-formedness rule the ordered package applies:
    the component, or None where the case carries none
    (or carries it malformed)."""
    onboarding = (content or {}).get("onboarding")
    if not (isinstance(onboarding, dict)
            and isinstance(onboarding.get("headline"), str)
            and isinstance(onboarding.get("deliverable"), str)
            and isinstance(onboarding.get("text"), str)):
        return None
    return onboarding


def _staged_journal_path(content):
    """The case's designated journal path under the same
    rule the journal component applies: the path, or None
    where no journal is designated."""
    designated = (content or {}).get("journal")
    if not isinstance(designated, str) or \
            not designated.startswith("scratch/") or \
            ".." in designated.split("/"):
        return None
    return designated


def _staged_snapshot(content):
    """Where the worker stands at his first wake (INDEX
    549): the settled results of the case's opening
    conversation, verbatim, where an opening record
    stands with settled results; the plain statement
    that nothing was settled where none stand.
    Record-derived only — the case's own opening
    record, never a composed picture of the worker or
    the job."""
    opening = (content or {}).get("opening")
    settled = opening.get("settled") \
        if isinstance(opening, dict) else None
    if isinstance(settled, list) and settled and \
            all(isinstance(item, str) for item in settled):
        return {"note": STAGED_SNAPSHOT_NOTE,
                "settled": copy.deepcopy(settled)}
    return {"note": STAGED_SNAPSHOT_EMPTY, "settled": []}


def _staged_access_way(catalogue, address):
    """A needed file's way in (INDEX 549): the concrete
    call that pulls it — sandbox.read where a catalogue
    entry grants it over the file's address, else
    sandbox.list likewise — read from the catalogue the
    package itself offers, so the way names a tool the
    worker actually holds, over that file's own
    address. None where no granted read covers the
    address: the entry then carries no way rather than
    a call the worker cannot make."""
    if not isinstance(address, str):
        return None
    for tool in ("sandbox.read", "sandbox.list"):
        for entry in catalogue or []:
            if not isinstance(entry, dict) or \
                    entry.get("tool") != tool:
                continue
            ceiling = entry.get("scope_ceiling")
            prefix = ceiling.get("path_prefix") \
                if isinstance(ceiling, dict) else None
            if isinstance(prefix, str) and (
                    address == prefix
                    or address.startswith(prefix + "/")):
                return {"tool": tool,
                        "parameters": {"path": address}}
    return None


def _worked_example_honoured(example, contract=None):
    """The sealed worked example the loop presents
    (round nine's correction pair, INDEX 548): the
    generated record's example, where it stands
    well-formed — the demonstration call and the
    performer's whole result, internally consistent
    (its hash and byte count its content's, its path
    the call's). A seal standing in any other shape is
    not presented; the checker reports it.

    The well-formed shape is the sealed contract's
    own (the calibration): under the first contract,
    the listing call and the listing performer's
    result, exactly as round nine presented them;
    under the pointer-rule successor, the read call
    and the read performer's whole result. Each
    population honours only its own form."""
    if not isinstance(example, dict) or \
            set(example) != {"tool", "path", "result"}:
        return None
    if contract in (
            _tool_policy.PRESENTATION_CONTRACT_V2,
            _tool_policy.PRESENTATION_CONTRACT_V3):
        return _worked_example_read_honoured(example)
    if example.get("tool") != "sandbox.list":
        return None
    path = example.get("path")
    result = example.get("result")
    if not isinstance(path, str) or not path or \
            not isinstance(result, dict) or \
            set(result) != {"path", "content",
                            "content_bytes",
                            "content_sha256",
                            "authority_path", "size_bytes",
                            "line_count"}:
        return None
    content = result.get("content")
    if result.get("path") != path or \
            not isinstance(content, str) or \
            result.get("content_bytes") != len(
                content.encode("utf-8")) or \
            result.get("content_sha256") != hashlib.sha256(
                content.encode("utf-8")).hexdigest() or \
            result.get("authority_path") not in (
                "source", "scratch") or \
            not isinstance(result.get("size_bytes"), int) \
            or isinstance(result.get("size_bytes"), bool) \
            or result.get("size_bytes") < 0 or \
            not isinstance(result.get("line_count"), int) \
            or isinstance(result.get("line_count"), bool) \
            or result.get("line_count") < 0:
        return None
    return copy.deepcopy(example)


def _worked_example_read_honoured(example):
    """The read demonstration's honour rule (the
    calibration): the sealed example under the
    pointer-rule contract, where it stands well-formed
    — a sandbox.read call and the read performer's
    whole result under the working-set contract (the
    file's whole content with its hash, byte count and
    authority path), internally consistent. A seal
    standing in any other shape is not presented; the
    checker reports it."""
    if example.get("tool") != "sandbox.read":
        return None
    path = example.get("path")
    result = example.get("result")
    if not isinstance(path, str) or not path or \
            not isinstance(result, dict) or \
            set(result) != {"path", "content",
                            "content_bytes",
                            "content_sha256",
                            "authority_path"}:
        return None
    content = result.get("content")
    if result.get("path") != path or \
            not isinstance(content, str) or \
            result.get("content_bytes") != len(
                content.encode("utf-8")) or \
            result.get("content_sha256") != hashlib.sha256(
                content.encode("utf-8")).hexdigest() or \
            result.get("authority_path") not in (
                "source", "scratch"):
        return None
    return copy.deepcopy(example)


def _stage_gate_what_arrived(stage):
    """What the stage gate's correction says arrived
    (round nine's correction pair, INDEX 548): a
    contribution, at the stage it was offered, before
    the task had been presented — the gate event's own
    stage, in the worker's terms."""
    return (f"a contribution, offered at the {stage} "
            f"stage of your onboarding, before your "
            f"task had been presented")


def _presentation_core(package, working_set_hash,
                       pointer_form=False):
    """The staged package's committed core: the package
    itself, with its two bulk references standing by
    their own commitments — the tool results by their
    recorded identities (dispatch, request, outcome,
    event), in presented order, and the working set by
    the hash its own commitment already records. Every
    other value stands verbatim, so a skipped stage, a
    reordered stage, a dashboard carrying the case dump,
    or any content standing twice diverges from the
    record's re-derivation.

    Under the pointer-rule successor contract (INDEX
    568) the core takes the pointer form: the presented
    working set — the pointers themselves — stands in
    the core verbatim beside the record set's hash, so
    the commitment binds both the set the office
    derived and the exact pointer form the worker was
    shown. The tool results still stand by their
    identities: the pointer rule changes where content
    is presented, not what the record holds."""
    core = copy.deepcopy(package)
    results = core.pop("tool_results", [])
    core["tool_result_refs"] = [
        {"dispatch_id": entry.get("dispatch_id"),
         "request_id": entry.get("request_id"),
         "outcome": entry.get("outcome"),
         "event_seq": entry.get("event_seq")}
        for entry in results]
    if not pointer_form:
        core.pop("working_set", None)
    core["working_set_hash"] = working_set_hash
    return core


def _presentation_hash(package, working_set_hash,
                       pointer_form=False):
    """The staged presentation's commitment: SHA-256 over
    the canonical form of the package's core — the
    commitment LOOP_ITERATION records for an assembly
    under the presentation contract, which the checker
    verifies by independent reconstruction from the
    record."""
    return sha256_hex(canonical(
        _presentation_core(package, working_set_hash,
                           pointer_form)))


def _cycle_core(package, working_set_hash):
    """The office-cycle package's committed core: the
    staged core with the tools section standing by its
    offer alone. The catalogue rides no package (the
    plan §5: it is office stock — a poster on the wall,
    not package content), so the core binds the offered
    tools by NAME (offered_tools, in offered order);
    their definitions are the sealed catalogue's own,
    re-derived from the record by both sides, and the
    adapter's wire framing of them is not package
    content. The per-call estimate (the plan §6) runs
    over this same core — the one serialization the
    loop, the checker, the driver and the rehearsal
    all reproduce byte-identically from the record:
    his position plus one block."""
    core = _presentation_core(package, working_set_hash,
                              pointer_form=False)
    offered = core.pop("tools", [])
    core["offered_tools"] = [
        entry.get("tool") for entry in offered]
    return core


def _cycle_presentation_hash(package, working_set_hash):
    """The cycle presentation's commitment: SHA-256
    over the canonical form of the package's cycle
    core."""
    return sha256_hex(canonical(
        _cycle_core(package, working_set_hash)))


def _translation_error_text(entry, offered_names):
    """The N16 error result for a translation refusal
    (native adapter piece): the examined templates of the
    scope, implemented as written — the call it answers,
    the decision in plain terms, and the explicit statement
    that nothing was dispatched for that call. It states
    what was decided and nothing else: no record internals,
    no apology, no speculation."""
    refusal = entry.get("refusal_class")
    if refusal == "unknown_tool":
        return (
            f"Tool unavailable: '{entry.get('name')}' is "
            f"not one of the tools offered for this task. "
            f"Nothing was dispatched for this call. The "
            f"tools offered are: {', '.join(offered_names)}.")
    if refusal == "malformed_call":
        return (
            f"Call not accepted: {entry.get('refusal_detail')}. "
            f"Nothing was dispatched for this call.")
    if refusal == "invalid_arguments":
        return (
            f"Arguments invalid: "
            f"{entry.get('validation_constraint')}. Nothing "
            f"was dispatched for this call.")
    if refusal == "call_cap_exceeded":
        return (
            "Call not accepted: this response's call limit "
            "was already reached. Nothing was dispatched "
            "for this call.")
    return ""


def _doorway_error_text(ground):
    """The N16 error result for a doorway refusal of a
    bound native call: the doorway's ground in plain
    terms — the ground's own sentence with its record-
    internal citations (the R-numbered parentheticals)
    removed; the record itself keeps the ground whole —
    and the explicit statement that nothing was dispatched
    for that call."""
    plain = re.sub(r"\s*\([^)]*\bR[0-9]+[^)]*\)", "",
                   ground or "")
    plain = re.sub(r"\s+", " ", plain).strip()
    return (f"Request refused: {plain}. Nothing was "
            f"dispatched for this call.")


def _plain_ground(ground):
    """A doorway ground in plain terms — the ground's own
    sentence with its record-internal citations removed,
    the cleaning _doorway_error_text applies — standing
    alone, for the failure instruction's why (Ben's gate
    ruling, INDEX 475: a refusal states its reason in
    usable terms, not as a regulation citation)."""
    plain = re.sub(r"\s*\([^)]*\bR[0-9]+[^)]*\)", "",
                   ground or "")
    return re.sub(r"\s+", " ", plain).strip()


# The envelope gate's recogniser (door scope, 2026-11-24):
# the exact rule, stated once. A response that has ALREADY
# failed the text-outcome JSON parse is an attempted
# contribution when, and only when, its trimmed form opens
# with "{" and its first two keys are, in order, the
# outcome discriminator naming contribute and the text
# key opening a string value:
#   { "outcome" : "contribute" , "text" : " ...
# (whitespace flexible, nothing else admitted before or
# between the two keys). Anything else — malformed prose,
# another outcome's envelope, a contribute named later in
# the object — is not recognised and keeps the stall path.
_CONTRIBUTE_ENVELOPE_RE = re.compile(
    r'^\{\s*"outcome"\s*:\s*"contribute"\s*,'
    r'\s*"text"\s*:\s*"')


def _recognised_contribution_attempt(raw):
    """Whether `raw` (a response's exact content) is a
    recognisable attempted contribution under the gate's
    rule above."""
    if not isinstance(raw, str):
        return False
    return _CONTRIBUTE_ENVELOPE_RE.match(
        raw.strip()) is not None


def _response_content_of(seam):
    """The exact response content a seam observation
    carries: its own content field where the transport
    recorded one, else the L4 text derived from its
    captured L1 bytes, else None."""
    if not isinstance(seam, dict):
        return None
    content = seam.get("content")
    if isinstance(content, str):
        return content
    l1 = seam.get("l1_bytes")
    if isinstance(l1, (bytes, bytearray)):
        l4 = _evidence.derive_layers(bytes(l1)).get("L4") or {}
        if l4.get("present"):
            return l4.get("text")
    return None


def _filing_write(path, data):
    """The office filing's one write of bytes to disk
    (door scope): the staging write through which every
    filing and every filing rollback passes, named as a
    single seam so the filing's failure paths can be
    witnessed against the real call — the door
    rehearsal's partial-write double replaces exactly
    this function, and nothing else in the filing path
    writes content bytes."""
    path.write_bytes(data)


class Loop:
    """One activation's bounded run.

    Loop(doorway, instance_token, model, executor=None):
    doorway — the framework's doorway (the loop's only route
    to the record); instance_token — the instance's own
    credential, as packed by the generator; model — the
    callable invoked per iteration as
    model(package, budget=remaining, deadline=<the
    activation's absolute deadline>); executor — the A2
    executor, used to perform dispatches the loop records and
    to close in-flight accounting at a stall. Without an
    executor, dispatches the loop records stand unperformed
    (their outcomes are recorded uncertain when accounting
    must close) — a loop that means to do tool work is given
    one.
    """

    def __init__(self, doorway, instance_token, model,
                 executor=None, evidence_store=None):
        self.doorway = doorway
        self.token = instance_token
        self.model = model
        self.executor = executor
        # Response-evidence piece: the evidence store's
        # root (the run directory; artifacts land in its
        # responses/ subdirectory under the store
        # contract). Where a store is given, the loop runs
        # the evidence sequence — CALL_ENTERED before each
        # call, the seam's evidence persisted and the
        # disposition committed before any effect of the
        # answer. Where none is given, the loop runs
        # exactly as it always has — but only for a
        # callable that is not a provider seam: a callable
        # publishing the seam (the adapter's
        # last_response_evidence channel, which the
        # transports fill) is a provider callable, and
        # running one without a store would silently
        # ungovern a real worker (build examination,
        # INDEX 314). run() refuses that pairing, fail
        # closed, before any iteration; a plain scripted
        # callable — no seam channel — is the genuinely
        # legacy path and runs ungoverned as before.
        self.evidence_store = evidence_store
        # The road's accounting (the office-cycle
        # contract): every package the loop builds, with
        # its canonical serialized size and its estimated
        # tokens under the one estimator — read by the
        # driver into the run's call ledger, beside the
        # captures' true wire bytes. An attribute of the
        # run, not of the record: the record's own
        # accounting is the iteration events and, where
        # the budget refuses a package, the refusal.
        self.call_estimates = []
        # The road's presentation events (the §6
        # amendment): every spill and shedding act the
        # road's presentation pass performs on a
        # package, read by the driver into the run's
        # report beside the adapter's transport events.
        # An attribute of the run, like the estimates.
        self.road_events = []

    # ------------------------------------------------------ run
    def run(self):
        """Run the activation to its outcome. Returns a result
        dict: {"ok": True, "outcome": "yield", "summary", ...}
        for a yield; {"ok": True, "outcome": "decline",
        "reason", ...} for a decline (caller-reported, nothing
        recorded for it); {"ok": False, "outcome": "stalled",
        "ground", "stall_event", ...} for a recorded stall;
        {"ok": False, "outcome": "not_run", "reason", ...}
        where the loop cannot begin at all (no standing
        activation, no bounds, an unestablishable anchor, an
        already-stalled activation) — in which case nothing is
        recorded and no model call is made."""
        if self.evidence_store is None and \
                hasattr(self.model, "last_response_evidence"):
            # Bypass by omission, closed (build
            # examination, INDEX 314): the callable is a
            # provider seam — it publishes response
            # evidence — and no evidence store stands to
            # receive it. The loop refuses rather than
            # take the ungoverned path: a missing store
            # must not silently turn a real worker into an
            # ungoverned one. Nothing is recorded and no
            # call is made; the refusal is the result.
            return {"ok": False, "outcome": "not_run",
                    "reason": "the callable publishes a "
                              "provider response-evidence "
                              "seam but no evidence store "
                              "was given; a provider worker "
                              "does not run ungoverned "
                              "(response-evidence piece)"}
        ctx = self._open_context()
        if isinstance(ctx, dict) and "not_run" in ctx:
            return ctx["not_run"]
        if ctx.get("tree") is not None:
            problem = self._stock_journal(ctx)
            if problem is not None:
                return {"not_run": {
                    "ok": False, "outcome": "not_run",
                    "instance_id": ctx["instance_id"],
                    "assembly_id": ctx["assembly_id"],
                    "reason": problem}}
        try:
            return self._run(ctx)
        finally:
            # The loop's context is local to the run and is
            # dropped at return; nothing here outlives the
            # call (evidenced disposal is Piece A5's).
            ctx.clear()

    def _stock_journal(self, ctx):
        """The v9 stocking rule (the build scope of
        2026-11-26, INDEX 602): where a tree stands
        sealed, the case's designated journal stands
        stocked before the first wake — created empty
        where none stands, an existing journal
        preserved untouched, never overwritten. The
        run of 2026-11-26 (demo-nemotron8) walked a
        worker in circles because the room directed a
        journal read against a file that did not
        exist; the office stocks its own furniture.
        Returns a problem naming why the run cannot
        begin, or None."""
        sandbox_dir = getattr(
            self.executor, "sandbox_dir", None)
        journal_path = _staged_journal_path(
            ctx.get("content") or {})
        if not sandbox_dir or not journal_path:
            return ("the tree stands sealed but the "
                    "journal cannot be stocked: the "
                    "executor names no sandbox or the "
                    "case designates no journal; no "
                    "loop (office-cycle-v9 stocking)")
        target = Path(sandbox_dir) / journal_path
        try:
            target.parent.mkdir(
                parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("", encoding="utf-8")
        except OSError as exc:
            return (f"the tree stands sealed but the "
                    f"journal could not be stocked at "
                    f"{journal_path}: {exc}; no loop "
                    f"(office-cycle-v9 stocking)")
        return None

    def _open_context(self):
        """Resolve the run's standing facts from the record —
        or the not_run result where the loop cannot begin.
        Nothing is recorded on any of these paths: a loop that
        cannot begin has no iteration to account and no stall
        ground that fits it (a stall names a bound the run
        reached; a run that never stood reached none)."""
        doorway = self.doorway
        instance_id = doorway._presented_instance(self.token)
        if instance_id is None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "reason": "the credential presented is not an "
                          "instance credential; the loop runs "
                          "only under an instance's own "
                          "credential (R44)"}}
        state = doorway.state()
        assembly_id, entry = doorway._assembly_entry_of_instance(
            state, instance_id)
        if entry is None or entry.get("activated_seq") is None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "reason": "the instance holds no standing "
                          "activation; the loop is "
                          "activation-bound (R49)"}}
        if doorway._activation_stall(state, instance_id) \
                is not None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "assembly_id": assembly_id,
                "reason": "the activation already stands "
                          "stalled; a stalled activation admits "
                          "no further loop (R50)"}}
        bounds = doorway._pinned_loop_bounds(state, entry)
        if bounds is None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "assembly_id": assembly_id,
                "reason": "the pinned case carries no loop "
                          "bounds; no bounds, no loop (R49)"}}
        remaining, problem = doorway.activation_remaining(
            instance_id)
        if problem is not None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "assembly_id": assembly_id,
                "reason": problem}}
        seat = entry.get("seat")
        content = doorway._pinned_case_content(state, entry)
        # Native-mode probe piece (probe scope §6): under a
        # probe-governed assembly, the adapter's mode is read
        # from the sealed packed package — the ASSEMBLY_PACKED
        # act's own payload, the same object the checker
        # verifies against the judgement. It is passed to the
        # model callable as a keyword only for governed
        # assemblies: a historical assembly's callable is
        # invoked exactly as it has always been.
        adapter_mode = None
        _generated_for_mode = doorway._generated_payload(
            assembly_id)
        if doorway._probe_governed(_generated_for_mode):
            packed = doorway._event_at(entry.get("packed_seq"))
            adapter_mode = (packed or {}).get(
                "payload", {}).get("adapter_mode")
        elif (_generated_for_mode or {}).get(
                "presentation_contract") in (
                _tool_policy.PRESENTATION_CONTRACT_V11,
                _tool_policy.PRESENTATION_CONTRACT_V12):
            # office-cycle-v8: the mode reaches the loop
            # from the sealed packed package exactly as
            # under the probe regime — the package the
            # judgement bound — except the mode standing
            # there is the office's declaration (the
            # director's rulings of 2026-11-25, 23:07 and
            # 23:08 MST: no probe stands in a v8 launch),
            # not the probe regime's decision. A v8 pack
            # carrying no declared mode admits no loop:
            # fail closed, never a silent default.
            packed = doorway._event_at(entry.get("packed_seq"))
            adapter_mode = (packed or {}).get(
                "payload", {}).get("adapter_mode")
            if adapter_mode is None:
                return {"not_run": {
                    "ok": False, "outcome": "not_run",
                    "instance_id": instance_id,
                    "assembly_id": assembly_id,
                    "reason": "the assembly is sealed under "
                              "office-cycle-v8 and its pack "
                              "carries no office-declared "
                              "adapter mode; a v8 run travels "
                              "in its declared mode or not "
                              "at all"}}
        # The door scope (2026-11-24): the delivery
        # declaration the loop honours is the one the
        # generator sealed into the assembly's record,
        # where it equals the pinned case's declaration
        # exactly — the case's word and the assembly's
        # seal, never one without the other. The working-
        # set declaration is read the same way, for the
        # gate's population.
        _generated = doorway._generated_payload(
            assembly_id) or {}
        _delivery = _generated.get("delivery")
        if not (isinstance(_delivery, dict)
                and _delivery.get("route") == _tool_policy
                .DELIVERY_ROUTE_CONTRIBUTION
                and (content or {}).get("delivery")
                == _delivery):
            _delivery = None
        # The presentation declaration (INDEX 544; the
        # pointer-rule successor, INDEX 568): the seal
        # names one of the two contracts — v1, or v2
        # under which a gathered entry's content is
        # presented once and stands as a pointer after.
        # The declared value rides the context beside
        # the boolean, so the staged builder renders the
        # sealed contract's own presentation; any other
        # seal declares nothing here, exactly as an
        # absent one does.
        _presentation_value = _generated.get(
            "presentation_contract")
        _presentation_declared = _presentation_value in (
            _tool_policy.PRESENTATION_CONTRACT,
            _tool_policy.PRESENTATION_CONTRACT_V2,
            _tool_policy.PRESENTATION_CONTRACT_V3,
            _tool_policy.PRESENTATION_CONTRACT_V4,
            _tool_policy.PRESENTATION_CONTRACT_V5,
            _tool_policy.PRESENTATION_CONTRACT_V6,
            _tool_policy.PRESENTATION_CONTRACT_V7,
            _tool_policy.PRESENTATION_CONTRACT_V8,
            _tool_policy.PRESENTATION_CONTRACT_V9,
            _tool_policy.PRESENTATION_CONTRACT_V10,
            _tool_policy.PRESENTATION_CONTRACT_V11,
            _tool_policy.PRESENTATION_CONTRACT_V12)
        # Round nine's correction pair (INDEX 548): the
        # worked example the files stage presents is the
        # one the generator sealed into the assembly's
        # record, honoured only under the presentation
        # contract and only standing well-formed — the
        # seal's word, never a loop-side composition.
        _worked_example = _worked_example_honoured(
            _generated.get("worked_example"),
            _presentation_value) \
            if _presentation_declared else None
        # Round ten (INDEX 552): the delivery-evidence
        # declaration the loop's door honours is read the
        # same way — the generator's seal, where it equals
        # the pinned case's own component exactly, standing
        # well-formed, and only where the delivery itself
        # stands (the gate guards the door; where no door
        # stands there is nothing to guard) and the
        # working-set contract stands declared (the
        # declaration speaks of the worker's working set).
        _delivery_evidence = _generated.get(
            "delivery_evidence")
        if not (isinstance(_delivery_evidence, dict)
                and set(_delivery_evidence) == {"addresses"}
                and isinstance(
                    _delivery_evidence.get("addresses"), list)
                and _delivery_evidence["addresses"]
                and all(isinstance(address, str) and address
                        for address in
                        _delivery_evidence["addresses"])
                and (content or {}).get("delivery_evidence")
                == _delivery_evidence
                and _delivery is not None
                and _generated.get("working_set_contract")
                == _tool_policy.WORKING_SET_CONTRACT):
            _delivery_evidence = None
        # The third gate (INDEX 557): the
        # delivery-length declaration the loop's door
        # honours is read the same way — the generator's
        # seal, where it equals the pinned case's own
        # component exactly, standing well-formed, and
        # only where the delivery itself stands (the
        # gate guards the door; where no door stands
        # there is nothing to guard). The floor speaks
        # of the contributed text, which stands wherever
        # the door stands, so no working-set declaration
        # is asked of it.
        _delivery_floor = _generated.get("delivery_floor")
        if not (isinstance(_delivery_floor, dict)
                and set(_delivery_floor) == {"min_words"}
                and isinstance(
                    _delivery_floor.get("min_words"), int)
                and not isinstance(
                    _delivery_floor.get("min_words"), bool)
                and _delivery_floor["min_words"] >= 1
                and (content or {}).get("delivery_floor")
                == _delivery_floor
                and _delivery is not None):
            _delivery_floor = None
        # The road (the §6 amendment, accepted
        # 2026-11-26): the loop's road standing is
        # read the same way as the other declarations
        # — the generator's seal, standing well-formed
        # under the one shape check. A seal that does
        # not stand governs nothing: the run travels
        # under the per-call budget exactly as before.
        _road = _generated.get("road")
        if not (isinstance(_road, dict)
                and _tool_policy.road_problem(_road)
                is None):
            _road = None
        # The process tree (office-cycle-v9): read
        # the same way — the generator's seal, standing
        # well-formed under the one shape check, and
        # governing only under its own contract. A
        # seal that does not stand governs nothing.
        _tree = _generated.get("tree")
        if not (isinstance(_tree, dict)
                and _tool_policy.tree_problem(_tree)
                is None
                and _presentation_value
                == _tool_policy.PRESENTATION_CONTRACT_V12):
            _tree = None
        return {
            "delivery": copy.deepcopy(_delivery),
            "working_set_declared":
                _generated.get("working_set_contract")
                == _tool_policy.WORKING_SET_CONTRACT,
            "presentation_declared":
                _presentation_declared,
            "presentation_contract":
                _presentation_value
                if _presentation_declared else None,
            "worked_example": _worked_example,
            "presentation_hash": None,
            "freshness_suspended":
                _generated.get("freshness_guard")
                == _tool_policy.FRESHNESS_GUARD_SUSPENDED,
            "deliverable_filed": None,
            "delivery_evidence": copy.deepcopy(
                _delivery_evidence),
            "delivery_gate_correction": None,
            "delivery_stage_gate_correction": None,
            "delivery_stage_gate_error": None,
            "delivery_evidence_gate_correction": None,
            "delivery_evidence_gate_error": None,
            "delivery_floor": copy.deepcopy(
                _delivery_floor),
            "road": copy.deepcopy(_road),
            "tree": copy.deepcopy(_tree),
            "road_blocked": None,
            "delivery_length_gate_correction": None,
            "delivery_length_gate_error": None,
            "tool_shape_gate_correction": None,
            "tool_shape_gate_error": None,
            "step_gate_correction": None,
            "cycle_gate_correction": None,
            "journal_gate_correction": None,
            "instance_id": instance_id,
            "assembly_id": assembly_id,
            "adapter_mode": adapter_mode,
            "seat": seat,
            "role": (state["seats"].get(seat) or {}).get("role"),
            "case_id": entry.get("case_id"),
            "case_version": entry.get("case_version"),
            "content": copy.deepcopy(content),
            "activated_seq": entry.get("activated_seq"),
            "bounds": bounds,
            # The cursor opens at the record's head as the
            # loop starts: the first package presents the
            # standing position, and everything recorded from
            # here is presented exactly once, as new.
            "cursor": state["head_seq"],
            "iterations": 0,
            "recorded": [],
            "refused": [],
            "dispatched": [],
            "call_timings": [],
        }

    def _run(self, ctx):
        doorway = self.doorway
        ceiling = ctx["bounds"]["step_ceiling"]
        while True:
            # (i) Bounds and deadline, before anything else:
            # a bound reached here stops the run before a
            # package is built or a call accounted.
            if ctx["iterations"] >= ceiling:
                return self._stall(ctx, "step_ceiling")
            remaining, problem = doorway.activation_remaining(
                ctx["instance_id"])
            if problem is not None:
                return self._stall(ctx, "runtime_failure",
                                   detail=problem)
            if remaining is not None and remaining <= 0:
                # Response-evidence piece (R4-3): under the
                # evidence regime this stall answers the
                # iteration that never began — its pre-call
                # step is the deadline standing expired at
                # its start.
                return self._stall(
                    ctx, "deadline",
                    terminal_step="deadline_at_start"
                    if self.evidence_store is not None
                    else None)

            # (ii) Construct and freeze the package from a
            # snapshot. A failure here is the loop's own —
            # runtime_failure — and counts no iteration: the
            # iteration event is recorded only for a package
            # that stands.
            package_started = time.monotonic()
            try:
                package, head = self._build_package(ctx)
            except Exception as exc:  # noqa: BLE001 — the
                # loop's own failure, classified as such
                return self._stall(
                    ctx, "runtime_failure",
                    detail=f"package construction failed: "
                           f"{type(exc).__name__}: {exc}",
                    terminal_step="package_construction"
                    if self.evidence_store is not None
                    else None)
            package_s = time.monotonic() - package_started
            iteration = ctx["iterations"] + 1
            if ctx.get("road_blocked") is not None:
                # The road's hard admission boundary
                # (the §6 amendment): the package, shed
                # to the ladder's last rung, still
                # stands at or past the sealed hard
                # fraction of the window. It is not
                # sent and no iteration stands for it —
                # the road's successor to the budget
                # refusal, at the window's edge rather
                # than at a per-call size.
                return self._stall(
                    ctx, "runtime_failure",
                    detail=ctx["road_blocked"])
            if ctx.get("road") is not None:
                # The sealed run budget (the §6
                # amendment): the office's allocation,
                # sealed at generation, bounds the run's
                # total spend. The adapter's reconciled
                # consumption is read through the model
                # handle; where it stands at or past the
                # allocation, no further package is
                # built and no call is made.
                totals_fn = getattr(
                    self.model, "road_totals", None)
                totals = totals_fn() \
                    if callable(totals_fn) else None
                if totals is not None and \
                        totals["consumed_tokens"] >= \
                        ctx["road"]["allocation_tokens"]:
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=f"the run's sealed road "
                               f"allocation is exhausted: "
                               f"{totals['consumed_tokens']} "
                               f"of "
                               f"{ctx['road']['allocation_tokens']} "
                               f"tokens consumed (the "
                               f"office's seal at "
                               f"generation; the worker "
                               f"cannot enlarge it)")

            # The per-call budget (the office-cycle
            # contract, the plan §6): the budget binds
            # the whole REQUEST — no single request may
            # exceed the sealed figure — so the estimate
            # the budget binds is the estimate of the
            # request as the adapter will construct it:
            # the contract framing, the system message,
            # the rendered package, and in native mode
            # the offered tool definitions, all inside
            # the one estimator. Where the model can
            # render its request without sending it
            # (render_request_bytes), the loop estimates
            # over those bytes; a model that cannot
            # render stands under the package-core
            # estimate below, as before. The package's
            # own estimated tokens — over its committed
            # core (its canonical serialization, the one
            # form the loop, the checker, the driver and
            # the rehearsal all reproduce byte-identically
            # from the record; the tool results stand in
            # the core by their identities, their
            # contents standing in the record already) —
            # are accounted beside the wire figure on
            # the loop for the driver's call ledger.
            # Where the budget estimate exceeds the
            # sealed budget the call is NOT sent: the
            # refusal is recorded and the run stalls
            # runtime_failure, fail closed and named,
            # and no iteration stands for the refused
            # package.
            budget_estimated = 0
            budget_bytes = 0
            if ctx.get("presentation_contract") in (
                    _tool_policy.PRESENTATION_CONTRACT_V4,
                    _tool_policy.PRESENTATION_CONTRACT_V5,
                    _tool_policy.PRESENTATION_CONTRACT_V6,
                    _tool_policy.PRESENTATION_CONTRACT_V7,
                    _tool_policy.PRESENTATION_CONTRACT_V8,
                    _tool_policy.PRESENTATION_CONTRACT_V9,
                    _tool_policy.PRESENTATION_CONTRACT_V10,
                    _tool_policy.PRESENTATION_CONTRACT_V11,
                    _tool_policy.PRESENTATION_CONTRACT_V12):
                core = _cycle_core(
                    package, ctx.get("working_set_hash"))
                serialized = canonical(core)
                estimated = _tool_policy.estimate_tokens(
                    len(serialized))
                wire_estimated = None
                wire_bytes = None
                render = getattr(
                    self.model, "render_request_bytes", None)
                if callable(render):
                    try:
                        rendered = render(
                            package,
                            mode=ctx.get("adapter_mode"))
                        wire_bytes = len(rendered)
                        wire_estimated = \
                            _tool_policy.estimate_tokens(
                                wire_bytes)
                    except Exception:  # noqa: BLE001 — a
                        # model that cannot render its
                        # request stands under the core
                        # estimate, as before
                        wire_estimated = None
                        wire_bytes = None
                budget_estimated = wire_estimated \
                    if wire_estimated is not None else estimated
                budget_bytes = wire_bytes \
                    if wire_bytes is not None \
                    else len(serialized)
                self.call_estimates.append({
                    "iteration": iteration,
                    "serialized_bytes": len(serialized),
                    "estimated_tokens": estimated,
                    "wire_estimated_tokens": wire_estimated,
                    "budget_estimated_tokens":
                        budget_estimated})
            if ctx.get("presentation_contract") in (
                    _tool_policy.PRESENTATION_CONTRACT_V4,
                    _tool_policy.PRESENTATION_CONTRACT_V5,
                    _tool_policy.PRESENTATION_CONTRACT_V6,
                    _tool_policy.PRESENTATION_CONTRACT_V7,
                    _tool_policy.PRESENTATION_CONTRACT_V8,
                    _tool_policy.PRESENTATION_CONTRACT_V9,
                    _tool_policy.PRESENTATION_CONTRACT_V10,
                    _tool_policy.PRESENTATION_CONTRACT_V11,
                    _tool_policy.PRESENTATION_CONTRACT_V12) \
                    and ctx.get("road") is None \
                    and budget_estimated > \
                    _tool_policy.PER_CALL_TOKEN_BUDGET:
                refusal = doorway.record_budget_refusal(
                    ctx["assembly_id"], iteration,
                    budget_estimated, budget_bytes,
                    _tool_policy.PER_CALL_TOKEN_BUDGET)
                ctx["recorded"].append(refusal)
                return self._stall(
                    ctx, "runtime_failure",
                    detail=f"the package for iteration "
                           f"{iteration} was refused "
                           f"before the call: its "
                           f"estimated tokens "
                           f"({budget_estimated}) "
                           f"exceed the per-call budget "
                           f"({_tool_policy.PER_CALL_TOKEN_BUDGET}); "
                           f"no request was sent")

            # (iii) Record the iteration, with the package's
            # exact cursor range, before the call. The
            # doorway's recording decision carries the
            # deadline decision (correction round 1): where
            # the deadline expired before the event could be
            # recorded — a package whose construction carried
            # the clock past expiry — the event is refused,
            # no iteration is counted, and the loop answers
            # with its deadline stall. Any other refusal is
            # the machinery's own failure.
            # BD-1 (native adapter piece): under a native-
            # judged assembly, the iteration's commitment
            # also records the disable_tool_validation
            # state of its request construction. The state
            # is read ONCE, here — a per-iteration snapshot
            # (build-examination correction, INDEX 403):
            # the snapshot is what the commitment records,
            # and the same snapshot is staged into the
            # call's request construction below, so the
            # committed state and the transmitted state are
            # one value, not two reads of a mutable
            # attribute that could drift apart between
            # them. A callable exposing no such state
            # stands under the build's settled construction:
            # enabled. A text-judged assembly records
            # nothing — its iteration events are exactly as
            # before.
            native_flag = None
            if ctx.get("adapter_mode") == "native":
                flag = getattr(self.model,
                               "disable_tool_validation", True)
                native_flag = flag if isinstance(flag, bool) \
                    else True
            ctx["flag_snapshot"] = native_flag
            try:
                ev = doorway.record_loop_iteration(
                    ctx["assembly_id"], iteration,
                    ctx["cursor"], head,
                    catalogue_hash=ctx.get("catalogue_hash"),
                    registry_version=ctx.get(
                        "registry_version"),
                    evidence_governed=self.evidence_store
                    is not None,
                    disable_tool_validation=native_flag,
                    working_set_hash=ctx.get(
                        "working_set_hash"),
                    presentation_hash=ctx.get(
                        "presentation_hash"))
            except DoorwayRefusal as refusal:
                if refusal.ground == \
                        LOOP_ITERATION_DEADLINE_GROUND:
                    return self._stall(
                        ctx, "deadline",
                        terminal_step="deadline_at_start"
                        if self.evidence_store is not None
                        else None)
                return self._stall(
                    ctx, "runtime_failure",
                    detail=f"the iteration could not be "
                           f"recorded: {refusal.ground}")
            ctx["iterations"] = iteration
            ctx["recorded"].append(ev)
            ctx["iteration_event_seq"] = ev["event_seq"]
            # The cursor advances only to the head actually
            # presented; the iteration event itself stands
            # after that head and is presented in the next
            # iteration's delta.
            ctx["cursor"] = head

            # Response-evidence piece: where an evidence
            # store stands, the call runs the evidence
            # sequence — the call boundary, the seam's
            # evidence persisted and dispositioned before
            # any effect — in _call_governed, which returns
            # a terminal result or "continue" after
            # adjudication.
            if self.evidence_store is not None:
                governed = self._call_governed(
                    ctx, package, iteration, ev, package_s)
                if governed != "continue":
                    return governed
                continue

            # (iv) Invoke the callable, with the activation's
            # remaining budget as a call parameter — outside
            # the package the model sees. Once the iteration
            # stands recorded, the callable is invoked for it
            # (correction round 1): one iteration is one model
            # call, so there is no path that records an
            # iteration and then exits uncalled. The budget
            # may already be exhausted by invocation time —
            # the callable receives it as derived, and a
            # callable that cannot begin within it does not
            # begin (the adapter refuses an exhausted budget
            # before any provider request); the loop answers
            # that outcome with its deadline stall, below. The
            # one exception is a budget that cannot be derived
            # at all — the anchor failed between the recording
            # decision and the call: no lawful budget exists
            # to invoke under, and the stop is the machinery's.
            # INDEX 222: the budget and the deadline handed to
            # the callable come from ONE doorway derivation —
            # the activation's absolute deadline, from which
            # the remaining budget is the distance to now. The
            # absolute point travels with the call so the
            # callable's cancellation boundary is the
            # activation deadline itself; a callable handed
            # only the sampled duration would reconstruct its
            # deadline at establishment and drift past the
            # true point by the sampling-to-invocation
            # interval.
            deadline, problem = doorway.activation_deadline(
                ctx["instance_id"])
            if problem is not None:
                return self._stall(ctx, "runtime_failure",
                                   detail=problem)
            remaining = deadline - time.monotonic() \
                if deadline is not None else None
            self._stage_flag_snapshot(ctx)
            call_started = time.monotonic()
            try:
                if ctx.get("adapter_mode") is not None:
                    raw = self.model(
                        package, budget=remaining,
                        deadline=deadline,
                        mode=ctx["adapter_mode"])
                else:
                    raw = self.model(package, budget=remaining,
                                     deadline=deadline)
            except AdapterFailure as failure:
                self._note_call_timing(ctx, iteration,
                                       package_s, call_started)
                # The deadline governs even here: a failure
                # that arrives after expiry is the deadline's
                # stop, whatever its kind.
                if self._deadline_passed(ctx):
                    return self._stall(ctx, "deadline")
                if failure.kind == "malformed_response":
                    return self._stall(ctx, "provider_failure",
                                       detail=failure.detail)
                return self._stall(
                    ctx, "provider_failure",
                    detail=f"{failure.kind}: {failure.detail}")
            except Exception as exc:  # noqa: BLE001 — a
                # provider-side failure of the callable itself
                self._note_call_timing(ctx, iteration,
                                       package_s, call_started)
                if self._deadline_passed(ctx):
                    return self._stall(ctx, "deadline")
                return self._stall(
                    ctx, "provider_failure",
                    detail=f"{type(exc).__name__}: {exc}")
            self._note_call_timing(ctx, iteration, package_s,
                                   call_started)
            # A response that arrives after the deadline is
            # not validated and not effected: the deadline is
            # the governing bound, and the stop is its.
            if self._deadline_passed(ctx):
                return self._stall(ctx, "deadline")

            # (v) Whole-response validation, then per-act and
            # per-request adjudication.
            outcome, data = self._validate(
                raw, native_mode=ctx.get("adapter_mode")
                == "native")
            if outcome == "malformed":
                return self._stall(ctx, "malformed_response",
                                   detail=data)
            if outcome == "decline":
                return {"ok": True, "outcome": "decline",
                        "reason": data,
                        "instance_id": ctx["instance_id"],
                        "assembly_id": ctx["assembly_id"],
                        "iterations": ctx["iterations"],
                        "recorded": ctx["recorded"],
                        "refused": ctx["refused"],
                        "dispatched": ctx["dispatched"],
                        "call_timings": ctx["call_timings"]}
            if outcome == "yield":
                return {"ok": True, "outcome": "yield",
                        "summary": data,
                        "instance_id": ctx["instance_id"],
                        "assembly_id": ctx["assembly_id"],
                        "iterations": ctx["iterations"],
                        "recorded": ctx["recorded"],
                        "refused": ctx["refused"],
                        "dispatched": ctx["dispatched"],
                        "call_timings": ctx["call_timings"]}
            if outcome == "native":
                # The native corridor (N20), on the
                # ungoverned path: classification, the
                # translation record, then dispatch — no
                # disposition stands on this path to bind,
                # so the record binds no artifact hash.
                native_result = self._adjudicate_native(
                    ctx, data, ev["event_seq"], None)
                if native_result != "continue":
                    return native_result
            else:
                self._adjudicate(ctx, data)
                if ctx.get("delivery_filing_error"):
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=ctx["delivery_filing_error"])
                if ctx.get("delivery_stage_gate_error"):
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=ctx[
                            "delivery_stage_gate_error"])
                if ctx.get("delivery_evidence_gate_error"):
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=ctx[
                            "delivery_evidence_gate_error"])
                if ctx.get("delivery_length_gate_error"):
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=ctx[
                            "delivery_length_gate_error"])
                if ctx.get("deliverable_filed") is not None:
                    return self._delivered_result(ctx)

    # --------------------------------- response evidence
    def _stage_flag_snapshot(self, ctx):
        """Hand the iteration's disable_tool_validation
        snapshot to the callable's request construction,
        where the callable exposes the staging seam
        (BD-1, build-examination correction INDEX 403):
        the value the iteration's commitment records is
        the value the transmitted request carries — the
        callable's own mutable attribute is not read
        again at construction time. A callable exposing
        no seam is handed nothing; its construction is
        its own, exactly as before."""
        stage = getattr(self.model,
                        "stage_disable_tool_validation", None)
        if callable(stage):
            stage(ctx.get("flag_snapshot"))

    def _call_governed(self, ctx, package, iteration,
                       iteration_ev, package_s):
        """One iteration's call under the response-evidence
        regime (WORKER-RESPONSE-EVIDENCE-SCOPE Rev 8), in
        the scope's one exact sequence (R2-3 as revised):
        CALL_ENTERED records the durable crossing of the
        call-entry boundary; the callable is invoked; the
        seam's evidence is persisted (where a response was
        captured) and the RESPONSE_EVIDENCE disposition is
        committed — ahead of the post-call deadline stall
        and ahead of any dispatch; only then do validation's
        outcomes take effect. A failure of the evidence
        mechanism itself ends the run at the
        evidence_capture_failure terminal (R8-2). Returns a
        terminal result dict, or "continue" after a
        proposals outcome has been adjudicated."""
        doorway = self.doorway
        iteration_seq = iteration_ev["event_seq"]
        try:
            doorway.record_call_entered(
                ctx["assembly_id"], iteration, iteration_seq)
        except DoorwayRefusal as refusal:
            return self._stall(
                ctx, "runtime_failure",
                detail=f"the call boundary could not be "
                       f"recorded: {refusal.ground}")
        deadline, problem = doorway.activation_deadline(
            ctx["instance_id"])
        if problem is not None:
            # The call cannot be invoked at all — the
            # anchor failed between the recording decision
            # and the call. The entered iteration still owes
            # its disposition: the seam observed nothing,
            # and nothing about receipt is established.
            seam = _evidence.empty_seam("loop")
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = problem
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam,
                    _evidence.adapter_verdict(
                        "not_reached",
                        reason="the call could not be "
                               "invoked; no interpretation "
                               "began"),
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="the call could not be "
                               "invoked; no outcome stood "
                               "to validate"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            return self._stall(ctx, "runtime_failure",
                               detail=problem)
        remaining = deadline - time.monotonic() \
            if deadline is not None else None
        # The callable's evidence channel opens empty for
        # this call: whatever stands there afterwards is
        # this call's seam observation, or nothing.
        if hasattr(self.model, "last_response_evidence"):
            try:
                self.model.last_response_evidence = None
            except Exception:
                pass
        self._stage_flag_snapshot(ctx)
        call_started = time.monotonic()
        try:
            if ctx.get("adapter_mode") is not None:
                raw = self.model(
                    package, budget=remaining,
                    deadline=deadline,
                    mode=ctx["adapter_mode"])
            else:
                raw = self.model(package, budget=remaining,
                                 deadline=deadline)
        except AdapterFailure as failure:
            self._note_call_timing(ctx, iteration, package_s,
                                   call_started)
            seam = self._seam_from_failure(failure)
            adapter_v = seam.pop("adapter_verdict", None) or \
                self._verdict_from_failure(failure, seam)
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam, adapter_v,
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="the adapter stage produced "
                               "no outcome to validate"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            if self._deadline_passed(ctx):
                return self._stall(ctx, "deadline")
            if failure.kind == "malformed_response":
                # The envelope gate (door scope,
                # 2026-11-24): a recognisable attempted
                # contribution that failed the parse is
                # answered with a correction and the run
                # continues within its budget — a gate,
                # not a stall. The raw response and the
                # parse failure already stand preserved in
                # this iteration's response-evidence
                # disposition, settled above.
                if self._try_delivery_gate(
                        ctx, iteration_seq, failure, seam):
                    return "continue"
                if ctx.get("delivery_gate_error"):
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=ctx["delivery_gate_error"])
                return self._stall(ctx, "provider_failure",
                                   detail=failure.detail)
            if failure.kind == "provider_error":
                # The tool-shape gate (the calibration):
                # a provider refusal of the tool-use
                # shape alone — the worker reached for a
                # tool natively where no native tools
                # were offered — is answered with a
                # correction and the run continues within
                # its budget, a gate under Ben's ruling
                # (INDEX 475), not a stall. Every other
                # provider failure stalls exactly as it
                # always has, below.
                if self._try_tool_shape_gate(
                        ctx, iteration_seq, failure, seam):
                    return "continue"
                if ctx.get("tool_shape_gate_error"):
                    return self._stall(
                        ctx, "runtime_failure",
                        detail=ctx["tool_shape_gate_error"])
            return self._stall(
                ctx, "provider_failure",
                detail=f"{failure.kind}: {failure.detail}")
        except Exception as exc:  # noqa: BLE001 — a
            # provider-side failure of the callable itself
            self._note_call_timing(ctx, iteration, package_s,
                                   call_started)
            seam = getattr(self.model,
                           "last_response_evidence", None)
            if not isinstance(seam, dict):
                seam = _evidence.empty_seam("loop")
                seam["seam"]["failure_class"] = \
                    "transport_internal_error"
                seam["seam"]["diagnostic"] = \
                    f"{type(exc).__name__}: {exc}"
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam,
                    _evidence.adapter_verdict(
                        "not_reached",
                        reason="the callable failed outside "
                               "its interpretation: "
                               f"{type(exc).__name__}"),
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="the adapter stage produced "
                               "no outcome to validate"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            if self._deadline_passed(ctx):
                return self._stall(ctx, "deadline")
            return self._stall(
                ctx, "provider_failure",
                detail=f"{type(exc).__name__}: {exc}")
        self._note_call_timing(ctx, iteration, package_s,
                               call_started)
        seam = getattr(self.model, "last_response_evidence",
                       None)
        if not isinstance(seam, dict):
            # The callable answered but its seam produced
            # no evidence observation at all: nothing about
            # the answer may take effect — the disposition
            # records the seam's silence as unresolved, and
            # the run stops as a provider failure.
            seam = _evidence.empty_seam("unknown")
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = (
                "the callable produced no response "
                "evidence; the answer's effects are not "
                "admitted")
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam,
                    _evidence.adapter_verdict(
                        "not_reached",
                        reason="the seam recorded no "
                               "adapter verdict"),
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="no response evidence stood "
                               "to validate against"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            return self._stall(
                ctx, "provider_failure",
                detail="the callable produced no response "
                       "evidence; the answer's effects are "
                       "not admitted")
        # Whole-response validation is effect-free: it
        # runs here so the artifact's loop verdict stands
        # complete before the disposition commits. Its
        # outcomes take effect only after the disposition.
        outcome, data = self._validate(
            raw, native_mode=ctx.get("adapter_mode")
            == "native")
        if outcome == "malformed":
            loop_v = _evidence.loop_verdict(
                "malformed", detail=data)
        else:
            loop_v = _evidence.loop_verdict(
                "validated", outcome=outcome)
        adapter_v = seam.get("adapter_verdict") or \
            self._verdict_from_outcome(seam, raw)
        try:
            disposition, disp_outcome = self._settle_evidence(
                ctx, iteration_seq, seam, adapter_v, loop_v)
        except _EvidenceFailure as fail:
            return self._evidence_failure_result(
                ctx, iteration_seq, fail)
        ctx["recorded"].append(disposition)
        if disp_outcome != "captured":
            # A returned answer whose seam captured no
            # response (or could not establish one): the
            # disposition prohibits every effect, and the
            # run stops — the seam and the answer disagree,
            # and the seam governs.
            return self._stall(
                ctx, "provider_failure",
                detail=f"the response disposition stands "
                       f"{disp_outcome}; the answer's "
                       f"effects are not admitted")
        # The evidence stands durable and bound; the
        # deadline governs from here, exactly as it
        # governs the ungoverned path — a response that
        # arrived after expiry is captured and bound
        # first (R2-3), and only then does the deadline
        # stall proceed, with the evidence attached.
        if self._deadline_passed(ctx):
            return self._stall(ctx, "deadline")
        if outcome == "malformed":
            return self._stall(ctx, "malformed_response",
                               detail=data)
        if outcome == "decline":
            return {"ok": True, "outcome": "decline",
                    "reason": data,
                    "instance_id": ctx["instance_id"],
                    "assembly_id": ctx["assembly_id"],
                    "iterations": ctx["iterations"],
                    "recorded": ctx["recorded"],
                    "refused": ctx["refused"],
                    "dispatched": ctx["dispatched"],
                    "call_timings": ctx["call_timings"]}
        if outcome == "yield":
            return {"ok": True, "outcome": "yield",
                    "summary": data,
                    "instance_id": ctx["instance_id"],
                    "assembly_id": ctx["assembly_id"],
                    "iterations": ctx["iterations"],
                    "recorded": ctx["recorded"],
                    "refused": ctx["refused"],
                    "dispatched": ctx["dispatched"],
                    "call_timings": ctx["call_timings"]}
        if outcome == "native":
            # The native corridor (N20), governed: the
            # disposition stands committed above, so the
            # translation record commits after it — bound
            # to its exact artifact hash — and before any
            # dispatch of this iteration.
            return self._adjudicate_native(
                ctx, data, iteration_seq,
                disposition["payload"].get("artifact_sha256"))
        self._adjudicate(ctx, data)
        if ctx.get("delivery_filing_error"):
            return self._stall(
                ctx, "runtime_failure",
                detail=ctx["delivery_filing_error"])
        if ctx.get("delivery_stage_gate_error"):
            return self._stall(
                ctx, "runtime_failure",
                detail=ctx["delivery_stage_gate_error"])
        if ctx.get("delivery_evidence_gate_error"):
            return self._stall(
                ctx, "runtime_failure",
                detail=ctx["delivery_evidence_gate_error"])
        if ctx.get("delivery_length_gate_error"):
            return self._stall(
                ctx, "runtime_failure",
                detail=ctx["delivery_length_gate_error"])
        if ctx.get("deliverable_filed") is not None:
            return self._delivered_result(ctx)
        return "continue"

    def _seam_from_failure(self, failure):
        """The seam observation an AdapterFailure carries:
        the failure's own attached evidence where the seam
        supplied it, else the callable's published
        evidence, else a seam synthesised from the
        failure's kind under the scope's class table —
        a deadline expiry with confirmed termination is
        timeout_after_send (unresolved: it establishes
        what the parent received, not what the provider
        sent, R5-1); an unconfirmed termination is
        termination_unconfirmed; anything else is the
        transport's internal error. Nothing here promotes
        an uncertain history to no_response."""
        seam = getattr(failure, "evidence", None)
        if not isinstance(seam, dict):
            seam = getattr(self.model,
                           "last_response_evidence", None)
        if isinstance(seam, dict):
            return seam
        seam = _evidence.empty_seam("adapter")
        if failure.kind == "no_response":
            seam["seam"]["failure_class"] = \
                "timeout_after_send"
            seam["seam"]["fence"] = "adapter_deadline"
            seam["seam"]["termination_confirmed"] = True
            seam["seam"]["diagnostic"] = failure.detail
        elif failure.kind == "transport_unresolved":
            seam["seam"]["failure_class"] = \
                "termination_unconfirmed"
            seam["seam"]["diagnostic"] = failure.detail
        else:
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = \
                f"{failure.kind}: {failure.detail}"
        return seam

    @staticmethod
    def _verdict_from_failure(failure, seam):
        """The adapter verdict for a failure the seam did
        not already verdict (R3-3, total): a malformed
        response is a parsing failure over a received
        answer — its content hash is L4's, where L4
        stands; every other failure means interpretation
        could not begin, and stands not_reached with the
        reason named."""
        if failure.kind == "malformed_response":
            content_hash = None
            if seam.get("l1_bytes") is not None:
                l4 = _evidence.derive_layers(
                    seam["l1_bytes"])["L4"]
                if l4.get("present"):
                    content_hash = l4["sha256"]
            return _evidence.adapter_verdict(
                "failure", kind=failure.kind,
                detail=failure.detail,
                content_hash=content_hash)
        return _evidence.adapter_verdict(
            "not_reached",
            reason=f"interpretation could not begin: "
                   f"{failure.kind}: {failure.detail}")

    @staticmethod
    def _verdict_from_outcome(seam, raw):
        """The adapter verdict for a returned outcome the
        seam did not already verdict: the typed outcome
        the adapter produced, with the hash of the exact
        content it consumed — L4's hash, where L4 stands
        (the identity chain W-a proves: the verdict's
        content is the artifact's L4)."""
        content_hash = None
        if seam.get("l1_bytes") is not None:
            l4 = _evidence.derive_layers(
                seam["l1_bytes"])["L4"]
            if l4.get("present"):
                content_hash = l4["sha256"]
        return _evidence.adapter_verdict(
            "outcome",
            kind=raw.get("outcome")
            if isinstance(raw, dict) else None,
            content_hash=content_hash)

    def _settle_evidence(self, ctx, iteration_seq, seam,
                         adapter_v, loop_v):
        """Persist the artifact (where a response was
        captured) and commit the iteration's disposition,
        in that order — durable before effects (R2-3).
        Returns (disposition event, outcome). Raises
        _EvidenceFailure naming the failed operation:
        persist/verify from the store, commit from the
        doorway's refusal — or from the doorway's own
        storage/transaction failure (build examination,
        INDEX 314): a commit that raises inside the
        doorway's route is the same commit failure,
        routed the same way, once the transaction stands
        in a known state again."""
        outcome, failure_class, seam_evidence = \
            _evidence.derive_disposition(seam)
        artifact_sha256 = None
        layers = None
        if outcome == "captured":
            binding = {
                "run_id": self.doorway.store.get_run_id(),
                "assembly_id": ctx["assembly_id"],
                "instance_id": ctx["instance_id"],
                "iteration_seq": iteration_seq,
                "iteration": ctx["iterations"]}
            artifact = _evidence.build_artifact(
                binding, seam,
                {"adapter": adapter_v, "loop": loop_v})
            try:
                _path, artifact_sha256 = \
                    _evidence.persist_artifact(
                        self.evidence_store, artifact)
            except _evidence.EvidenceStoreError as exc:
                raise _EvidenceFailure(exc.operation,
                                       exc.detail)
            layers = _evidence.layer_summaries(artifact)
        try:
            ev = self.doorway.record_response_evidence(
                ctx["assembly_id"], iteration_seq, outcome,
                failure_class=failure_class,
                seam_evidence=seam_evidence,
                artifact_sha256=artifact_sha256,
                layers=layers,
                provenance=seam.get("provenance"),
                http_status=seam.get("http_status"))
        except DoorwayRefusal as refusal:
            raise _EvidenceFailure("commit", refusal.ground)
        except Exception as exc:  # noqa: BLE001 — a
            # storage or transaction failure inside the
            # doorway's route (its store.commit() raising
            # is the named case): the disposition append
            # may stand pending in an open transaction.
            # Before the failure terminal may be attempted,
            # the transaction must stand in a KNOWN state —
            # rolled back, the partial disposition
            # discarded — so the failed disposition can
            # never later be committed alongside the
            # terminal. Where even the rollback fails, the
            # state is not known: the failure is raised as
            # not terminal-recordable, and the run stops
            # claiming nothing (INDEX 314, on R8-2).
            try:
                self.doorway.store.rollback()
            except Exception as rb_exc:  # noqa: BLE001
                raise _EvidenceFailure(
                    "commit",
                    f"the disposition commit failed "
                    f"({type(exc).__name__}: {exc}) and "
                    f"the transaction could not be rolled "
                    f"back to a known state "
                    f"({type(rb_exc).__name__}: {rb_exc}); "
                    f"no evidence failure terminal is "
                    f"recorded and none is claimed",
                    terminal_recordable=False)
            raise _EvidenceFailure(
                "commit",
                f"the disposition commit failed in the "
                f"record store ({type(exc).__name__}: "
                f"{exc}); the transaction was rolled back "
                f"and the disposition stands nowhere")
        return ev, outcome

    def _evidence_failure_result(self, ctx, iteration_seq,
                                 fail):
        """The run's answer to an evidence mechanism
        failure (R8-2): record the evidence_capture_failure
        terminal — the one terminal the doorway admits
        while a disposition is outstanding — and end the
        run. Where the record mechanism itself cannot
        commit even that terminal, the implementation note
        governs: nothing is claimed — the result says the
        reason was not recorded, and CALL_ENTERED stands
        outstanding for the checker to report."""
        base = {"ok": False, "outcome": "stalled",
                "ground": "evidence_capture_failure",
                "operation": fail.operation,
                "detail": fail.detail,
                "instance_id": ctx["instance_id"],
                "assembly_id": ctx["assembly_id"],
                "iterations": ctx["iterations"],
                "recorded": ctx["recorded"],
                "refused": ctx["refused"],
                "dispatched": ctx["dispatched"],
                "call_timings": ctx["call_timings"]}
        if not fail.terminal_recordable:
            # The disposition commit failed and its
            # transaction could not be returned to a known
            # state (INDEX 314): attempting the terminal
            # here could commit the failed disposition
            # alongside it. Stop instead, claiming nothing
            # — CALL_ENTERED stands outstanding, and the
            # checker reports the incomplete history.
            base["evidence_failure_recorded"] = False
            base["reason"] = (
                "the disposition commit failed and the "
                "transaction could not be returned to a "
                "known state; no evidence failure terminal "
                "was attempted and no recorded reason is "
                "claimed")
            return base
        try:
            ev = self.doorway.record_evidence_capture_failure(
                ctx["assembly_id"], iteration_seq,
                fail.operation, detail=fail.detail)
        except Exception as exc:  # noqa: BLE001 — the
            # record mechanism itself unavailable: claim
            # nothing (the Rev 8 implementation note)
            base["evidence_failure_recorded"] = False
            base["reason"] = (
                f"the evidence failure terminal could not "
                f"be recorded ({type(exc).__name__}: "
                f"{exc}); no recorded reason is claimed")
            return base
        base["evidence_failure_recorded"] = True
        base["evidence_failure_event"] = ev
        return base

    # -------------------------------------------------- package
    def _apply_road_presentation(self, ctx, package):
        """The road's presentation pass (the §6
        amendment, accepted 2026-11-26; the build
        scope's Pieces 3 and 4): applied to a built
        cycle package under a sealed road, before its
        commitment is taken. Two acts, in order:

        SPILL — a presented block's content, or a tool
        result's content, over the spill threshold
        (4,096 counted tokens) does not ride whole:
        the package carries its reference instead —
        the content's identity, its counted size, its
        fingerprint, and a preview at or under 512
        counted tokens. The full content stands where
        it always stood (the block's file, the
        record's event); the preview is presentation
        only, and the worker pulls the whole through
        his standing read tools in bounded slices.

        SHEDDING — the package's counted size (the
        rendered request, measured with the route's
        own instrument) is held against the sealed
        window: at the start fraction (70%) the
        ladder runs — first the spill above, then
        every remaining carried result content is
        stubbed to its reference, then the journal
        draft is stubbed to its pointer — and at the
        hard fraction (80%) the package is not
        admitted at all: ctx's road_blocked names it
        and the run stalls before any iteration
        stands. Shedding clears presentation only;
        nothing is deleted, and everything shed
        stands retrievable where it stood.

        Every act is appended to the loop's road
        events for the run's report. A package under
        the thresholds is returned untouched."""
        road_decl = ctx["road"]
        window = road_decl["window_tokens"]
        counter_fn = getattr(self.model, "road_counter",
                             None)
        counter = counter_fn() \
            if callable(counter_fn) else None
        if counter is None:
            counter = _road.counter_for()
        threshold = \
            _tool_policy.ROAD_SPILL_THRESHOLD_TOKENS
        preview_max = \
            _tool_policy.ROAD_SPILL_PREVIEW_TOKENS

        def spill_stub(content, identity):
            counted = counter.count_text(content)
            return {
                **identity,
                "spilled": True,
                "counted_tokens": counted,
                "sha256": hashlib.sha256(
                    content.encode("utf-8")).hexdigest(),
                "preview": _road.bounded_preview(
                    content, preview_max, counter),
                "preview_tokens": counter.count_text(
                    _road.bounded_preview(
                        content, preview_max, counter)),
                "note": "the whole content stands "
                        "where it stood and is pulled "
                        "in bounded slices; this "
                        "preview is presentation only"}

        # --- spill: the presented block's content
        block_content = package.get("block_content")
        if isinstance(block_content, dict) and \
                isinstance(
                    block_content.get("content"), str):
            counted = counter.count_text(
                block_content["content"])
            if counted > threshold:
                stub = spill_stub(
                    block_content["content"], {
                        "block_id":
                            block_content.get("block_id"),
                        "address":
                            block_content.get("address")})
                package["block_content"] = stub
                self.road_events.append({
                    "kind": "spill",
                    "surface": "block_content",
                    "block_id": stub["block_id"],
                    "address": stub["address"],
                    "counted_tokens": counted,
                    "method": counter.method})
        # --- spill: carried tool results' contents
        for entry in package.get("tool_results") or []:
            result = entry.get("result") \
                if isinstance(entry, dict) else None
            if isinstance(result, dict) and \
                    isinstance(
                        result.get("content"), str):
                counted = counter.count_text(
                    result["content"])
                if counted > threshold:
                    entry["result"] = spill_stub(
                        result["content"], {
                            "dispatch_id":
                                entry.get("dispatch_id")})
                    self.road_events.append({
                        "kind": "spill",
                        "surface": "tool_result",
                        "dispatch_id":
                            entry.get("dispatch_id"),
                        "counted_tokens": counted,
                        "method": counter.method})
        # --- shedding: measure the rendered request
        # The measure is the rendered request's own
        # size under the route instrument: the adapter
        # renders without sending (its settled
        # render), and the counter counts that render
        # as the request's text — an approximation of
        # the wire count, named as the shedding
        # measure wherever it stands.
        def rendered_tokens():
            render = getattr(
                self.model, "render_request_bytes", None)
            if not callable(render):
                return None
            try:
                raw = render(
                    package, mode=ctx.get("adapter_mode"))
            except Exception:  # noqa: BLE001
                return None
            return counter.count_text(
                raw.decode("utf-8", "replace"))

        size = rendered_tokens()
        if size is not None and \
                size >= _tool_policy.ROAD_SHED_START_FRACTION \
                * window:
            # Rung 2: every remaining carried result
            # content is stubbed to its reference.
            for entry in package.get("tool_results") \
                    or []:
                result = entry.get("result") \
                    if isinstance(entry, dict) else None
                if isinstance(result, dict) and \
                        isinstance(
                            result.get("content"), str):
                    entry["result"] = {
                        "dispatch_id":
                            entry.get("dispatch_id"),
                        "shed": True,
                        "counted_tokens":
                            counter.count_text(
                                result["content"]),
                        "sha256": hashlib.sha256(
                            result["content"].encode(
                                "utf-8")).hexdigest(),
                        "note": "shed from presentation "
                                "under the road's ladder; "
                                "the result stands in "
                                "the record"}
                    self.road_events.append({
                        "kind": "shed",
                        "rung": "clear_results",
                        "dispatch_id":
                            entry.get("dispatch_id"),
                        "method": counter.method})
            size = rendered_tokens()
        if size is not None and \
                size >= _tool_policy.ROAD_SHED_START_FRACTION \
                * window:
            # Rung 3: the journal draft is stubbed to
            # its pointer (the journal itself stands
            # in the room, read by pull).
            draft = package.get("journal_draft")
            if isinstance(draft, dict) and \
                    isinstance(
                        draft.get("content"), str):
                package["journal_draft"] = {
                    "shed": True,
                    "counted_tokens": counter.count_text(
                        draft["content"]),
                    "sha256": hashlib.sha256(
                        draft["content"].encode(
                            "utf-8")).hexdigest(),
                    "note": "shed from presentation "
                            "under the road's ladder; "
                            "the journal stands in the "
                            "room and is read by pull"}
                self.road_events.append({
                    "kind": "shed",
                    "rung": "journal_pointer",
                    "method": counter.method})
                size = rendered_tokens()
        if size is not None and \
                size >= _tool_policy.ROAD_SHED_HARD_FRACTION \
                * window:
            ctx["road_blocked"] = (
                f"the package was not admitted under "
                f"the road's hard boundary: shed to "
                f"the ladder's last rung it still "
                f"stands at {size} counted tokens, at "
                f"or past 80% of the sealed window "
                f"({window}); no request was sent")
            self.road_events.append({
                "kind": "admission_blocked",
                "counted_tokens": size,
                "window_tokens": window,
                "method": counter.method})
        elif size is not None:
            self.road_events.append({
                "kind": "measured",
                "counted_tokens": size,
                "window_tokens": window,
                "method": counter.method})
        return package

    def _build_package(self, ctx):
        """Construct and freeze one iteration's package from a
        snapshot of the record, in the driver's package shape:
        the pinned case view (rendered, boundary-narrowed per
        R11), the record delta since the cursor, the settled
        tool results the delta carries, the instance's full
        standing dispatch state, its bounds state, and the
        tool catalogue derived from its sealed grants (Piece
        A3-CAT) — whose canonical hash and the registry
        version are stashed on the context for the iteration
        event to record. Returns (package, head) — the head
        the package was frozen at, which is the cursor
        range's close."""
        doorway = self.doorway
        # The step gate (the room rebuild): under the
        # process-tree contract, a gate owed at this
        # wake is recorded BEFORE the snapshot, so the
        # package's head stands after it and its facts
        # are true at presentation; a gate that cannot
        # be recorded raises here and the run stalls
        # runtime_failure — fail closed, as the
        # family's gates do.
        if ctx.get("presentation_contract") == \
                _tool_policy.PRESENTATION_CONTRACT_V3:
            self._record_step_gate_if_owed(ctx)
        # The cycle contract's gate records (the plan
        # §5): under the office-cycle contract, the
        # journal transitions and refusals the record
        # shows but has not yet recorded, and a cycle
        # gate owed at this wake, are recorded BEFORE
        # the snapshot, the same way — the package's
        # head stands after them and their facts are
        # true at presentation.
        if ctx.get("presentation_contract") in (
                _tool_policy.PRESENTATION_CONTRACT_V4,
                _tool_policy.PRESENTATION_CONTRACT_V5,
                _tool_policy.PRESENTATION_CONTRACT_V6,
                _tool_policy.PRESENTATION_CONTRACT_V7,
                _tool_policy.PRESENTATION_CONTRACT_V8,
                _tool_policy.PRESENTATION_CONTRACT_V9,
                _tool_policy.PRESENTATION_CONTRACT_V10,
                _tool_policy.PRESENTATION_CONTRACT_V11,
                _tool_policy.PRESENTATION_CONTRACT_V12):
            self._record_cycle_events_if_owed(ctx)
        events = doorway.store.all_events()
        state = fold(events, doorway.store.get_run_id())
        head = state["head_seq"]
        # Piece A3-CAT: the tool catalogue, derived from the
        # instance's sealed assembly record — the same
        # generated object the doorway's grant check reads —
        # so what the package advertises cannot drift from
        # what the doorway enforces. An undescribable granted
        # tool raises here, and the run answers with its
        # runtime_failure stall: no package, no iteration,
        # no call.
        generated = doorway._generated_payload(
            ctx["assembly_id"])
        # The retrieval piece: an assembly standing under
        # the retrieval regime is catalogued per grant and
        # its retrieval results are carried once (below).
        # The regime's assemblies are the retrieval
        # contract's (catalogued under v3 — the version its
        # dispatches record) and, for their retrieval tools,
        # the exec contract's (the combined configuration,
        # INDEX 476 — catalogued under v4, the version the
        # ternary below prefers for them). Any other
        # assembly derives under the current version and
        # presents its outcomes exactly as it always has.
        governed = doorway._retrieval_governed(generated)
        # Working-set carriage (the run-3 correction): the
        # combined configuration's assemblies declare the
        # working-set contract in their sealed record; their
        # packages present the gathered material accumulated
        # in a working set (below) instead of letting each
        # result evaporate with its delta. Every other
        # assembly's package is exactly as it has always
        # been.
        ws_applies = governed and (generated or {}).get(
            "working_set_contract") == \
            _tool_policy.WORKING_SET_CONTRACT
        version = _tool_policy.EXEC_REGISTRY_VERSION \
            if doorway._exec_governed(generated) else \
            _tool_policy.RETRIEVAL_REGISTRY_VERSION \
            if governed else _tool_policy.REGISTRY_VERSION
        # A governed assembly's catalogue is per grant (the
        # attempt-7 release correction, INDEX 257): its two
        # authority paths grant the same tools under two
        # scopes, and both scopes are the worker's to see.
        catalogue = _derive_catalogue(
            (generated or {}).get("grants"), version,
            per_grant=governed)
        ctx["catalogue_hash"] = _catalogue_hash(catalogue)
        ctx["registry_version"] = version
        # The native preflight (N7) resolves against this
        # very catalogue object — the one whose hash the
        # iteration event records — never a re-derivation.
        ctx["catalogue"] = catalogue
        seat = ctx["seat"]
        view = render_view(events, seat)
        boundary = ctx["content"].get("evidence_boundary")
        if isinstance(boundary, list):
            view["sealed"] = [s for s in view["sealed"]
                              if s["material_id"] in boundary]
        raw_delta = [ev for ev in events
                     if ctx["cursor"] < ev["event_seq"] <= head
                     and self._relevant(ctx, ev)]
        # tool_results is built from the record's own events,
        # before the delta's copy is stubbed for single
        # carriage below: this is the one place the package
        # carries a retrieval result's content — except
        # under the working-set contract, where the entries
        # are stubbed in their turn (below) and the content
        # stands in the working set.
        tool_results = [{
            "dispatch_id": ev["payload"].get("dispatch_id"),
            "request_id": ev["payload"].get("request_id"),
            "outcome": ev["payload"].get("outcome"),
            "result": copy.deepcopy(
                ev["payload"].get("result")),
            "detail": ev["payload"].get("detail"),
            "event_seq": ev["event_seq"],
        } for ev in raw_delta if ev["type"] == "TOOL_OUTCOME"]
        # Native adapter piece (B4 — N26/N24): the binding
        # between provider call IDs and the loop's request
        # identities stands in the record's translation
        # records; the carriage reads it from the full
        # snapshot, so an outcome settling in a later delta
        # than its translation still answers under its call
        # ID. Outcome entries gain the provider call ID
        # beside request_id and dispatch_id where a binding
        # stands; translation refusals and doorway refusals
        # of bound calls are presented in the same carriage,
        # in the examined N16 error form; and the bound
        # entries assemble in provider call order. Where no
        # binding stands anywhere — every text-mode package
        # — the carriage is exactly as it has always been.
        call_binding = {}
        for ev in events:
            if ev["type"] != "TRANSLATION_RECORDED":
                continue
            for centry in ev["payload"].get("calls") or []:
                if centry.get("loop_request_id"):
                    call_binding[centry["loop_request_id"]] = {
                        "provider_call_id":
                            centry.get("provider_call_id"),
                        "provider_ordinal":
                            centry.get("provider_ordinal"),
                        "translation_seq": ev["event_seq"]}
        if any(ev["type"] == "TRANSLATION_RECORDED"
               for ev in events):
            offered_names = list(dict.fromkeys(
                entry["tool"] for entry in catalogue))
            for entry in tool_results:
                binding = call_binding.get(entry["request_id"])
                if binding is not None:
                    entry["provider_call_id"] = \
                        binding["provider_call_id"]
                    entry["provider_ordinal"] = \
                        binding["provider_ordinal"]
                    entry["_translation_seq"] = \
                        binding["translation_seq"]
            for ev in raw_delta:
                if ev["type"] == "TRANSLATION_RECORDED":
                    for centry in \
                            ev["payload"].get("calls") or []:
                        if not centry.get("refusal_class"):
                            continue
                        tool_results.append({
                            "dispatch_id": None,
                            "request_id": None,
                            "provider_call_id": centry.get(
                                "provider_call_id"),
                            "provider_ordinal": centry.get(
                                "provider_ordinal"),
                            "outcome": "refused",
                            "refusal_class":
                                centry["refusal_class"],
                            "error": _translation_error_text(
                                centry, offered_names),
                            "result": None,
                            "detail": None,
                            "event_seq": ev["event_seq"],
                            "_translation_seq":
                                ev["event_seq"]})
                elif ev["type"] == "REJECTION" and \
                        ev["payload"].get("attempted_type") \
                        == "TOOL_DISPATCHED":
                    binding = call_binding.get(
                        ev["payload"].get("request_id"))
                    if binding is not None:
                        tool_results.append({
                            "dispatch_id": None,
                            "request_id": ev["payload"].get(
                                "request_id"),
                            "provider_call_id": binding[
                                "provider_call_id"],
                            "provider_ordinal": binding[
                                "provider_ordinal"],
                            "outcome": "refused",
                            "refusal_class": "doorway_refused",
                            "error": _doorway_error_text(
                                ev["payload"].get("ground")),
                            "result": None,
                            "detail": None,
                            "event_seq": ev["event_seq"],
                            "_translation_seq": binding[
                                "translation_seq"]})
            # Provider call order (N24): the bound entries
            # sort by their translation record and ordinal;
            # any unbound entry keeps its place after them,
            # in record order. The sort key is carriage-local
            # and is removed before the package freezes.
            tool_results.sort(key=lambda entry: (
                (0, entry["_translation_seq"],
                 entry["provider_ordinal"])
                if "_translation_seq" in entry else
                (1, 0, entry.get("event_seq") or 0)))
            for entry in tool_results:
                entry.pop("_translation_seq", None)
        if ws_applies:
            # Failure instruction (Ben's gate ruling,
            # INDEX 475; the freedom-first setup pass,
            # 2026-11-24): in a working-set package, a
            # presented failure or refusal carries usable
            # instruction — what was asked, why it failed
            # in plain terms, and the working alternative
            # that exists within his grants; an identical
            # call whose failure was already presented in
            # an earlier wake is named as a repeat. A
            # refusal is a gate, not a wall: the
            # doorway's authority is unchanged — nothing
            # dispatched until the call was right — this
            # changes only what the refusal SAYS. Working-
            # set packages only; every other population's
            # packages are byte-identical to what they were.
            self._attach_failure_instructions(
                tool_results, events, raw_delta, ctx,
                generated)
        if ws_applies and ctx.get(
                "presentation_contract") != \
                _tool_policy.PRESENTATION_CONTRACT_V2:
            # Working-set carriage: this delta's retrieval
            # results are presented in the working set (the
            # accumulated set built below), so their
            # tool_results entries stand by the same
            # provenance stub the delta's copy carries,
            # pointing at the working set — the content
            # appears exactly once in the package.
            #
            # Under the pointer-rule successor contract
            # (INDEX 568) this stub does not stand: the
            # working set is presented as pointers, so the
            # one presentation of a result's content is
            # here, in the newest results of the first
            # wake after its gather — the content appears
            # exactly once in the package still, and in
            # no later package at all.
            dispatch_tools_all = {
                did: d.get("tool")
                for did, d in state["dispatches"].items()}
            for entry in tool_results:
                if entry.get("outcome") != "result":
                    continue
                if dispatch_tools_all.get(
                        entry.get("dispatch_id")) not in \
                        _tool_policy.RETRIEVAL_TOOLS:
                    continue
                result = entry.get("result")
                if not isinstance(result, dict) or \
                        "content" not in result:
                    continue
                entry["result"] = _carriage_stub(
                    result, "working_set")
        delta = copy.deepcopy(raw_delta)
        if governed:
            # Single carriage (retrieval piece; INDEX 249):
            # the record retains each retrieval outcome in
            # full, but the package presents its content
            # exactly once — in tool_results, with its
            # provenance. The delta's rendering of the same
            # outcome carries the provenance without the
            # content: the fields that bear content (the
            # content itself, search passages, a listing's
            # headings) are replaced by the carriage marker,
            # and every scalar the provenance needs — the
            # path, the authority path, the content's hash
            # and size, the served range or window, the
            # search's totals — stands as recorded. A later
            # package does not re-present the result at all:
            # the cursor has passed it, as it passes every
            # event exactly once. Under the working-set
            # contract the one presentation moves: the
            # content stands in the package's working set
            # (accumulated across wakes), and both the
            # delta's copy and the tool_results entry carry
            # the stub pointing there.
            dispatch_tools = {
                did: d.get("tool")
                for did, d in state["dispatches"].items()}
            for ev in delta:
                if ev["type"] != "TOOL_OUTCOME":
                    continue
                payload = ev["payload"]
                result = payload.get("result")
                if payload.get("outcome") != "result" or \
                        dispatch_tools.get(
                            payload.get("dispatch_id")) not in \
                        _tool_policy.RETRIEVAL_TOOLS or \
                        not isinstance(result, dict) or \
                        "content" not in result:
                    continue
                payload["result"] = _carriage_stub(
                    result,
                    "working_set" if ws_applies
                    else "tool_results")
        # The working set itself: derived from the whole
        # snapshot's recorded outcomes (not the delta), so
        # material gathered in any earlier wake is still in
        # front of the worker at this one. Its commitment
        # hash is stashed on the context for the iteration
        # event to record, beside the catalogue's.
        working_set = None
        if ws_applies:
            working_set = _derive_working_set(
                events, state["dispatches"],
                ctx["instance_id"], head)
            ctx["working_set_hash"] = _working_set_hash(
                working_set)
        standing = [{
            "dispatch_id": did,
            "request_id": d.get("request_id"),
            "tool": d.get("tool"),
            "outcome": d.get("outcome"),
            "reconciled_outcome": d.get("reconciled_outcome"),
        } for did, d in sorted(state["dispatches"].items())
            if d.get("instance_id") == ctx["instance_id"]]
        remaining, _problem = doorway.activation_remaining(
            ctx["instance_id"])
        package = {
            "seat": seat,
            "role": ctx["role"],
            "instance_id": ctx["instance_id"],
            "case": copy.deepcopy(ctx["content"]),
            "case_id": ctx["case_id"],
            "case_version": ctx["case_version"],
            "view": view,
            "delta": copy.deepcopy(delta),
            "tools": catalogue,
            "tool_results": tool_results,
            "standing_dispatches": standing,
            "bounds": {
                "iteration": ctx["iterations"] + 1,
                "steps_used": ctx["iterations"],
                "step_ceiling": ctx["bounds"]["step_ceiling"],
                "deadline_seconds":
                    ctx["bounds"]["deadline_seconds"],
                "seconds_remaining": remaining,
            },
            "position": head,
        }
        if working_set is not None:
            package["working_set"] = working_set
        if ws_applies:
            # The orientation pass (Ben's rulings on the
            # worker consultation, 2026-11-24 — the
            # worker asked, from his side of the door,
            # for his position, his tools stated plainly,
            # his task state, and his own notebook back):
            # a working-set package states where he
            # stands in the run's bounds, that his task
            # stands in progress, and his granted tools
            # as an explicit list derived from the sealed
            # grants — and, where the case designates a
            # journal, presents the journal as it stands.
            # Presentation only: no lifecycle machinery,
            # no new authority. Working-set packages only;
            # every other population's packages are
            # byte-identical to what they were.
            #
            # The run-6 package (Ben's rulings and the
            # worker's briefcase consultation, 2026-11-24)
            # orders a working-set package as his
            # briefcase is laid out: his onboarding at
            # the head — at the first wake the full text
            # the case carries; at later wakes a short
            # cover in its place, his dashboard: the
            # job's headline, the deliverable, his step
            # and his task's state — then his position
            # and status, then the case itself (the
            # brief: the assignment and the glossary),
            # then his working set, then his journal,
            # then his tools as a phase-grouped menu,
            # then the record's own furniture — the view,
            # the delta and the outcomes — as it has
            # always stood. The components' values are
            # the same values the package has always
            # carried; only their order, the onboarding
            # and cover, the journal's purpose label and
            # the menu's grouping are new. A case carrying
            # no onboarding opens with no guide, exactly
            # as a case designating no journal presents
            # no notebook.
            step_position = {
                "statement":
                    f"step {ctx['iterations'] + 1} of "
                    f"{ctx['bounds']['step_ceiling']}",
                "iteration": ctx["iterations"] + 1,
                "step_ceiling":
                    ctx["bounds"]["step_ceiling"]}
            journal = self._journal_component(ctx)
            onboarding = (ctx["content"] or {}).get(
                "onboarding")
            if not (isinstance(onboarding, dict)
                    and isinstance(
                        onboarding.get("headline"), str)
                    and isinstance(
                        onboarding.get("deliverable"), str)
                    and isinstance(
                        onboarding.get("text"), str)):
                onboarding = None
            deliverable = onboarding["deliverable"] \
                if onboarding is not None else None
            ordered = {}
            if onboarding is not None:
                if ctx["iterations"] == 0:
                    ordered["onboarding"] = \
                        onboarding["text"]
                else:
                    ordered["cover"] = {
                        "headline":
                            onboarding["headline"],
                        "deliverable": deliverable,
                        "statement":
                            f"{onboarding['headline']} "
                            f"— the deliverable: "
                            f"{deliverable}. Step "
                            f"{ctx['iterations'] + 1} of "
                            f"{ctx['bounds']['step_ceiling']}"
                            f"; task in progress. Your "
                            f"onboarding — the full "
                            f"briefcase guide — stands "
                            f"at the head of your first "
                            f"wake's package."}
            if ctx["iterations"] == 0:
                # The door scope's carriage (2026-11-24):
                # at the first wake only, the role-memory
                # snapshot rides with the onboarding
                # material, and the opening record stands
                # immediately after it — the settled
                # results of the opening conversation,
                # carried into the room as recorded work
                # state. Both are the case's own components,
                # presented exactly as sealed.
                _role_memory = (ctx["content"] or {}).get(
                    "role_memory")
                if isinstance(_role_memory, list) \
                        and _role_memory:
                    ordered["role_memory"] = copy.deepcopy(
                        _role_memory)
                _opening = (ctx["content"] or {}).get(
                    "opening")
                if isinstance(_opening, dict) and _opening:
                    ordered["opening"] = copy.deepcopy(
                        _opening)
            ordered["step_position"] = step_position
            ordered["task_status"] = "in progress"
            if ctx.get("delivery_gate_correction") \
                    is not None:
                ordered["delivery_gate_correction"] = \
                    ctx.pop("delivery_gate_correction")
            if ctx.get("delivery_stage_gate_correction") \
                    is not None:
                ordered["delivery_stage_gate_correction"] \
                    = ctx.pop(
                        "delivery_stage_gate_correction")
            if ctx.get(
                    "delivery_evidence_gate_correction") \
                    is not None:
                ordered[
                    "delivery_evidence_gate_correction"] \
                    = ctx.pop(
                        "delivery_evidence_gate_correction")
            if ctx.get(
                    "delivery_length_gate_correction") \
                    is not None:
                ordered[
                    "delivery_length_gate_correction"] \
                    = ctx.pop(
                        "delivery_length_gate_correction")
            if ctx.get("tool_shape_gate_correction") \
                    is not None:
                ordered["tool_shape_gate_correction"] \
                    = ctx.pop("tool_shape_gate_correction")
            ordered["case"] = package["case"]
            if working_set is not None:
                ordered["working_set"] = working_set
            if journal is not None:
                ordered["journal"] = journal
            ordered["tool_list"] = _derive_tool_menu(
                catalogue, deliverable=deliverable)
            for key in ("seat", "role", "instance_id",
                        "case_id", "case_version", "view",
                        "delta", "tools", "tool_results",
                        "standing_dispatches", "bounds",
                        "position"):
                ordered[key] = package[key]
            if ctx.get("presentation_declared"):
                # Staged onboarding (INDEX 544): where the
                # assembly's sealed record declares the
                # presentation contract, the package the
                # worker is woken with is the staged one —
                # built from this same derivation's
                # components, with the case dump, the view
                # and the delta left out entirely — and its
                # commitment is stashed for the iteration
                # event to record. Under the process-tree
                # successor (the room rebuild) the package
                # is the tree one — the opening package,
                # then one step package per tree step —
                # and its commitment takes the pointer
                # form: the presented working set stands
                # in the core verbatim as pointers, beside
                # the record set's hash.
                if ctx.get("presentation_contract") in (
                        _tool_policy.PRESENTATION_CONTRACT_V4,
                        _tool_policy.PRESENTATION_CONTRACT_V5,
                        _tool_policy.PRESENTATION_CONTRACT_V6,
                        _tool_policy.PRESENTATION_CONTRACT_V7,
                        _tool_policy.PRESENTATION_CONTRACT_V8,
                        _tool_policy.PRESENTATION_CONTRACT_V9,
                        _tool_policy.PRESENTATION_CONTRACT_V10,
                        _tool_policy.PRESENTATION_CONTRACT_V11,
                        _tool_policy.PRESENTATION_CONTRACT_V12):
                    package = self._build_cycle_package(
                        ctx, package, ordered, catalogue)
                    if ctx.get("road") is not None:
                        # The road's presentation pass
                        # (the §6 amendment): spill and
                        # shedding applied to the built
                        # package BEFORE its commitment
                        # is taken, so the hash the
                        # iteration event records is the
                        # hash of the package the worker
                        # actually receives.
                        package = \
                            self._apply_road_presentation(
                                ctx, package)
                    ctx["presentation_hash"] = \
                        _cycle_presentation_hash(
                            package,
                            ctx.get("working_set_hash"))
                elif ctx.get("presentation_contract") == \
                        _tool_policy.PRESENTATION_CONTRACT_V3:
                    package = self._build_tree_package(
                        ctx, package, ordered, catalogue)
                    ctx["presentation_hash"] = \
                        _presentation_hash(
                            package,
                            ctx.get("working_set_hash"),
                            pointer_form=True)
                else:
                    package = self._build_staged_package(
                        ctx, package, ordered, catalogue)
                    ctx["presentation_hash"] = \
                        _presentation_hash(
                            package, ctx.get("working_set_hash"),
                            pointer_form=ctx.get(
                                "presentation_contract") == _tool_policy.PRESENTATION_CONTRACT_V2)
            else:
                package = ordered
        return package, head

    def _build_staged_package(self, ctx, base, ordered,
                              catalogue):
        """One staged wake package (staged onboarding,
        INDEX 544): assembled from the same derivation the
        ordered package used — the base package's recorded
        furniture and the ordered package's governed
        components — rearranged into the stage this wake
        walks. Every value derives from the record: the
        pinned case's components, the sealed declarations,
        the recorded outcomes — so the checker re-derives
        the package whole from the same record and any
        divergence (a skipped or reordered stage, the case
        dump smuggled back, a dashboard out of shape)
        breaks the iteration's presentation commitment.
        The bounds stand without the seconds-remaining
        figure for the same reason: that figure is the
        wall clock's, not the record's, and a committed
        package must be the record's alone."""
        content = ctx["content"] or {}
        iteration = ctx["iterations"] + 1
        ceiling = ctx["bounds"]["step_ceiling"]
        stage = _staged_stage(iteration)
        onboarding = _staged_onboarding(content)
        headline = onboarding["headline"] \
            if onboarding is not None else \
            "The job in your briefcase"
        deliverable = onboarding["deliverable"] \
            if onboarding is not None else None
        if deliverable is None and \
                isinstance(ctx.get("delivery"), dict):
            deliverable = ctx["delivery"].get("destination")
        deliverable_text = deliverable \
            if isinstance(deliverable, str) else \
            "the deliverable named in your case"
        if iteration == 1:
            cover_statement = STAGED_COVER_FIRST.format(
                seat=ctx["seat"], role=ctx["role"],
                headline=headline,
                deliverable=deliverable_text)
        elif stage == "dashboard":
            cover_statement = (
                f"{headline} — the deliverable: "
                f"{deliverable_text}. Step {iteration} of "
                f"{ceiling}; task in progress.")
        else:
            cover_statement = (
                f"{headline} — the deliverable: "
                f"{deliverable_text}. Step {iteration} of "
                f"{ceiling}; task in progress. Onboarding "
                f"stage {iteration} of 4: {stage}.")
        staged = {}
        for key in ("seat", "role", "instance_id",
                    "case_id", "case_version"):
            staged[key] = base[key]
        # The sealed contract's own presentation (INDEX
        # 544; the pointer-rule successor, INDEX 568):
        # the component names the contract the assembly
        # sealed — v1, or v2, whose directions and files
        # introduction tell the pointer truth and whose
        # working set stands as pointers below.
        contract = ctx.get("presentation_contract") \
            or _tool_policy.PRESENTATION_CONTRACT
        pointer_form = contract == \
            _tool_policy.PRESENTATION_CONTRACT_V2
        directions = STAGED_DIRECTIONS_V2 \
            if pointer_form else STAGED_DIRECTIONS
        staged["presentation"] = {
            "contract": contract,
            "stage": stage,
            "direction": directions[stage]}
        staged["cover"] = {
            "headline": headline,
            "deliverable": deliverable_text,
            "statement": cover_statement}
        if stage == "memory":
            # The snapshot (INDEX 549): where he stands
            # when he wakes — what was settled before he
            # arrived — riding before his memory, small,
            # and derived from the case's opening record
            # alone.
            staged["snapshot"] = _staged_snapshot(content)
            role_memory = content.get("role_memory")
            staged["memory"] = {
                "introduction": STAGED_MEMORY_INTRO,
                "entries": copy.deepcopy(role_memory)
                if isinstance(role_memory, list) else []}
        elif stage == "case":
            essentials = {
                "part": content.get("part"),
                "evidence_boundary": copy.deepcopy(
                    content.get("evidence_boundary")),
                "delivery": copy.deepcopy(
                    content["delivery"])
                if isinstance(content.get("delivery"),
                              dict) else None,
                "freshness": (
                    "suspended — no freshness refusal "
                    "applies to this job; your answers "
                    "are judged on the work"
                    if ctx.get("freshness_suspended")
                    else "in force — your answers are "
                         "judged against the record as it "
                         "stood when you were woken")}
            opening = content.get("opening")
            if isinstance(opening, dict) and opening:
                essentials["opening"] = copy.deepcopy(
                    opening)
            staged["case_essentials"] = essentials
        elif stage == "files":
            # The needed files (INDEX 549): the case's
            # glossary — the case's own statement of what
            # the job needs — each entry carrying its way
            # in beside its address: the concrete call,
            # naming a granted tool, that pulls that file.
            # And the worked example (INDEX 548): the
            # office's real call, with its real result,
            # sealed at generation — shown, not
            # described. Under the first contract the
            # call is the listing of the first file;
            # under the pointer-rule successor it is a
            # read of one of the map's files, with the
            # room-proof line standing beside it (the
            # calibration). Where no example was sealed
            # (the call could not be made), none is
            # presented and the introduction says so by
            # its shape.
            example = ctx.get("worked_example")
            if pointer_form:
                intro = STAGED_FILES_INTRO_V2 \
                    if example is not None \
                    else STAGED_FILES_INTRO_NO_EXAMPLE_V2
            else:
                intro = STAGED_FILES_INTRO \
                    if example is not None \
                    else STAGED_FILES_INTRO_NO_EXAMPLE
            files = {"introduction": intro,
                     "briefcase": []}
            glossary = content.get("glossary")
            if isinstance(glossary, list):
                for entry in glossary:
                    if isinstance(entry, dict) and \
                            isinstance(
                                entry.get("address"), str):
                        brief = {
                            "address": entry["address"],
                            "description":
                                entry.get("description")}
                        way = _staged_access_way(
                            catalogue, entry["address"])
                        if way is not None:
                            brief["access"] = way
                        files["briefcase"].append(brief)
            journal_path = _staged_journal_path(content)
            if journal_path is not None:
                files["journal"] = {
                    "path": journal_path,
                    "label": STAGED_JOURNAL_POINTER_V2
                    if pointer_form
                    else STAGED_JOURNAL_POINTER}
            if example is not None:
                files["worked_example"] = {
                    "label": STAGED_EXAMPLE_LABEL,
                    "call": {
                        "tool": example["tool"],
                        "parameters": {
                            "path": example["path"]}},
                    "result": copy.deepcopy(
                        example["result"])}
                if pointer_form:
                    # The room-proof line (the
                    # calibration): the proof stands
                    # beside the example only under the
                    # successor contract, whose example
                    # is the read the line speaks of.
                    files["worked_example"]["proof"] = \
                        STAGED_EXAMPLE_PROOF
            staged["files"] = files
        elif stage == "task":
            task = {"assignment": content.get("assignment"),
                    "deliverable": deliverable_text}
            # The third gate drawn before it bites
            # (INDEX 557): where the case declares the
            # delivery's length floor and the door
            # honours it, the task stage's deliverable
            # statement states the floor in words — the
            # worker reads the minimum in his task
            # before he can deliver against it.
            floor = ctx.get("delivery_floor")
            if floor is not None:
                statement = \
                    STAGED_TASK_FLOOR_STATEMENT_V2 \
                    if pointer_form \
                    else STAGED_TASK_FLOOR_STATEMENT
                task["delivery_floor"] = statement.format(
                    min_words=floor["min_words"])
            verification = content.get("verification_list")
            if isinstance(verification, list):
                task["verification_list"] = copy.deepcopy(
                    verification)
            staged["task"] = task
        else:
            addresses = []
            glossary = content.get("glossary")
            if isinstance(glossary, list):
                for entry in glossary:
                    if isinstance(entry, dict) and \
                            isinstance(
                                entry.get("address"), str):
                        addresses.append(entry["address"])
            journal_path = _staged_journal_path(content)
            staged["pointers"] = [
                {"item": "your memory",
                 "pointer": "presented at your first wake "
                            "(onboarding stage 1); it "
                            "stands in your case in this "
                            "office"},
                {"item": "your case",
                 "pointer": "presented at your second "
                            "wake (onboarding stage 2): "
                            "the frame, the evidence "
                            "boundary and the delivery "
                            "declaration"},
                {"item": "your files",
                 "pointer": "the briefcase map from your "
                            "third wake (onboarding "
                            "stage 3): "
                            + ("; ".join(addresses)
                               if addresses else
                               "no files stand in the "
                               "briefcase's map")},
                {"item": "your journal",
                 "pointer": journal_path
                 if journal_path is not None else
                 "no journal is designated for this job"},
                {"item": "your task",
                 "pointer": "presented at your fourth "
                            "wake (onboarding stage 4), "
                            "with your tool menu grouped "
                            "by the job's phases"}]
        staged["step_position"] = {
            "statement": f"step {iteration} of {ceiling}",
            "iteration": iteration,
            "step_ceiling": ceiling}
        staged["task_status"] = "in progress"
        if ordered.get("delivery_gate_correction") \
                is not None:
            staged["delivery_gate_correction"] = \
                ordered["delivery_gate_correction"]
        if ordered.get("delivery_stage_gate_correction") \
                is not None:
            staged["delivery_stage_gate_correction"] = \
                ordered["delivery_stage_gate_correction"]
        if ordered.get(
                "delivery_evidence_gate_correction") \
                is not None:
            staged["delivery_evidence_gate_correction"] \
                = ordered[
                    "delivery_evidence_gate_correction"]
        if ordered.get(
                "delivery_length_gate_correction") \
                is not None:
            staged["delivery_length_gate_correction"] \
                = ordered[
                    "delivery_length_gate_correction"]
        if ordered.get("tool_shape_gate_correction") \
                is not None:
            staged["tool_shape_gate_correction"] = \
                ordered["tool_shape_gate_correction"]
        staged["tool_results"] = base["tool_results"]
        if ordered.get("working_set") is not None:
            if pointer_form:
                # The pointer rule applied to the set
                # itself (INDEX 568): the record-side set
                # stands in this package as pointers —
                # derived from the record at this moment,
                # exactly as the record-side set was.
                staged["working_set"] = \
                    _presented_working_set_pointers(
                        ordered["working_set"],
                        self.doorway.store.all_events(),
                        ctx["assembly_id"], catalogue)
            else:
                staged["working_set"] = \
                    ordered["working_set"]
        if stage == "task":
            staged["tool_list"] = _derive_tool_menu(
                catalogue, deliverable=deliverable)
        if stage in ("files", "task", "dashboard"):
            staged["tools"] = base["tools"]
        staged["standing_dispatches"] = \
            base["standing_dispatches"]
        staged["bounds"] = {
            "iteration": iteration,
            "steps_used": ctx["iterations"],
            "step_ceiling": ceiling,
            "deadline_seconds":
                ctx["bounds"]["deadline_seconds"]}
        staged["position"] = base["position"]
        return staged

    def _record_step_gate_if_owed(self, ctx):
        """The step gate's firing (the room rebuild):
        at the build of a tree package past the first,
        where the tree's current GATHER step stands
        incomplete and the record shows it partly done
        or work standing ahead of it, record the gate
        and stash its correction for the package. The
        derivation runs over the record as it stands
        before this package's snapshot, so the gate's
        facts are true at presentation. A gate that
        cannot be recorded raises here — package
        construction fails and the run stalls
        runtime_failure, fail closed, as the family's
        gates do. The worker's work is never refused:
        the gate governs only the presentation."""
        ctx["step_gate_correction"] = None
        if ctx["iterations"] < 1:
            return
        doorway = self.doorway
        events = doorway.store.all_events()
        state = doorway.state()
        head = state["head_seq"]
        tstate = _tree_state(
            events, state["dispatches"],
            ctx["instance_id"], head, ctx["content"],
            ctx["iterations"] + 1)
        if tstate is None:
            raise ValueError(
                "the assembly is sealed under the "
                "process-tree presentation contract but "
                "the pinned case carries no well-formed "
                "process tree; no tree package can be "
                "built")
        owed = _tree_step_gate_owed(tstate)
        if owed is None:
            return
        step, address, missing, ahead = owed
        gate_ev = doorway.record_step_gate(
            ctx["assembly_id"],
            ctx.get("iteration_event_seq"), step,
            address, missing)
        ctx["recorded"].append(gate_ev)
        ctx["step_gate_correction"] = \
            _step_gate_correction(
                step, address, missing, ahead,
                tstate["journal_path"])

    def _record_cycle_events_if_owed(self, ctx):
        """The cycle contract's gate records (the plan
        §5): at the build of a cycle package past the
        first, the journal's transitions and refusals
        standing in the record but not yet recorded as
        events are recorded, and a cycle gate owed at
        this wake is recorded — all BEFORE the package's
        snapshot, so the events stand inside the
        package's head and their facts are true at
        presentation, exactly as the step gate's are.
        The corrections the events earn are stashed for
        the package: the cycle gate's where one was
        recorded at this build (or stands recorded
        against the previous iteration and not yet
        answered), and the journal gate's likewise. A
        record that cannot be made raises here — package
        construction fails and the run stalls
        runtime_failure, fail closed, as the family's
        gates do. The worker's work is never refused:
        the gates govern only the presentation."""
        ctx["cycle_gate_correction"] = None
        ctx["journal_gate_correction"] = None
        if ctx["iterations"] < 1:
            return
        doorway = self.doorway
        events = doorway.store.all_events()
        state = doorway.state()
        head = state["head_seq"]
        generated = doorway._generated_payload(
            ctx["assembly_id"])
        # The file-grain successor (office-cycle-v8):
        # the same records at the file grain — the
        # journal transitions and refusals recorded
        # exactly as here (the chain is the chain;
        # its attribution runs in file numbers), and
        # the cycle gate owed only where a later
        # FILE's work ran ahead, never between a
        # file's own parts.
        file_grain = ctx.get(
            "presentation_contract") in (
            _tool_policy.PRESENTATION_CONTRACT_V11,
            _tool_policy.PRESENTATION_CONTRACT_V12)
        if file_grain:
            cstate = _cycle_state_v8(
                events, state["dispatches"],
                ctx["instance_id"], head, ctx["content"],
                generated, ctx["iterations"] + 1)
        else:
            cstate = _cycle_state(
                events, state["dispatches"],
                ctx["instance_id"], head, ctx["content"],
                generated, ctx["iterations"] + 1)
        if cstate is None:
            raise ValueError(
                "the assembly is sealed under the "
                "office-cycle presentation contract but "
                "the sealed block map does not stand "
                "against the pinned case, or the case "
                "designates no journal; no cycle package "
                "can be built")
        previous_seq = ctx.get("iteration_event_seq")
        recorded_appends = set()
        recorded_gates = set()
        for ev in events:
            if ev["type"] == "JOURNAL_APPEND":
                recorded_appends.add(
                    ev["payload"].get("write_seq"))
            elif ev["type"] == "JOURNAL_GATE":
                recorded_gates.add(
                    ev["payload"].get("write_seq"))
        for transition in cstate["chain"]["transitions"]:
            if transition["write_seq"] in recorded_appends:
                continue
            ev = doorway.record_journal_append(
                ctx["assembly_id"], previous_seq,
                cstate["attribution"].get(
                    transition["write_seq"]),
                transition["write_seq"],
                transition["before_sha256"],
                transition["after_sha256"],
                transition["added_bytes"])
            ctx["recorded"].append(ev)
            recorded_appends.add(transition["write_seq"])
        for refusal in cstate["chain"]["refusals"]:
            if refusal["write_seq"] in recorded_gates:
                continue
            ev = doorway.record_journal_gate(
                ctx["assembly_id"], previous_seq,
                refusal["write_seq"],
                refusal["accepted_sha256"],
                refusal["attempted_sha256"])
            ctx["recorded"].append(ev)
            recorded_gates.add(refusal["write_seq"])
        # The corrections this wake answers: the latest
        # cycle gate and journal gate standing against
        # the previous iteration — recorded at this
        # build or an earlier one, answered once, in
        # the first package built after them.
        events = doorway.store.all_events()
        for ev in events:
            payload = ev["payload"]
            if payload.get("assembly_id") != \
                    ctx["assembly_id"]:
                continue
            if ev["type"] == "CYCLE_GATE" and \
                    payload.get("iteration_seq") == \
                    previous_seq:
                ctx["cycle_gate_correction"] = \
                    _cycle_gate_correction_v8(
                        payload, cstate["journal_path"],
                        cstate["files"]) \
                    if file_grain else \
                    _cycle_gate_correction(
                        payload, cstate["journal_path"])
            elif ev["type"] == "JOURNAL_GATE" and \
                    payload.get("iteration_seq") == \
                    previous_seq:
                ctx["journal_gate_correction"] = \
                    _journal_gate_correction(
                        payload, cstate["journal_path"])
        if file_grain:
            owed = _cycle_gate_owed_v8(cstate)
            if owed is None:
                return
            cycle, mine, ahead = owed
            already = any(
                ev["type"] == "CYCLE_GATE"
                and ev["payload"].get("iteration_seq")
                == previous_seq
                for ev in events)
            if already:
                return
            # The gate event at the file grain: its
            # cycle is the current file's number, and
            # both files are anchored by their first
            # blocks — the current file's own first
            # block, and the ahead file's first block
            # whose read stands.
            ahead_block = next(
                block for block in ahead["blocks"]
                if block["read_stands"])
            gate_ev = doorway.record_cycle_gate(
                ctx["assembly_id"], previous_seq, cycle,
                mine["blocks"][0]["block_id"],
                mine["address"],
                ahead_block["block_id"],
                ahead["address"])
            ctx["recorded"].append(gate_ev)
            ctx["cycle_gate_correction"] = \
                _cycle_gate_correction_v8(
                    gate_ev["payload"],
                    cstate["journal_path"],
                    cstate["files"])
            return
        owed = _cycle_gate_owed(cstate)
        if owed is None:
            return
        cycle, mine, ahead = owed
        already = any(
            ev["type"] == "CYCLE_GATE"
            and ev["payload"].get("iteration_seq")
            == previous_seq
            for ev in events)
        if already:
            return
        gate_ev = doorway.record_cycle_gate(
            ctx["assembly_id"], previous_seq, cycle,
            mine["block_id"], mine["address"],
            ahead["block_id"], ahead["address"])
        ctx["recorded"].append(gate_ev)
        ctx["cycle_gate_correction"] = \
            _cycle_gate_correction(
                gate_ev["payload"], cstate["journal_path"])

    def _build_cycle_package(self, ctx, base, ordered,
                             catalogue):
        """One wake package under the office-cycle
        contract (the plan of 2026-11-25): the opening
        package at the first wake — his identity and
        role memory as his own knowledge, the task
        whole, the cycle poster with the sealed block
        map and an access way per block, the journal's
        address and contract, and his position — and at
        every later wake a cycle package: his position,
        the blocks with their states (a gathered block
        as a pointer, carrying its dispatch provenance),
        the current cycle spelled out with its block's
        way in, and the current block's content
        presented exactly once, at its cycle, the first
        wake its read stands. When every cycle stands
        complete the package is the SUMMARIZE package.
        The journal stands in no package — no component,
        no excerpt; a journal read's own result is
        presented once, in the results carriage of the
        wake after the pull, like any newest result, and
        stubbed after. The package's tools are the offer
        set (the cycle's tools plus the journal tools);
        the catalogue as presented matter rides no
        package. Every value derives from the record,
        so the checker re-derives the package whole."""
        content = ctx["content"] or {}
        iteration = ctx["iterations"] + 1
        ceiling = ctx["bounds"]["step_ceiling"]
        head = base["position"]
        doorway = self.doorway
        events = doorway.store.all_events()
        state = fold(events, doorway.store.get_run_id())
        generated = doorway._generated_payload(
            ctx["assembly_id"])
        # The split-on-return successor (office-cycle-
        # v2): the same derivation, forked where its
        # presentation rule differs — the opening
        # carries the room's rules once, the results
        # carriage carries only what the wake presents,
        # and the cycle gate's correction does not ride
        # (see the carriage and the correction attach
        # below). Everything else in this builder is
        # the two contracts' shared derivation.
        # The cleaned-opening successor (office-cycle-
        # v4): the same derivation again — its cycle
        # and summarize packages are v3's whole (the
        # split carriage and the draft-page texts) —
        # forked at the opening alone, where the JSON
        # component assembly is replaced by the
        # director's plain-text structure.
        # The carryover successor (office-cycle-v5):
        # the same derivation again — its opening is
        # v4's whole (the director's structure, its
        # contract line naming this seal) — forked in
        # the cycle and summarize packages: the
        # statement line formatted from the sealed
        # delivery declaration, the gates' corrections
        # riding again, the journal's standing content
        # carried as his draft so far, and the cycle
        # instruction stating the one next step.
        # The zero-carryover successor (office-cycle-
        # v6): the same derivation again — its opening
        # is v5's whole — forked in the cycle and
        # summarize packages against v5: the journal
        # draft component does not attach (the
        # director's reversal — zero carryover; the
        # journal stands in his scratch and he reads
        # it himself), the cycle direction states
        # that truth again with the journal's own
        # address, and the blocks component is
        # slimmed to each block's place and state.
        # V5's statement line and its riding
        # corrections stand unchanged, the next step
        # included: they are the intro the director's
        # ruling keeps.
        # The imperative-first successor (office-
        # cycle-v7): the same derivation again — its
        # opening is v6's whole — forked in every
        # package against v6 by one rule of order:
        # the package opens with the Next line, the
        # one next step stated as an imperative,
        # derived at presentation from the cycle
        # state it opens (the director's order of
        # 2026-11-25 22:41 MST, after demo-gptoss9's
        # packages described state and left the
        # deciding to the worker). On the opening
        # the line stands after the outcome frame,
        # before the director's structure; on cycle
        # and summarize packages it is the package's
        # first component, the gates' corrections
        # standing below it unmerged. Everything
        # else is v6's whole: zero carryover, the
        # slimmed blocks, the statement line from
        # the seal, the riding corrections.
        # The file-grain successor (office-cycle-
        # v8): the same derivation again — its
        # opening is v7's whole in form (the frame,
        # the Next line, the director's structure)
        # rendered at the file grain, and its cycle
        # and summarize packages are v7's whole in
        # discipline (the Next line first, zero
        # carryover, the statement line from the
        # seal, the corrections riding) with the
        # FILE as the walk's unit: the cycle state
        # is the file state, the bookkeeping lists
        # files, and a multi-part file's slices are
        # plumbing inside its step — presented in
        # sequence as they land, gated never.
        file_grain = ctx.get(
            "presentation_contract") in (
            _tool_policy.PRESENTATION_CONTRACT_V11,
            _tool_policy.PRESENTATION_CONTRACT_V12)
        imperative_first = ctx.get(
            "presentation_contract") in (
                _tool_policy.PRESENTATION_CONTRACT_V10,
                _tool_policy.PRESENTATION_CONTRACT_V11,
                _tool_policy.PRESENTATION_CONTRACT_V12)
        carryover = ctx.get(
            "presentation_contract") == \
            _tool_policy.PRESENTATION_CONTRACT_V8
        zero_carryover = ctx.get(
            "presentation_contract") in (
                _tool_policy.PRESENTATION_CONTRACT_V9,
                _tool_policy.PRESENTATION_CONTRACT_V10,
                _tool_policy.PRESENTATION_CONTRACT_V11,
                _tool_policy.PRESENTATION_CONTRACT_V12)
        cleaned_opening = ctx.get(
            "presentation_contract") == \
            _tool_policy.PRESENTATION_CONTRACT_V7 \
            or carryover or zero_carryover
        draft_page = ctx.get(
            "presentation_contract") == \
            _tool_policy.PRESENTATION_CONTRACT_V6 \
            or cleaned_opening
        split_return = draft_page or ctx.get(
            "presentation_contract") == \
            _tool_policy.PRESENTATION_CONTRACT_V5
        contract_value = \
            _tool_policy.PRESENTATION_CONTRACT_V12 \
            if ctx.get("presentation_contract") == \
            _tool_policy.PRESENTATION_CONTRACT_V12 else \
            _tool_policy.PRESENTATION_CONTRACT_V11 \
            if file_grain else \
            _tool_policy.PRESENTATION_CONTRACT_V10 \
            if imperative_first else \
            _tool_policy.PRESENTATION_CONTRACT_V9 \
            if zero_carryover else \
            _tool_policy.PRESENTATION_CONTRACT_V8 \
            if carryover else \
            _tool_policy.PRESENTATION_CONTRACT_V7 \
            if cleaned_opening else \
            _tool_policy.PRESENTATION_CONTRACT_V6 \
            if draft_page else \
            _tool_policy.PRESENTATION_CONTRACT_V5 \
            if split_return else \
            _tool_policy.PRESENTATION_CONTRACT_V4
        # The draft-page successor's texts
        # (office-cycle-v3): the same derivation,
        # with the seven journal-defining wordings
        # exchanged for the draft-page variants.
        # Under v1 and v2 the standing texts are
        # selected, exactly as before.
        cover_first = CYCLE_COVER_FIRST_V3 \
            if draft_page else CYCLE_COVER_FIRST
        direction_summarize = \
            CYCLE_DIRECTION_SUMMARIZE_V3 \
            if draft_page else \
            CYCLE_DIRECTION_SUMMARIZE
        poster_intro = CYCLE_POSTER_INTRO_V3 \
            if draft_page else CYCLE_POSTER_INTRO
        journal_contract = \
            CYCLE_JOURNAL_CONTRACT_V3 \
            if draft_page else CYCLE_JOURNAL_CONTRACT
        pull_instruction = \
            CYCLE_PULL_INSTRUCTION_V3 \
            if draft_page else CYCLE_PULL_INSTRUCTION
        read_stands_instruction = \
            CYCLE_READ_STANDS_INSTRUCTION_V3 \
            if draft_page else \
            CYCLE_READ_STANDS_INSTRUCTION
        summarize_instruction = \
            CYCLE_SUMMARIZE_INSTRUCTION_V3 \
            if draft_page else \
            CYCLE_SUMMARIZE_INSTRUCTION
        # The carryover successor's directions
        # (office-cycle-v5): the cycle direction can
        # no longer say the journal is not carried —
        # under this contract it rides as his draft —
        # and the summarize direction names the
        # carried draft; selected here, beside the
        # other text selections, and standing texts
        # otherwise.
        direction_cycle = CYCLE_DIRECTION_CYCLE_V5 \
            if carryover else CYCLE_DIRECTION_CYCLE
        if carryover:
            direction_summarize = \
                CYCLE_DIRECTION_SUMMARIZE_V5
        if file_grain:
            cstate = _cycle_state_v8(
                events, state["dispatches"],
                ctx["instance_id"], head, content,
                generated, iteration)
        else:
            cstate = _cycle_state(
                events, state["dispatches"],
                ctx["instance_id"], head, content,
                generated, iteration)
        if cstate is None:
            raise ValueError(
                "the assembly is sealed under the "
                "office-cycle presentation contract but "
                "the sealed block map does not stand "
                "against the pinned case, or the case "
                "designates no journal; no cycle package "
                "can be built")
        # The process tree (office-cycle-v9): the one
        # computation, derived here from the cycle
        # state this package already stands on; the
        # opening carries its text, every later
        # package carries it as a component, and the
        # results carriage's speaking refusal renders
        # from it below.
        tree_computation = None
        if ctx.get("presentation_contract") == \
                _tool_policy.PRESENTATION_CONTRACT_V12 \
                and ctx.get("tree") is not None:
            tree_computation = _tree_computation(
                ctx["tree"], cstate, iteration,
                ctx.get("deliverable_filed") is not None)
            # The speaking refusal enriches the
            # base carriage HERE, before either
            # return path derives its own carriage
            # from it — one computation, one place,
            # both paths carry it.
            _tree_speaking_refusals(
                base["tool_results"], tree_computation)
        if file_grain:
            # The file-grain successor's cycle
            # direction (office-cycle-v8): the
            # standing truth in the job's own units,
            # with the journal's own address
            # formatted in. The summarize direction
            # keeps the standing selection, as under
            # v6 and v7.
            direction_cycle = \
                CYCLE_DIRECTION_CYCLE_V8.format(
                    journal=cstate["journal_path"])
        elif zero_carryover:
            # The zero-carryover successor's cycle
            # direction (office-cycle-v6): the
            # standing truth stated again with the
            # journal's own address — not carried,
            # standing in his scratch, read by pull —
            # formatted here, where the cycle state
            # (and with it the journal's address)
            # stands derived. The summarize direction
            # keeps the standing selection: it already
            # sends him to read his journal whole in
            # his room.
            direction_cycle = \
                CYCLE_DIRECTION_CYCLE_V6.format(
                    journal=cstate["journal_path"])
        onboarding = _staged_onboarding(content)
        headline = onboarding["headline"] \
            if onboarding is not None else \
            "The job in your briefcase"
        deliverable = onboarding["deliverable"] \
            if onboarding is not None else None
        if deliverable is None and \
                isinstance(ctx.get("delivery"), dict):
            deliverable = ctx["delivery"].get(
                "destination")
        deliverable_text = deliverable \
            if isinstance(deliverable, str) else \
            "the deliverable named in your case"
        # The sealed delivery declaration's own
        # destination (the carryover successor's
        # statement ground, office-cycle-v5): the
        # loop's delivery declaration — the generated
        # record's, verified equal to the case's own
        # and contribution-routed at the context's
        # derivation — read for its destination,
        # never the onboarding prose, whose
        # deliverable sentence is the case's authored
        # text and not the seal. Where no declaration
        # stands, the standing fallback serves, as
        # everywhere in this builder.
        delivery_destination = None
        if isinstance(ctx.get("delivery"), dict):
            delivery_destination = ctx["delivery"].get(
                "destination")
        if not isinstance(delivery_destination, str):
            delivery_destination = deliverable_text
        total = len(cstate["files"]) if file_grain \
            else len(cstate["blocks"])
        current = cstate["current"]
        summarize = current is None
        package = {}
        for key in ("seat", "role", "instance_id",
                    "case_id", "case_version"):
            package[key] = base[key]
        if iteration == 1 and cleaned_opening:
            # The cleaned opening (office-cycle-v4):
            # no JSON component assembly stands in
            # this package — the director's plain-
            # text structure, rendered from the
            # sealed case, is the opening's whole
            # content beyond the identity keys, and
            # the adapter renders it behind the
            # compressed outcome frame. The shared
            # tail below still stands: the offer set
            # is the package's tools, the split
            # carriage carries the (empty) first
            # results, and the position is the base
            # package's own.
            destination = None
            if isinstance(ctx.get("delivery"), dict):
                destination = ctx["delivery"].get(
                    "destination")
            if not isinstance(destination, str):
                destination = deliverable_text
            floor = ctx.get("delivery_floor")
            package["presentation"] = {
                "contract": contract_value,
                "package": "opening"}
            if file_grain:
                # The file-grain successor's opening
                # (office-cycle-v8): the first FILE's
                # Next line stands between the frame
                # and the director's structure, as
                # under v7 — and the structure itself
                # is the director's, rendered at the
                # file grain: the sources one line
                # per file, the method as the file
                # rhythm, the position counting
                # files. The parts stand only inside
                # their file's line, as plumbing.
                package["opening_text"] = \
                    _cycle_next_line_v8(
                        cstate["files"][0],
                        cstate["journal_path"]) + \
                    "\n\n" + _cycle_opening_text_v8(
                        seat=package["seat"],
                        role=package["role"],
                        instance_id=package[
                            "instance_id"],
                        case_id=package["case_id"],
                        case_version=package[
                            "case_version"],
                        destination=destination,
                        points=list(
                            TREE_COMPOSE_POINTS),
                        min_words=floor["min_words"]
                        if isinstance(floor, dict)
                        else None,
                        files=cstate["files"],
                        catalogue=catalogue,
                        journal_path=cstate[
                            "journal_path"],
                        total=total,
                        contract=contract_value)
                if tree_computation is not None:
                    # The tree in the opening package:
                    # its text stands after the
                    # director's structure — the map,
                    # in hand from the first wake.
                    package["opening_text"] += \
                        "\n\n" + _tree_text(
                            tree_computation)
            elif imperative_first:
                # The imperative-first successor's
                # opening (office-cycle-v7): the
                # first block's Next line stands
                # between the outcome frame and the
                # director's structure — the adapter
                # renders the frame, then this text —
                # so the first words of the job he
                # reads are the step he is to take.
                # The structure itself is rendered
                # whole below, byte-identical to its
                # v4-through-v6 form but for the
                # contract line naming this seal.
                package["opening_text"] = \
                    _cycle_next_line_v7(
                        cstate["blocks"][0],
                        cstate["journal_path"]) + \
                    "\n\n" + _cycle_opening_text_v4(
                        seat=package["seat"],
                        role=package["role"],
                        instance_id=package[
                            "instance_id"],
                        case_id=package["case_id"],
                        case_version=package[
                            "case_version"],
                        destination=destination,
                        points=list(
                            TREE_COMPOSE_POINTS),
                        min_words=floor["min_words"]
                        if isinstance(floor, dict)
                        else None,
                        blocks=cstate["blocks"],
                        catalogue=catalogue,
                        journal_path=cstate[
                            "journal_path"],
                        total=total,
                        contract=contract_value)
            else:
                package["opening_text"] = \
                    _cycle_opening_text_v4(
                    seat=package["seat"],
                    role=package["role"],
                    instance_id=package["instance_id"],
                    case_id=package["case_id"],
                    case_version=package["case_version"],
                    destination=destination,
                    points=list(TREE_COMPOSE_POINTS),
                    min_words=floor["min_words"]
                    if isinstance(floor, dict)
                    else None,
                    blocks=cstate["blocks"],
                    catalogue=catalogue,
                    journal_path=cstate["journal_path"],
                    total=total,
                    contract=contract_value)
        elif iteration == 1:
            package["presentation"] = {
                "contract": contract_value,
                "package": "opening",
                "direction": CYCLE_DIRECTION_OPENING}
            package["cover"] = {
                "headline": headline,
                "deliverable": deliverable_text,
                "statement": cover_first.format(
                    seat=ctx["seat"], role=ctx["role"],
                    headline=headline,
                    deliverable=deliverable_text)}
            package["snapshot"] = _staged_snapshot(
                content)
            role_memory = content.get("role_memory")
            package["memory"] = {
                "introduction": STAGED_MEMORY_INTRO,
                "entries": copy.deepcopy(role_memory)
                if isinstance(role_memory, list) else []}
            essentials = {
                "part": content.get("part"),
                "evidence_boundary": copy.deepcopy(
                    content.get("evidence_boundary")),
                "delivery": copy.deepcopy(
                    content["delivery"])
                if isinstance(content.get("delivery"),
                              dict) else None,
                "freshness": (
                    "suspended — no freshness refusal "
                    "applies to this job; your answers "
                    "are judged on the work"
                    if ctx.get("freshness_suspended")
                    else "in force — your answers are "
                         "judged against the record as "
                         "it stood when you were woken")}
            opening = content.get("opening")
            if isinstance(opening, dict) and opening:
                essentials["opening"] = copy.deepcopy(
                    opening)
            package["case_essentials"] = essentials
            floor = ctx.get("delivery_floor")
            figures = STAGED_TASK_FLOOR_STATEMENT_V2 \
                .format(min_words=floor["min_words"]) \
                if floor is not None else \
                "The brief runs to about 600 words."
            package["task"] = {
                "introduction": CYCLE_TASK_INTRO,
                "assignment": content.get("assignment"),
                "deliverable": deliverable_text,
                "points": list(TREE_COMPOSE_POINTS),
                "figures": figures}
            poster_blocks = []
            for block in cstate["blocks"]:
                entry = {
                    "block_id": block["block_id"],
                    "address": block["address"],
                    "line_start": block["line_start"],
                    "line_end": block["line_end"],
                    "content_bytes":
                        block["content_bytes"],
                    "content_sha256":
                        block["content_sha256"],
                    "state": block["state"]}
                way = _cycle_access(block, catalogue)
                if way is not None:
                    entry["access"] = way
                poster_blocks.append(entry)
            package["poster"] = {
                "introduction": poster_intro,
                "cycles": total,
                "blocks": poster_blocks}
            if split_return:
                # The room's rules, stated once, in
                # the opening alone (office-cycle-v2):
                # the budget in plain figures, the
                # one-block-per-wake return, and the
                # consequence for pulling ahead. No
                # later package repeats them.
                package["poster"]["room_knowledge"] = \
                    CYCLE_ROOM_KNOWLEDGE
            package["journal"] = {
                "path": cstate["journal_path"],
                "contract": journal_contract}
        else:
            package["presentation"] = {
                "contract": contract_value,
                "package": "summarize" if summarize
                else "cycle",
                "direction": direction_summarize
                if summarize else direction_cycle}
            if file_grain:
                # The file-grain successor's
                # presentation (office-cycle-v8):
                # the position names the file, never
                # a cycle.
                package["presentation"]["file"] = \
                    current
            else:
                package["presentation"]["cycle"] = \
                    current
            if carryover or zero_carryover:
                # The statement line from the facts
                # (office-cycle-v5): the deliverable
                # named from the sealed delivery
                # declaration — the brief delivered as
                # the contribute outcome at the end of
                # the walk, the office filing it at
                # the declared destination, the v4
                # opening's own story — never the
                # onboarding prose, whose sentence
                # ("written with a tool") contradicted
                # that door in every cycle package of
                # the gptoss8 run. The zero-carryover
                # successor (office-cycle-v6) keeps
                # the line whole, by its brief: v5's
                # items 1–2 stand unchanged under it.
                statement_deliverable = (
                    f"the brief, delivered as your "
                    f"contribute outcome at the end "
                    f"of the walk; the office files "
                    f"it at {delivery_destination}")
            else:
                statement_deliverable = deliverable_text
            if summarize:
                statement = (
                    f"{headline} — the deliverable: "
                    f"{statement_deliverable}. Step "
                    f"{iteration} of {ceiling}; task in "
                    f"progress. "
                    + ("Every file stands complete: "
                       "summarize." if file_grain else
                       "Every cycle stands complete: "
                       "summarize."))
            else:
                statement = (
                    f"{headline} — the deliverable: "
                    f"{statement_deliverable}. Step "
                    f"{iteration} of {ceiling}; task in "
                    f"progress. "
                    + (f"File {current} of {total}."
                       if file_grain else
                       f"Cycle {current} of {total}."))
            package["cover"] = {"statement": statement}
        if iteration > 1:
            blocks_component = []
            for block in cstate["blocks"]:
                if zero_carryover:
                    # The slimmed blocks (office-cycle-
                    # v6; the director's tap of
                    # 2026-11-25 22:30 MST): the package
                    # carries the block's place and its
                    # state alone. The per-wake
                    # bookkeeping — the address, the
                    # range, the gathered block's
                    # fingerprint and size, its dispatch
                    # provenance — stands in the
                    # opening's source table and in the
                    # record, and nothing else loses it;
                    # the budget is spent on the intro
                    # and the work, not on re-carrying
                    # the map at every wake. (The
                    # slimming is what makes room, at
                    # the near-ceiling joints, for the
                    # corrections that ride again.)
                    blocks_component.append({
                        "block_id": block["block_id"],
                        "state": block["state"]})
                    continue
                entry = {
                    "block_id": block["block_id"],
                    "address": block["address"],
                    "line_start": block["line_start"],
                    "line_end": block["line_end"],
                    "state": block["state"]}
                if block["read_stands"]:
                    # A gathered block stands as its
                    # pointer (the plan §3): fingerprint,
                    # size and the dispatch provenance of
                    # the pull that gathered it. A block
                    # not yet pulled stands by its place
                    # alone — its fingerprint and size
                    # stand in the opening's poster, and
                    # the per-call budget (the plan §6)
                    # is spent on the current block's
                    # content, not on re-carrying the
                    # map at every wake.
                    entry["content_bytes"] = \
                        block["content_bytes"]
                    entry["content_sha256"] = \
                        block["content_sha256"]
                    if block["entry"] is not None:
                        source = block["entry"]
                        entry["dispatch_id"] = \
                            source.get("dispatch_id")
                        entry["request_id"] = \
                            source.get("request_id")
                        entry["outcome_event_seq"] = \
                            source.get(
                                "outcome_event_seq")
                blocks_component.append(entry)
            package["blocks"] = blocks_component
            if carryover:
                # The carryover (office-cycle-v5): the
                # journal's current content — the
                # accepted chain's standing text,
                # derived from the record at this
                # package's head — rides as the
                # package's centre, labelled his draft
                # so far, in cycle and summarize
                # packages alike: every step after the
                # opening is taken from his own words,
                # and the draft he is building is what
                # the package centres, not the
                # machinery's state.
                package["journal_draft"] = {
                    "path": cstate["journal_path"],
                    "label":
                        CYCLE_JOURNAL_DRAFT_LABEL_V5,
                    "content": cstate["chain"]
                        ["accepted"]}
            # Under the zero-carryover successor
            # (office-cycle-v6) the component above
            # does not attach at all — no package,
            # cycle or summarize, carries the
            # journal's content; the journal stands in
            # his scratch and he reads it himself.
            if summarize:
                package["current_cycle"] = {
                    "stage": "summarize",
                    # Under the carryover successor the
                    # instruction's destination is the
                    # sealed declaration's own (brief
                    # item 1: the stale prose stands in
                    # no v5 package, this one included);
                    # the standing contracts format it
                    # exactly as before. The zero-
                    # carryover successor (office-cycle-
                    # v6) formats it the same way — its
                    # intro sends him to read his journal
                    # and combine, and names the sealed
                    # destination.
                    "instruction":
                        summarize_instruction
                        .format(
                            journal=cstate["journal_path"],
                            deliverable=(
                                delivery_destination
                                if (carryover or
                                    zero_carryover) else
                                deliverable_text)),
                    "points": list(TREE_COMPOSE_POINTS),
                    "figures":
                        STAGED_TASK_FLOOR_STATEMENT_V2
                        .format(min_words=ctx[
                            "delivery_floor"]["min_words"])
                        if ctx.get("delivery_floor")
                        is not None else
                        "The brief runs to about 600 "
                        "words."}
            else:
                block = cstate["blocks"][current - 1]
                range_text = (
                    f", lines {block['line_start']} to "
                    f"{block['line_end']}"
                    if block["line_start"] is not None
                    else " — the whole file")
                component = {
                    "cycle": current,
                    "of": total,
                    "block_id": block["block_id"],
                    "address": block["address"],
                    "line_start": block["line_start"],
                    "line_end": block["line_end"]}
                if block["read_stands"]:
                    component["instruction"] = \
                        read_stands_instruction \
                        .format(
                            cycle=current, total=total,
                            block_id=block["block_id"],
                            address=block["address"],
                            range_text=range_text,
                            journal=cstate["journal_path"])
                else:
                    component["instruction"] = \
                        pull_instruction.format(
                            cycle=current, total=total,
                            block_id=block["block_id"],
                            address=block["address"],
                            range_text=range_text,
                            journal=cstate["journal_path"])
                if carryover or zero_carryover:
                    # The one next step (office-cycle-
                    # v5): the instruction states it in
                    # the job's plain words, derived
                    # from this cycle's state at
                    # presentation — the read and the
                    # append it feeds, or the append
                    # alone where the read stands — in
                    # place of the standing instruction's
                    # cycle narration. The zero-
                    # carryover successor (office-cycle-
                    # v6) keeps it whole: it is the
                    # intro's next part of the job, the
                    # one carry the director's ruling
                    # names.
                    component["instruction"] = \
                        _cycle_next_step_v5(
                            block, cstate["journal_path"])
                way = _cycle_access(block, catalogue)
                if way is not None:
                    component["access"] = way
                component["workaround"] = CYCLE_WORKAROUND
                if ctx.get("adapter_mode") == "native":
                    component["call_shape"] = (
                        "In this room your tools are "
                        "offered natively: call the tool "
                        "itself, with its arguments.")
                else:
                    component["call_shape"] = (
                        "In this room your tools are "
                        "called in the text shape: your "
                        "answer is one JSON object whose "
                        "outcome is \"tool_requests\", "
                        "with a requests list naming each "
                        "call — the tool's name and its "
                        "parameters.")
                package["current_cycle"] = component
                # The current block's content, presented
                # exactly once: at the first wake its
                # read stands and its cycle is current,
                # where it has not already been
                # presented at an earlier wake.
                if block["read_stands"]:
                    earlier = [
                        (ev["payload"].get("iteration"),
                         ev["payload"].get("cursor_to"))
                        for ev in events
                        if ev["type"] == "LOOP_ITERATION"
                        and ev["payload"].get(
                            "assembly_id")
                        == ctx["assembly_id"]
                        and isinstance(ev["payload"].get(
                            "iteration"), int)
                        and ev["payload"].get("iteration")
                        < iteration
                        and isinstance(ev["payload"].get(
                            "cursor_to"), int)]
                    presented = \
                        _cycle_presented_block_ids(
                            events, state["dispatches"],
                            ctx["instance_id"], content,
                            generated, earlier)
                    if block["block_id"] not in presented:
                        block_content = _block_content(
                            cstate["entries"], block)
                        if block_content is not None:
                            package["block_content"] = {
                                "block_id":
                                    block["block_id"],
                                "address":
                                    block["address"],
                                "content": block_content}
        if file_grain and iteration > 1:
            # The file-grain successor's components
            # (office-cycle-v8): the standing
            # construction above ran at the block
            # grain; its components are exchanged
            # here for the file-grain ones. The
            # bookkeeping lists FILES — each file's
            # place and state alone, in the slimmed
            # form — the current component names the
            # file and its next step, and the
            # block_content presents the current
            # file's most recently landed part whose
            # content has not stood presented at an
            # earlier wake: a file's parts present in
            # sequence inside its step, each exactly
            # once, and no part of any other file
            # presents here at all.
            package.pop("blocks", None)
            package.pop("current_cycle", None)
            package.pop("block_content", None)
            package["files"] = [
                {"file_id": entry["file_id"],
                 "state": entry["state"]}
                for entry in cstate["files"]]
            if summarize:
                package["current_file"] = {
                    "stage": "summarize",
                    "instruction":
                        summarize_instruction
                        .format(
                            journal=cstate[
                                "journal_path"],
                            deliverable=(
                                delivery_destination)),
                    "points": list(
                        TREE_COMPOSE_POINTS),
                    "figures":
                        STAGED_TASK_FLOOR_STATEMENT_V2
                        .format(min_words=ctx[
                            "delivery_floor"]
                            ["min_words"])
                        if ctx.get("delivery_floor")
                        is not None else
                        "The brief runs to about 600 "
                        "words."}
            else:
                current_file = cstate["files"][
                    current - 1]
                component = {
                    "file": current,
                    "of": total,
                    "file_id": current_file["file_id"],
                    "address": current_file["address"],
                    "instruction":
                        _cycle_next_step_v8(
                            current_file,
                            cstate["journal_path"])}
                if len(current_file["blocks"]) == 1:
                    way = _cycle_access(
                        current_file["blocks"][0],
                        catalogue)
                    if way is not None:
                        component["access"] = way
                component["workaround"] = \
                    CYCLE_WORKAROUND
                if ctx.get("adapter_mode") == "native":
                    component["call_shape"] = (
                        "In this room your tools are "
                        "offered natively: call the tool "
                        "itself, with its arguments.")
                else:
                    component["call_shape"] = (
                        "In this room your tools are "
                        "called in the text shape: your "
                        "answer is one JSON object whose "
                        "outcome is \"tool_requests\", "
                        "with a requests list naming each "
                        "call — the tool's name and its "
                        "parameters.")
                package["current_file"] = component
                earlier = [
                    (ev["payload"].get("iteration"),
                     ev["payload"].get("cursor_to"))
                    for ev in events
                    if ev["type"] == "LOOP_ITERATION"
                    and ev["payload"].get(
                        "assembly_id")
                    == ctx["assembly_id"]
                    and isinstance(ev["payload"].get(
                        "iteration"), int)
                    and ev["payload"].get("iteration")
                    < iteration
                    and isinstance(ev["payload"].get(
                        "cursor_to"), int)]
                presented = _v8_presented_parts(
                    events, state["dispatches"],
                    ctx["instance_id"], content,
                    generated, earlier)
                part = _v8_current_part(
                    cstate, presented)
                if part is not None:
                    block_content = _block_content(
                        cstate["entries"], part)
                    if block_content is not None:
                        package["block_content"] = {
                            "block_id":
                                part["block_id"],
                            "address":
                                part["address"],
                            "content": block_content}
        for key in ("delivery_gate_correction",
                    "delivery_stage_gate_correction",
                    "delivery_evidence_gate_correction",
                    "delivery_length_gate_correction",
                    "tool_shape_gate_correction"):
            if ordered.get(key) is not None:
                package[key] = ordered[key]
        if ctx.get("cycle_gate_correction") is not None \
                and (not split_return or carryover
                     or zero_carryover):
            # Under the split-on-return successor the
            # gate's event stands in the record exactly
            # as under v1, but its correction does not
            # ride the package: the metered presentation
            # itself — the current cycle's instruction,
            # the ahead blocks standing as pointers —
            # and the opening's standing lines carry
            # the correction's whole content, and the
            # correction component on a batch wake was
            # itself part of what pushed that wake over
            # the per-call budget the run died on.
            # Under the carryover successor
            # (office-cycle-v5) the correction rides
            # again, by the director's order: derived
            # fresh at this build from the gate event
            # standing against the previous iteration —
            # what arrived, the cycle the walk stands
            # on, and the append that advances it — so
            # a worker whose work ran ahead can see
            # what the walk is waiting for. The journal
            # gate's correction below rides under every
            # contract, this one included, in the same
            # derived-fresh shape.
            package["cycle_gate_correction"] = \
                ctx["cycle_gate_correction"]
        if ctx.get("journal_gate_correction") is not None:
            package["journal_gate_correction"] = \
                ctx["journal_gate_correction"]
        package["tools"] = _cycle_offer_set(
            catalogue, cstate, summarize)
        if split_return:
            # The split-on-return carriage (office-
            # cycle-v2): the wake carries only what it
            # presents. A block read's result rides
            # only where its block is the current
            # cycle's — stubbed to the block_content
            # component where the content stands
            # there, or answered with its content
            # where the pull is a re-pull of the
            # current block after its presentation.
            # Every other block's read result does not
            # ride: its block stands as its pointer in
            # the blocks component, and its content is
            # presented when its cycle comes. The
            # journal read stands as it arrived, as
            # under v1; listings, searches, writes and
            # failures are not block contents and stand
            # as they arrived.
            if file_grain:
                # The file-grain successor's carriage
                # (office-cycle-v8): the split rule at
                # the file grain — the current file's
                # reads ride (the presented part
                # stubbed to the block_content
                # component, the file's other parts
                # dropped to their pointers in the
                # files component), and no other
                # file's read rides at all.
                v8_part = None
                if "block_content" in package and \
                        current is not None:
                    for block in cstate["files"][
                            current - 1]["blocks"]:
                        if block["block_id"] == \
                                package["block_content"][
                                    "block_id"]:
                            v8_part = block
                            break
                package["tool_results"] = \
                    _cycle_split_carriage_v8(
                        base["tool_results"],
                        state["dispatches"], cstate,
                        current, v8_part)
            else:
                package["tool_results"] = \
                    _cycle_split_carriage(
                        base["tool_results"],
                        state["dispatches"], cstate,
                        current,
                        "block_content" in package)
            package["position"] = base["position"]
            if imperative_first and iteration > 1:
                # The imperative-first successor
                # (office-cycle-v7): the package is
                # rebuilt with the Next line as its
                # first component — the adapter
                # renders the package in its own
                # order, so the first words of the
                # package proper are the step he is
                # to take, and every component below
                # it, the gates' corrections
                # included, stands as its support,
                # unmerged. The line is derived
                # here, at the package's completion,
                # from the cycle state it opens: the
                # current block and whether its read
                # stands, or the combine where every
                # cycle stands complete; a standing
                # cycle or journal gate correction
                # makes the append the step that
                # passes, as the helper derives it.
                if file_grain:
                    # The file-grain successor's Next
                    # line (office-cycle-v8): derived
                    # from the FILE state — the read
                    # of the file or its next part, the
                    # append where the file's read
                    # stands or a gate's correction
                    # stands answered, the combine
                    # where every file stands
                    # complete.
                    next_line = _cycle_next_line_v8(
                        None if summarize else
                        cstate["files"][current - 1],
                        cstate["journal_path"],
                        refused=(
                            ctx.get(
                                "cycle_gate_correction")
                            is not None
                            or ctx.get(
                                "journal_gate_correction")
                            is not None))
                else:
                    next_line = _cycle_next_line_v7(
                        None if summarize else
                        cstate["blocks"][current - 1],
                        cstate["journal_path"],
                        refused=(
                            ctx.get(
                                "cycle_gate_correction")
                            is not None
                            or ctx.get(
                                "journal_gate_correction")
                            is not None))
                package = {
                    "next_step": next_line,
                    **package}
            if tree_computation is not None:
                package["process_tree"] = {
                    "text": _tree_text(tree_computation),
                    "nodes": tree_computation["nodes"]}
            return package
        # The tool results: the carriage carries the
        # newest response's results (the base package's
        # own derivation), and a block read's content
        # stands in it under the presentation rule
        # alone — presented where the pull is a re-pull
        # of an earlier block (answered once, here) or
        # a journal read (his pull of his own notebook,
        # answered once, here; the journal itself is
        # never a component), and stubbed where the
        # content stands in this package's block_content
        # (the current block, freshly read) or belongs
        # to a later block (stubbed until its cycle).
        # Listings and searches are not block contents:
        # they stand as they arrived. Failures keep
        # their standing shapes.
        tool_results = copy.deepcopy(base["tool_results"])
        dispatch_tools = {
            did: d.get("tool")
            for did, d in state["dispatches"].items()}
        entries_by_dispatch = {
            entry.get("dispatch_id"): entry
            for entry in cstate["entries"]}
        blocks_by_address = {}
        for block in cstate["blocks"]:
            blocks_by_address.setdefault(
                block["address"], []).append(block)
        for entry in tool_results:
            if entry.get("outcome") != "result":
                continue
            tool = dispatch_tools.get(
                entry.get("dispatch_id"))
            if tool not in ("sandbox.read",
                            "sandbox.read_range"):
                continue
            result = entry.get("result")
            if not isinstance(result, dict) or \
                    "content" not in result:
                continue
            gathered = entries_by_dispatch.get(
                entry.get("dispatch_id"))
            path = gathered.get("path") \
                if gathered is not None else None
            if path == cstate["journal_path"]:
                continue
            served = (gathered.get("served") or {}) \
                if gathered is not None else {}
            cycles = set()
            for block in blocks_by_address.get(
                    path, []):
                if served.get("kind") == "whole":
                    cycles.add(block["cycle"])
                elif served.get("kind") == "range" and \
                        isinstance(
                            served.get("start_line"), int) \
                        and isinstance(
                            served.get("end_line"), int):
                    first = block["line_start"] \
                        if block["line_start"] is not None \
                        else 1
                    last = block["line_end"] \
                        if block["line_end"] is not None \
                        else served["end_line"]
                    if served["start_line"] <= last and \
                            first <= served["end_line"]:
                        cycles.add(block["cycle"])
            if not cycles or current is None:
                continue
            if current in cycles and \
                    "block_content" in package:
                entry["result"] = _carriage_stub(
                    result, "block_content")
            elif max(cycles) > current:
                entry["result"] = _carriage_stub(
                    result, "its_cycle")
        if tree_computation is not None:
            # The tree component (the speaking
            # refusal was rendered into the base
            # carriage at the computation, above —
            # both return paths derive from it).
            package["process_tree"] = {
                "text": _tree_text(tree_computation),
                "nodes": tree_computation["nodes"]}
        package["tool_results"] = tool_results
        package["position"] = base["position"]
        return package

    def _tree_step_component(self, ctx, tstate,
                             catalogue, deliverable_text):
        """The current step, spelled out: what to do,
        the step's own tools (their catalogue entries,
        not the whole catalogue — that rode the
        opening), the shape this room calls them in,
        and the step's workaround text where the record
        has earned one."""
        current = tstate["current"]
        journal_path = tstate["journal_path"]
        step = {"node": current["id"],
                "kind": current["kind"]}
        floor = ctx.get("delivery_floor")
        figures = STAGED_TASK_FLOOR_STATEMENT_V2.format(
            min_words=floor["min_words"]) \
            if floor is not None else \
            "The brief runs to about 600 words."
        if current["kind"] == "gather":
            address = current["address"]
            step["address"] = address
            facts = tstate["gather_facts"][current["id"]]
            if facts["read_stands"]:
                step["instruction"] = \
                    TREE_GATHER_READ_STANDS_INSTRUCTION \
                    .format(address=address,
                            journal=journal_path)
            else:
                step["instruction"] = \
                    TREE_GATHER_INSTRUCTION.format(
                        address=address,
                        tool="sandbox.read",
                        journal=journal_path)
            step["tools"] = [
                copy.deepcopy(entry)
                for entry in catalogue
                if entry.get("tool") in (
                    "sandbox.read", "sandbox.write")]
            if ctx.get("adapter_mode") == "native":
                step["call_shape"] = (
                    "In this room your tools are offered "
                    "natively: call the tool itself, with "
                    "its arguments — sandbox.read with "
                    "{\"path\": \"" + address + "\"}; "
                    "sandbox.write with {\"path\": \""
                    + str(journal_path) + "\", "
                    "\"content\": \"<your journal as it "
                    "stands, plus the new bits>\"}.")
            else:
                step["call_shape"] = (
                    "In this room your tools are called "
                    "in the text shape: your answer is "
                    "one JSON object whose outcome is "
                    "\"tool_requests\", with a requests "
                    "list naming each call — the tool's "
                    "name and its parameters, as in "
                    "{\"tool\": \"sandbox.read\", "
                    "\"parameters\": {\"path\": \""
                    + address + "\"}}.")
        elif current["kind"] == "orient":
            first = next(
                (node for node in tstate["nodes"]
                 if node["kind"] == "gather"), None)
            step["instruction"] = \
                TREE_ORIENT_INSTRUCTION.format(
                    address=first["address"]
                    if first is not None else "")
            step["tools"] = []
        elif current["kind"] == "compose":
            step["instruction"] = \
                TREE_COMPOSE_INSTRUCTION
            step["points"] = list(TREE_COMPOSE_POINTS)
            step["deliverable"] = deliverable_text
            step["figures"] = figures
            step["tools"] = []
            step["call_shape"] = (
                "The brief itself is delivered at the "
                "next step, as your contribution.")
        else:
            destination = tstate["root"]
            gathers_done = all(
                tstate["gather_facts"][node["id"]][
                    "read_stands"]
                and tstate["gather_facts"][node["id"]][
                    "journal_stands"]
                for node in tstate["nodes"]
                if node["kind"] == "gather")
            compose_done = gathers_done and any(
                node["kind"] == "compose"
                and tstate["states"][node["id"]] == "done"
                for node in tstate["nodes"])
            if compose_done:
                step["instruction"] = \
                    TREE_DELIVER_AGAIN_INSTRUCTION.format(
                        destination=destination)
            else:
                step["instruction"] = \
                    TREE_DELIVER_INSTRUCTION.format(
                        destination=destination)
            step["deliverable"] = deliverable_text
            step["figures"] = figures
            step["tools"] = []
            step["call_shape"] = (
                "Your answer is one JSON object: "
                "{\"outcome\": \"contribute\", \"text\": "
                "\"<the brief's text>\"}.")
        return step

    def _build_tree_package(self, ctx, base, ordered,
                            catalogue):
        """One wake package under the process-tree
        contract (the room rebuild): the opening package
        at the first wake — his identity and role memory
        framed as his own knowledge, the sealed tree,
        the case essentials, the files map with access
        ways, the tool catalogue once, the journal with
        its contract — and at every later wake a step
        package: the tree with its node states, the
        current step spelled out, his journal verbatim,
        at most the current step's fresh content
        presented exactly once at its step, and pointers
        for everything else. Every value derives from
        the record, so the checker re-derives the
        package whole from the same record."""
        content = ctx["content"] or {}
        iteration = ctx["iterations"] + 1
        ceiling = ctx["bounds"]["step_ceiling"]
        head = base["position"]
        doorway = self.doorway
        events = doorway.store.all_events()
        state = fold(events, doorway.store.get_run_id())
        tstate = _tree_state(
            events, state["dispatches"],
            ctx["instance_id"], head, content, iteration)
        if tstate is None:
            raise ValueError(
                "the assembly is sealed under the "
                "process-tree presentation contract but "
                "the pinned case carries no well-formed "
                "process tree; no tree package can be "
                "built")
        onboarding = _staged_onboarding(content)
        headline = onboarding["headline"] \
            if onboarding is not None else \
            "The job in your briefcase"
        deliverable = onboarding["deliverable"] \
            if onboarding is not None else None
        if deliverable is None and \
                isinstance(ctx.get("delivery"), dict):
            deliverable = ctx["delivery"].get(
                "destination")
        deliverable_text = deliverable \
            if isinstance(deliverable, str) else \
            "the deliverable named in your case"
        current = tstate["current"]
        package = {}
        for key in ("seat", "role", "instance_id",
                    "case_id", "case_version"):
            package[key] = base[key]
        if iteration == 1:
            package["presentation"] = {
                "contract":
                    _tool_policy.PRESENTATION_CONTRACT_V3,
                "package": "opening",
                "direction": TREE_DIRECTION_OPENING}
            cover_statement = TREE_COVER_FIRST.format(
                seat=ctx["seat"], role=ctx["role"],
                headline=headline,
                deliverable=deliverable_text)
        else:
            if current is None:
                current_label = "complete"
            elif current["kind"] == "gather":
                current_label = \
                    f"gather {current['address']}"
            else:
                current_label = current["kind"]
            package["presentation"] = {
                "contract":
                    _tool_policy.PRESENTATION_CONTRACT_V3,
                "package": "step",
                "step": current["id"]
                if current is not None else None,
                "direction": TREE_DIRECTION_STEP}
            cover_statement = (
                f"{headline} — the deliverable: "
                f"{deliverable_text}. Step {iteration} "
                f"of {ceiling}; task in progress. "
                f"Current step: {current_label}.")
        package["cover"] = {
            "headline": headline,
            "deliverable": deliverable_text,
            "statement": cover_statement}
        if iteration == 1:
            package["snapshot"] = _staged_snapshot(
                content)
            role_memory = content.get("role_memory")
            package["memory"] = {
                "introduction": STAGED_MEMORY_INTRO,
                "entries": copy.deepcopy(role_memory)
                if isinstance(role_memory, list) else []}
            essentials = {
                "part": content.get("part"),
                "evidence_boundary": copy.deepcopy(
                    content.get("evidence_boundary")),
                "delivery": copy.deepcopy(
                    content["delivery"])
                if isinstance(content.get("delivery"),
                              dict) else None,
                "freshness": (
                    "suspended — no freshness refusal "
                    "applies to this job; your answers "
                    "are judged on the work"
                    if ctx.get("freshness_suspended")
                    else "in force — your answers are "
                         "judged against the record as "
                         "it stood when you were woken")}
            opening = content.get("opening")
            if isinstance(opening, dict) and opening:
                essentials["opening"] = copy.deepcopy(
                    opening)
            package["case_essentials"] = essentials
        package["process_tree"] = {
            "root": tstate["root"],
            "nodes": [
                dict(
                    {"id": node["id"],
                     "kind": node["kind"]},
                    **({"address": node["address"]}
                       if node["kind"] == "gather"
                       else {}),
                    state=tstate["states"][node["id"]])
                for node in tstate["nodes"]]}
        if current is not None:
            package["current_step"] = \
                self._tree_step_component(
                    ctx, tstate, catalogue,
                    deliverable_text)
        if iteration == 1:
            files = {"introduction": TREE_FILES_INTRO,
                     "briefcase": []}
            glossary = content.get("glossary")
            if isinstance(glossary, list):
                for entry in glossary:
                    if isinstance(entry, dict) and \
                            isinstance(
                                entry.get("address"), str):
                        brief = {
                            "address": entry["address"],
                            "description":
                                entry.get("description")}
                        way = _staged_access_way(
                            catalogue, entry["address"])
                        if way is not None:
                            brief["access"] = way
                        files["briefcase"].append(brief)
            if tstate["journal_path"] is not None:
                files["journal"] = {
                    "path": tstate["journal_path"],
                    "label": TREE_JOURNAL_LABEL}
            package["files"] = files
        # The call machinery, as in every package under
        # every contract: the full catalogue stands in
        # the package's tools at every wake, so any
        # call he makes resolves by name and executes
        # into the room — his work is never refused for
        # arriving off-step (a call the catalogue could
        # not name would resolve unknown_tool at
        # translation: a refusal with no dispatch, the
        # failure the director named — errors because
        # he tried to use a tool). The PRESENTATION
        # names only the current step's own tools (the
        # current_step component); the catalogue as
        # presented material rides the opening package
        # alone.
        package["tools"] = base["tools"]
        if tstate["journal_path"] is not None:
            package["journal"] = {
                "path": tstate["journal_path"],
                "label": TREE_JOURNAL_LABEL,
                "content": tstate["journal_content"]}
        for key in ("delivery_gate_correction",
                    "delivery_stage_gate_correction",
                    "delivery_evidence_gate_correction",
                    "delivery_length_gate_correction",
                    "tool_shape_gate_correction"):
            if ordered.get(key) is not None:
                package[key] = ordered[key]
        if ctx.get("step_gate_correction") is not None:
            package["step_gate_correction"] = \
                ctx["step_gate_correction"]
        if iteration > 1 and current is not None and \
                current["kind"] == "gather":
            facts = tstate["gather_facts"][current["id"]]
            if facts["read_stands"]:
                earlier = [
                    (ev["payload"].get("iteration"),
                     ev["payload"].get("cursor_to"))
                    for ev in events
                    if ev["type"] == "LOOP_ITERATION"
                    and ev["payload"].get("assembly_id")
                    == ctx["assembly_id"]
                    and isinstance(
                        ev["payload"].get("iteration"),
                        int)
                    and ev["payload"].get("iteration")
                    < iteration
                    and isinstance(
                        ev["payload"].get("cursor_to"),
                        int)]
                presented = _tree_presented_addresses(
                    events, state["dispatches"],
                    ctx["instance_id"], content, earlier)
                if current["address"] not in presented:
                    parts = [
                        {"served": copy.deepcopy(
                            entry["served"]),
                         "content": entry["content"]}
                        for entry in tstate["entries"]
                        if entry.get("path")
                        == current["address"]
                        and entry.get("tool") in (
                            "sandbox.read",
                            "sandbox.read_range")
                        and entry.get("content_carried")
                        and "content" in entry]
                    if parts:
                        package["current_content"] = {
                            "address": current["address"],
                            "parts": parts}
        # The tool results stand by their provenance
        # stubs: under the tree contract a retrieval
        # result's content is presented exactly once,
        # as the current step's fresh content — never
        # in the results carriage, whose entries keep
        # their identities and their failure
        # instructions, with the stub naming where the
        # content stands.
        tool_results = copy.deepcopy(base["tool_results"])
        dispatch_tools = {
            did: d.get("tool")
            for did, d in state["dispatches"].items()}
        for entry in tool_results:
            if entry.get("outcome") != "result":
                continue
            if dispatch_tools.get(
                    entry.get("dispatch_id")) not in \
                    _tool_policy.RETRIEVAL_TOOLS:
                continue
            result = entry.get("result")
            if not isinstance(result, dict) or \
                    "content" not in result:
                continue
            entry["result"] = _carriage_stub(
                result, "current_step")
        package["tool_results"] = tool_results
        if ordered.get("working_set") is not None:
            package["working_set"] = \
                _presented_working_set_pointers(
                    ordered["working_set"],
                    self.doorway.store.all_events(),
                    ctx["assembly_id"], catalogue)
        package["standing_dispatches"] = \
            base["standing_dispatches"]
        package["step_position"] = {
            "statement": f"step {iteration} of {ceiling}",
            "iteration": iteration,
            "step_ceiling": ceiling}
        package["task_status"] = "in progress"
        package["bounds"] = {
            "iteration": iteration,
            "steps_used": ctx["iterations"],
            "step_ceiling": ceiling,
            "deadline_seconds":
                ctx["bounds"]["deadline_seconds"]}
        package["position"] = base["position"]
        return package

    def _journal_component(self, ctx):
        """The worker's journal, as it stands at this
        wake (the orientation pass, Part A): the case
        designates the journal's path inside his scratch
        (the case content's "journal"); the component
        presents its current content, read from its
        resting place through the executor — the same
        resting places the combined configuration
        collects his brief from — labelled as his own
        working notes: orientation, not record, not
        memory; the framework does not treat it as fact.
        The notebook is his to write and rewrite:
        appending is the convention he asked for and
        follows, not a mechanism — nothing enforces
        append-only, and a wake presents whatever
        stands there, replaced whole if he replaced it.
        The label states the notebook's purpose in the
        terms his briefcase consultation gave it (run 6,
        2026-11-24): run 5's debrief established the
        journal stood in his packages unnoticed — present
        but unlabelled as his — so the component now
        names what it is for, in his words' substance,
        where it cannot sit as wallpaper.
        Carriage is bounded by the working-set budget's
        figure, honestly: whole where it fits; where it
        does not, the longest prefix of complete lines
        that fits, with the omission stated in the
        component — never a silent cut (where not even
        one line fits, the budget's worth of bytes
        stands carried and the note says the cut stands
        mid-note). No designation, no component; a
        designated journal with nothing standing yet
        presents empty, so he knows the notebook is his
        to start."""
        designated = (ctx["content"] or {}).get("journal")
        if not isinstance(designated, str) or \
                not designated.startswith("scratch/") or \
                ".." in designated.split("/"):
            return None
        component = {
            "path": designated,
            "label": "your journal — your notebook: "
                     "notes, decisions, where you left "
                     "off. It returns to you at every "
                     "wake, exactly as you left it, and "
                     "it is yours to write and rewrite. "
                     "Orientation, not record and not "
                     "memory: nothing here is treated "
                     "as fact.",
            "content": "",
            "bytes_total": 0,
            "bytes_carried": 0,
            "complete": True,
        }
        executor = self.executor
        if executor is None or not hasattr(
                executor, "read_designated_scratch"):
            return component
        found = executor.read_designated_scratch(
            designated)
        if found is None:
            return component
        resting, raw, also = found
        component["resting_place"] = resting
        if also is not None:
            component["also_stands_in"] = also
        total = len(raw)
        component["bytes_total"] = total
        budget = _tool_policy.WORKING_SET_CONTENT_BUDGET
        if total <= budget:
            component["content"] = raw.decode(
                "utf-8", errors="replace")
            component["bytes_carried"] = total
            return component
        carried = 0
        for line in raw.splitlines(keepends=True):
            if carried + len(line) > budget:
                break
            carried += len(line)
        if carried == 0:
            carried = budget
        component["content"] = raw[:carried].decode(
            "utf-8", errors="replace")
        component["bytes_carried"] = carried
        component["complete"] = False
        component["note"] = (
            f"your journal stands at {total} bytes; "
            f"the first {carried} bytes are carried "
            f"here and the rest stands uncarried in "
            f"your scratch this wake — it is not lost, "
            f"and you can pull it with your read tools.")
        return component

    def _attach_failure_instructions(self, tool_results,
                                     events, raw_delta, ctx,
                                     generated):
        """Attach the failure instruction to each failure or
        refusal entry in tool_results (Ben's gate ruling,
        INDEX 475; the freedom-first setup pass): what was
        asked, why it failed in plain terms, the working
        alternative that exists within his grants, and —
        where an identical call already failed in a failure
        the worker was actually shown — the repeat named
        with the step it failed at. A repeat is a
        presentation fact, not a record fact (the
        examiner's correction of the freedom-first pass):
        the earlier failure must stand at or before the
        cursor — the head the previous wake presented —
        so it stood in an earlier package; an identical
        failure from the same response batch stands after
        the cursor, in this package's own delta, and is
        not a repeat however identical, because the worker
        had not seen it when he made the call. And the
        repeat claims "for this reason" only where the
        earlier failure's plain reason stands established
        in the record and equals this entry's; otherwise
        it claims only that the same call previously
        failed. Everything is derived from the record
        snapshot the package itself is built from; an
        alternative is named only where his sealed grants
        and the case actually offer one — never invented.
        Entries whose identity cannot be established from
        the record carry no instruction rather than a
        guessed one."""
        content = ctx["content"] or {}
        requests = {}
        for ev in events:
            if ev["type"] == "TOOL_REQUESTED":
                p = ev["payload"]
                requests[p.get("request_id")] = (
                    p.get("tool"), p.get("parameters"))
        iterations = [
            ev["payload"].get("cursor_to")
            for ev in events
            if ev["type"] == "LOOP_ITERATION"
            and ev["payload"].get("instance_id")
            == ctx["instance_id"]]

        def step_of(seq):
            return sum(1 for c in iterations
                       if isinstance(c, int)
                       and not isinstance(c, bool)
                       and c < seq)

        def canon(parameters):
            if not isinstance(parameters, dict):
                return None
            return json.dumps(parameters, sort_keys=True)

        grounds = {}
        occurrences = []
        # Occurrences are collected from the whole snapshot,
        # not the delta: a repeat is a call that failed in an
        # EARLIER window, already presented and scrolled out
        # of the delta — the record remembers it even where
        # the package no longer carries it. Each occurrence
        # carries the failure's plain reason, derived exactly
        # as the presenting entry's why is derived below, so
        # the repeat may claim "for this reason" only where
        # the reasons stand established and equal; where a
        # reason cannot be established from the record it
        # stands as None, and the repeat claims the failure
        # alone. The translation reason is the very error
        # text the carriage derived for such an entry, from
        # the same catalogue names.
        catalogue_names = [t.get("tool") for t in
                           ctx.get("catalogue") or []
                           if isinstance(t, dict)
                           and t.get("tool")]
        if not catalogue_names:
            catalogue_names = [t.get("tool") for t in
                               content.get("tool_catalogue")
                               or [] if isinstance(t, dict)
                               and t.get("tool")]
        for ev in events:
            p = ev["payload"]
            if ev["type"] == "TOOL_OUTCOME" and \
                    p.get("outcome") == "failure":
                tool, params = requests.get(
                    p.get("request_id"), (None, None))
                reason = p.get("detail") or ""
                if "No such file or directory" in reason \
                        and isinstance(params, dict) and \
                        isinstance(params.get("path"), str):
                    reason = (f"no file stands at "
                              f"{params['path']} in your "
                              f"briefcase")
                occurrences.append((ev["event_seq"], (
                    "call", tool, canon(params)),
                    reason or None))
            elif ev["type"] == "REJECTION" and \
                    p.get("attempted_type") == "TOOL_DISPATCHED":
                grounds[p.get("request_id")] = p.get("ground")
                tool, params = requests.get(
                    p.get("request_id"), (None, None))
                occurrences.append((ev["event_seq"], (
                    "call", tool, canon(params)),
                    _plain_ground(p.get("ground")) or None))
            elif ev["type"] == "TRANSLATION_RECORDED":
                for centry in p.get("calls") or []:
                    if centry.get("refusal_class"):
                        occurrences.append((ev["event_seq"], (
                            "translation", centry.get("name"),
                            centry.get("arguments_sha256")),
                            _translation_error_text(
                                centry, catalogue_names)
                            or None))

        stocked = []
        for gentry in content.get("glossary") or []:
            if isinstance(gentry, dict):
                addr = gentry.get("address")
                if isinstance(addr, str) and \
                        addr.startswith("sources/"):
                    stocked.append(addr)
        if not stocked:
            boundary = content.get("evidence_boundary")
            if isinstance(boundary, str):
                stocked = re.findall(r"sources/[\w.\-]+",
                                     boundary)
            elif isinstance(boundary, list):
                stocked = [b for b in boundary
                           if isinstance(b, str)
                           and b.startswith("sources/")]
        grants = (generated or {}).get("grants") or []
        granted_tools = list(dict.fromkeys(
            g.get("tool") for g in grants
            if isinstance(g, dict) and g.get("tool")))
        offered_names = [t.get("tool") for t in
                         content.get("tool_catalogue") or []
                         if isinstance(t, dict)
                         and t.get("tool")]

        def alternative(tool, params, why_text):
            path = params.get("path") if isinstance(
                params, dict) else None
            if isinstance(path, str) and \
                    path.startswith("sources/") and \
                    stocked and path not in stocked:
                return (
                    "your briefcase holds: "
                    + ", ".join(stocked)
                    + " — pull one of those (sandbox.list "
                      "on sources/ shows each file with its "
                      "size). If the material you need is "
                      "not in your briefcase, say so in your "
                      "yield: asking is how the office "
                      "learns what to stock.")
            if "exhausted" in why_text and \
                    len(granted_tools) > 1:
                others = [t for t in granted_tools
                          if t != tool]
                return (
                    "that door's grant count is spent for "
                    "this run; your other granted doors "
                    "stand: " + ", ".join(others) + ".")
            if isinstance(path, str) and \
                    "matches" in why_text and \
                    "sandbox.read_range" in granted_tools:
                return (
                    "pull the section by line range "
                    "instead: sandbox.read_range with "
                    "start_line and end_line — the lines "
                    "named above are the matches.")
            if isinstance(path, str) and \
                    path.startswith("scratch/") and \
                    "no file stands" in why_text:
                return (
                    "scratch/ is your writing space and "
                    "nothing stands there yet — create it "
                    "with sandbox.write, or in your office "
                    "with container.exec.")
            if isinstance(path, str) and \
                    "container.exec" in granted_tools:
                return (
                    "read it inside your office instead: "
                    "container.exec with cmd [\"cat\", "
                    f"\"{path}\"] — the room serves the "
                    "whole file.")
            if tool is not None and offered_names and \
                    tool not in offered_names:
                return (
                    "the tools on offer are: "
                    + ", ".join(offered_names) + ".")
            return None

        for entry in tool_results:
            if entry.get("outcome") not in ("failure",
                                            "refused"):
                continue
            if entry.get("result") is not None:
                continue
            seq = entry.get("event_seq")
            tool = params = args_hash = None
            identity = None
            if entry.get("request_id") is not None or \
                    entry.get("dispatch_id") is not None:
                tool, params = requests.get(
                    entry.get("request_id"), (None, None))
                identity = ("call", tool, canon(params))
            elif entry.get("refusal_class"):
                for ev in raw_delta:
                    if ev["event_seq"] != seq or \
                            ev["type"] != \
                            "TRANSLATION_RECORDED":
                        continue
                    for centry in \
                            ev["payload"].get("calls") or []:
                        if centry.get("provider_call_id") \
                                == entry.get(
                                    "provider_call_id") and \
                                centry.get("refusal_class"):
                            tool = centry.get("name")
                            args_hash = centry.get(
                                "arguments_sha256")
                            identity = ("translation", tool,
                                        args_hash)
            if identity is None or tool is None:
                continue
            if entry.get("refusal_class") == "doorway_refused":
                why = _plain_ground(grounds.get(
                    entry.get("request_id"))) or \
                    entry.get("error") or ""
            elif entry.get("outcome") == "refused":
                why = entry.get("error") or ""
            else:
                why = entry.get("detail") or ""
                if "No such file or directory" in why and \
                        isinstance(params, dict) and \
                        isinstance(params.get("path"), str):
                    why = (f"no file stands at "
                           f"{params['path']} in your "
                           f"briefcase")
            instruction = {
                "asked": {"tool": tool,
                          "parameters": params}
                if args_hash is None else
                {"tool": tool,
                 "arguments_sha256": args_hash},
                "why": why,
                "alternative": alternative(tool, params, why),
            }
            # A repeat must have been PRESENTED in an
            # earlier wake (the examiner's correction):
            # the earlier occurrence stands at or before
            # the cursor — the head the previous wake
            # presented — so it stood in an earlier
            # package. An identical failure from the same
            # response batch stands after the cursor, in
            # this package's own delta, presented now for
            # the first time alongside this entry: not a
            # repeat, however identical, because the
            # worker had not seen it when he made this
            # call. The step named is the step the
            # relevant earlier failure was made at, by
            # the same cursor derivation as above; where
            # an earlier presented failure's plain reason
            # stands established and equals this entry's
            # why, the note may say "for this reason" —
            # otherwise it claims only that the same call
            # previously failed.
            cursor = ctx.get("cursor")
            earlier = [(s, r) for s, ident, r in occurrences
                       if ident == identity
                       and isinstance(cursor, int)
                       and not isinstance(cursor, bool)
                       and s <= cursor]
            if earlier:
                matching = [s for s, r in earlier
                            if r and why and r == why]
                if matching:
                    first_step = step_of(max(matching))
                    instruction["repeat"] = {
                        "already_failed_step": first_step,
                        "note": "this exact call already "
                                f"failed at step "
                                f"{first_step} for this "
                                "reason"}
                else:
                    first_step = step_of(max(
                        s for s, _r in earlier))
                    instruction["repeat"] = {
                        "already_failed_step": first_step,
                        "note": "this exact call already "
                                f"failed at step "
                                f"{first_step}"}
            entry["instruction"] = instruction

    def _relevant(self, ctx, ev):
        """Whether an event belongs in this activation's
        delta: the instance's own record (its requests,
        dispatches, outcomes, iteration bookkeeping, and the
        refusals recorded against it), the acts presented
        under its seat since activation, and the pinned case's
        own lifecycle. Everything else in the record is not
        this activation's work."""
        p = ev["payload"]
        if p.get("instance_id") == ctx["instance_id"]:
            return True
        if ev["type"] == "REJECTION" and \
                p.get("seat") == ctx["seat"] and \
                ev["event_seq"] > ctx["activated_seq"]:
            return True
        if ev["actor"] == ctx["seat"] and \
                ev["event_seq"] > ctx["activated_seq"]:
            return True
        if ev["type"].startswith("CASE_") and \
                p.get("case_id") == ctx["case_id"]:
            return True
        return False

    # ----------------------------------------------- validation
    @staticmethod
    def _validate(raw, native_mode=False):
        """Validate a whole response before anything is
        effected (R49): ("proposals", {"proposals": [...],
        "tool_requests": [...]}) / ("yield", summary) /
        ("decline", reason) / ("malformed", detail).
        Validation is all-or-nothing for shape; what it passes
        is adjudicated per act afterwards. Terminal outcomes
        are mutually exclusive — a yield or decline combined
        with anything is malformed whole. The native adapter
        piece adds one outcome, under a native-judged
        assembly only: ("native", [extraction records]) —
        the adapter's per-call extraction of a native
        response's tool calls, whose classification is the
        native preflight's, not this validation's."""
        if not isinstance(raw, dict):
            return "malformed", "the response is not an outcome"
        outcome = raw.get("outcome")
        if outcome == "native_calls":
            if not native_mode:
                return "malformed", \
                    "a native_calls outcome stands only " \
                    "under a native-judged assembly"
            if set(raw) != {"outcome", "native_calls"}:
                return "malformed", \
                    "a native_calls outcome carries its " \
                    "extraction records and nothing else"
            records = Loop._validate_extraction(
                raw.get("native_calls"))
            if records is None:
                return "malformed", "the native extraction " \
                    "records are not well-formed"
            return "native", records
        if outcome == "decline":
            if set(raw) != {"outcome", "reason"} or \
                    not isinstance(raw.get("reason"), str):
                return "malformed", \
                    "a decline carries a reason only"
            return "decline", raw["reason"]
        if outcome == "yield":
            if set(raw) != {"outcome", "summary"} or \
                    not isinstance(raw.get("summary"), str) or \
                    not raw["summary"].strip():
                return "malformed", \
                    "a yield carries a summary only"
            return "yield", raw["summary"]
        if outcome == "tool_requests":
            if set(raw) != {"outcome", "tool_requests"}:
                return "malformed", \
                    "a tool_requests outcome carries its " \
                    "requests and nothing else"
            requests = Loop._validate_requests(
                raw.get("tool_requests"))
            if requests is None:
                return "malformed", "the tool requests are " \
                    "not well-formed"
            return "proposals", {"proposals": [],
                                 "tool_requests": requests}
        if outcome == "proposals":
            if not set(raw) <= {"outcome", "proposals",
                                "tool_requests"} or \
                    "proposals" not in raw:
                return "malformed", \
                    "a proposals outcome carries proposals " \
                    "and optionally tool requests, nothing else"
            proposals = Loop._validate_proposals(
                raw.get("proposals"))
            if proposals is None:
                return "malformed", "the proposals are not " \
                    "well-formed acts"
            requests = []
            if "tool_requests" in raw:
                requests = Loop._validate_requests(
                    raw["tool_requests"])
                if requests is None:
                    return "malformed", "the tool requests " \
                        "are not well-formed"
            return "proposals", {"proposals": proposals,
                                 "tool_requests": requests}
        return "malformed", f"unknown outcome {outcome!r}"

    @staticmethod
    def _validate_extraction(raw):
        """Well-formed per-call extraction records (native
        adapter piece, B1): a non-empty list, one record per
        call in emitted order, each naming exactly its
        provider ordinal (its position, 1-based), its
        provider call ID (the emitted string, or None where
        none stands), its name (the emitted string, or None
        where unreadable), its arguments form — "string"
        (the arguments stand as the raw string the provider
        emitted, unparsed: extraction is structural only,
        INDEX 406), "object" (the arguments stand as the
        emitted object) or "non_object" (the arguments
        stand as emitted, neither string nor object) — and
        the arguments in the form's shape. One further field
        may stand: wire_name, the name as it stood on the
        wire, present exactly where the route's name
        translation renamed the call at extraction (Ben's
        ruling, 2026-11-24) — the record's name is then the
        canonical name, and the wire name is kept beside it
        so both stand visible. Anything else is malformed
        whole: the loop classifies records it can trust,
        and trusts only this shape."""
        if not isinstance(raw, list) or not raw:
            return None
        out = []
        for position, entry in enumerate(raw, start=1):
            if not isinstance(entry, dict) or \
                    not {"provider_ordinal",
                         "provider_call_id", "name",
                         "arguments_form",
                         "arguments"} <= set(entry) <= \
                    {"provider_ordinal", "provider_call_id",
                     "name", "arguments_form", "arguments",
                     "wire_name"}:
                return None
            if entry["provider_ordinal"] != position:
                return None
            call_id = entry["provider_call_id"]
            if call_id is not None and (
                    not isinstance(call_id, str) or not call_id):
                return None
            name = entry["name"]
            if name is not None and (
                    not isinstance(name, str) or not name):
                return None
            wire_name = entry.get("wire_name")
            if wire_name is not None and (
                    not isinstance(wire_name, str)
                    or not wire_name):
                return None
            form = entry["arguments_form"]
            if form == "object":
                if not isinstance(entry["arguments"], dict):
                    return None
            elif form == "string":
                if not isinstance(entry["arguments"], str):
                    return None
            elif form == "non_object":
                if isinstance(entry["arguments"],
                              (dict, str)):
                    return None
            else:
                return None
            validated = {
                "provider_ordinal": position,
                "provider_call_id": call_id,
                "name": name,
                "arguments_form": form,
                "arguments": entry["arguments"]}
            if wire_name is not None:
                validated["wire_name"] = wire_name
            out.append(validated)
        return out

    @staticmethod
    def _validate_proposals(raw):
        """Well-formed acts, in the driver's shape: a list of
        dicts naming a known event type with a dict payload —
        or None, malformed whole."""
        if not isinstance(raw, list):
            return None
        out = []
        for item in raw:
            if not isinstance(item, dict):
                return None
            type_ = item.get("type")
            payload = item.get("payload")
            if type_ not in EVENT_TYPES or \
                    not isinstance(payload, dict):
                return None
            out.append({"type": type_, "payload": dict(payload)})
        return out

    @staticmethod
    def _validate_requests(raw):
        """Well-formed tool requests: a non-empty list of
        dicts naming exactly a tool (a non-empty string) and
        its parameters (an object) — or None, malformed
        whole."""
        if not isinstance(raw, list) or not raw:
            return None
        out = []
        for entry in raw:
            if not isinstance(entry, dict) or \
                    set(entry) != {"tool", "parameters"} or \
                    not isinstance(entry.get("tool"), str) or \
                    not entry["tool"] or \
                    not isinstance(entry.get("parameters"), dict):
                return None
            out.append({"tool": entry["tool"],
                        "parameters": entry["parameters"]})
        return out

    # -------------------------------- native preflight (N20)
    def _classify_native(self, ctx, records):
        """Phase (i) of the native preflight: classify every
        individuable call in emitted order, each on its own
        merits, in the ruled order (the examiner's ordering
        ruling, INDEX 408) — call-ID integrity (N6) first,
        then the per-response cap (N22), then name
        readability and the closed-world catalogue
        determination against this package's catalogue
        (N7), then argument parsing and the canonical
        arguments hash (N32), then the pure schema
        validation (N8), for resolved calls only —
        producing the translation record's entry set and
        the converted requests, in emitted order. The
        determination precedes parsing, but an unknown
        name does not skip parsing: N32 requires the hash
        for calls that reach that stage, and the refusal
        precedence is the established one — a call whose
        arguments then fail stands malformed_call (an
        unknown name with unreadable arguments is
        malformed_call, not unknown_tool), its entry
        carrying no resolution standing, resolution
        not_reached, exactly as the doorway's coherence
        for the class requires (N13); the determination
        was made, but a malformed call's disposition
        carries no resolution outcome in the record.
        No call's verdict waits on or is contaminated by
        another's. Returns (entries, converted): one entry
        per call with the N32 field set; the converted
        requests in the existing {"tool", "parameters"}
        shape, whose loop request identities the entries
        carry — assigned here, deterministically, in the
        order the adjudication below will present them."""
        catalogue = ctx.get("catalogue") or []
        by_name = {}
        for entry in catalogue:
            by_name.setdefault(entry["tool"], entry)
        entries = []
        converted = []
        seen_ids = {}
        presented = 0
        for record in records:
            ordinal = record["provider_ordinal"]
            call_id = record["provider_call_id"]
            entry = {
                "provider_ordinal": ordinal,
                "provider_call_id": call_id,
                "name": record["name"],
                "arguments_sha256": None,
                "resolution": "not_reached",
                "validation": "not_reached",
                "validation_constraint": None,
                "refusal_class": None,
                "refusal_detail": None,
                "loop_request_id": None}
            # The wire name, where the route's translation
            # renamed the call at extraction (Ben's ruling,
            # 2026-11-24): the translation record keeps
            # both names visible — the canonical name the
            # determination judges, and the name as it
            # stood on the wire.
            if record.get("wire_name") is not None:
                entry["wire_name"] = record["wire_name"]
            entries.append(entry)
            if call_id is not None and call_id not in seen_ids:
                seen_ids[call_id] = ordinal
            # Call-ID integrity (N6) is judged BEFORE the
            # cap (build-examination correction, INDEX
            # 403): a missing or duplicated ID is the
            # call's first defect, and an overflow call
            # carrying one is malformed_call, never masked
            # as a cap refusal. The cap still precedes
            # name resolution, argument parsing and schema
            # validation — an overflow call's arguments
            # are never processed.
            if call_id is None:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its call ID was absent"
                continue
            if seen_ids.get(call_id) != ordinal:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its call ID was duplicated"
                continue
            if ordinal > CALL_CAP:
                # Overflow (N22): identity and ordinal are
                # recorded; the call reaches neither name
                # resolution nor argument processing — not
                # resolved, not parsed, not validated, not
                # converted.
                entry["refusal_class"] = "call_cap_exceeded"
                continue
            if record["name"] is None:
                # Name readability is the determination
                # stage's first half: an unreadable name
                # cannot be determined against the
                # catalogue at all, and the call is
                # malformed before any argument work.
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its name could not be read"
                continue
            # The catalogue determination (N7) stands
            # here, before argument parsing (INDEX 408):
            # for a call that survived call-ID integrity
            # and the cap, whether its name resolves
            # against this package's catalogue is decided
            # now, from the name alone. No call refused
            # above reached this determination, and no
            # argument work precedes it for a call that
            # does.
            resolved = _resolve_against_catalogue(
                by_name, record["name"])
            # Argument parsing stands after the
            # determination (INDEX 406/408): only a call
            # that survived call-ID integrity and the cap
            # reaches it — a refused call's arguments are
            # never parsed, so the work the cap bounds is
            # the work performed — and an unknown name
            # does not skip it, because N32 requires the
            # parsed-arguments hash for calls reaching
            # this stage and the malformed-argument
            # classification is established precedence.
            # A string form parses now, in classification;
            # a string that cannot be read, and any form
            # that does not yield an object, is
            # malformed_call (N13) — the determination
            # extraction once made is classification's, at
            # the point the order reaches it.
            if record["arguments_form"] == "string":
                try:
                    arguments = _parse_arguments_string(
                        record["arguments"])
                except ValueError:
                    entry["refusal_class"] = "malformed_call"
                    entry["refusal_detail"] = \
                        "its arguments could not be read"
                    continue
                if not isinstance(arguments, dict):
                    entry["refusal_class"] = "malformed_call"
                    entry["refusal_detail"] = \
                        "its arguments are not an object"
                    continue
            elif record["arguments_form"] == "object":
                arguments = record["arguments"]
            else:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its arguments are not an object"
                continue
            # The arguments stand parsed: the hash is taken
            # over the parsed arguments' canonical form
            # (N32) — for a call the determination found
            # unknown exactly as for a resolved one; the
            # determination does not discard it.
            entry["arguments_sha256"] = sha256_hex(
                canonical(arguments))
            if resolved is None:
                entry["resolution"] = "unknown"
                entry["refusal_class"] = "unknown_tool"
                continue
            entry["resolution"] = "resolved"
            verdict, constraint = \
                _schema_validator.validate_arguments(
                    resolved["parameters"], arguments)
            if verdict != "valid":
                entry["validation"] = "invalid"
                entry["validation_constraint"] = constraint
                entry["refusal_class"] = "invalid_arguments"
                continue
            entry["validation"] = "valid"
            presented += 1
            entry["loop_request_id"] = (
                f"loop-{ctx['instance_id']}-"
                f"{ctx['iterations']}-{presented}")
            converted.append({"tool": record["name"],
                              "parameters": arguments})
        return entries, converted

    def _adjudicate_native(self, ctx, records, iteration_seq,
                           artifact_sha256):
        """The native corridor (N20's three phases, build
        brief B3): classify the whole response (phase i),
        persist the complete decision set as the translation
        record (phase ii), then dispatch the converted
        requests in emitted order through the ordinary
        adjudication (phase iii) — from conversion onward
        the iteration is indistinguishable from its
        text-mode twin (N9). If the translation record
        cannot be persisted, nothing from the response is
        dispatched and the iteration follows the
        record-failure path: a runtime_failure stall, fail
        closed (N15/N20). Refusals are collected in the
        run's result beside the dispatched outcomes (N19);
        they consume no dispatch, no grant bound and no
        step beyond this iteration, and are not stalls
        (N18). Returns "continue" or the stall result."""
        entries, converted = self._classify_native(ctx, records)
        try:
            ev = self.doorway.record_translation(
                ctx["assembly_id"], iteration_seq, entries,
                artifact_sha256=artifact_sha256,
                catalogue_hash=ctx.get("catalogue_hash"),
                registry_version=ctx.get("registry_version"))
        except DoorwayRefusal as refusal:
            return self._stall(
                ctx, "runtime_failure",
                detail=f"the translation record could not "
                       f"be persisted: {refusal.ground}; "
                       f"nothing from the response was "
                       f"dispatched (N20)")
        except Exception as exc:  # noqa: BLE001 — the
            # record mechanism itself unavailable: fail
            # closed, claim nothing was dispatched
            return self._stall(
                ctx, "runtime_failure",
                detail=f"the translation record could not "
                       f"be persisted "
                       f"({type(exc).__name__}: {exc}); "
                       f"nothing from the response was "
                       f"dispatched (N20)")
        ctx["recorded"].append(ev)
        for entry in entries:
            if entry["refusal_class"] is not None:
                ctx["refused"].append({
                    "type": "TRANSLATION_REFUSAL",
                    "provider_call_id":
                        entry["provider_call_id"],
                    "provider_ordinal":
                        entry["provider_ordinal"],
                    "ground": entry["refusal_class"]})
        self._adjudicate(ctx, {"proposals": [],
                               "tool_requests": converted})
        return "continue"

    # --------------------------------------------------- door
    def _delivered_result(self, ctx):
        """The loop's completion on a filing (door scope,
        2026-11-24): the successful-completion semantics
        are the yield's — the run stands complete because
        the deliverable stands filed — with the filing's
        facts carried in the result beside the summary."""
        return {"ok": True, "outcome": "yield",
                "summary": "the contributed deliverable "
                           "was filed by the office at "
                           + ctx["deliverable_filed"][
                               "destination"],
                "deliverable_filed":
                    ctx["deliverable_filed"],
                "instance_id": ctx["instance_id"],
                "assembly_id": ctx["assembly_id"],
                "iterations": ctx["iterations"],
                "recorded": ctx["recorded"],
                "refused": ctx["refused"],
                "dispatched": ctx["dispatched"],
                "call_timings": ctx["call_timings"]}

    def _file_deliverable(self, ctx, proposal, ev):
        """File one accepted contribution at the declared
        destination (door scope): the office's own write,
        through the loop/office layer's channel — the
        executor's sandbox tree, the run's scratch — never
        through the worker's sandbox grants, and recorded
        as DELIVERABLE_FILED with authorship and filing
        kept distinct. A filing that cannot be performed
        or recorded is the machinery's failure, named on
        the context for the caller's stall.

        The filing's integrity shape (the examiner's
        filing-integrity correction, 2026-11-24): the
        destination's prior state — absent, or its exact
        prior bytes — is captured before anything is
        written; the contributed bytes are written to a
        staging path in the same directory and renamed
        atomically onto the destination, so a partial
        write only ever exists at the staging path, never
        at the destination; the filing is then recorded.
        If any step of that sequence fails, the
        destination is rolled back to its prior state
        through the same staging route — a pre-existing
        worker draft is restored exactly, never deleted —
        and the loop stalls fail-closed with no filing
        standing and no unaccounted deliverable at the
        destination. If the rollback itself fails, a
        durable reconciliation note stands beside the
        destination naming the incomplete filing, so the
        state left behind is explicit and recoverable
        rather than silent. On the record side, a failed
        filing's pending insert is rolled back before
        the stall records; if that rollback itself
        fails, the pending transaction is discarded by
        resetting the store's connection, and if even
        that fails no stall is recorded on the poisoned
        connection — no later commit may land the
        discarded filing."""
        text = proposal["payload"].get("text")
        destination = ctx["delivery"]["destination"]
        if not isinstance(text, str) or not text:
            ctx["delivery_filing_error"] = (
                "the accepted contribution carries no "
                "text to file")
            return
        if self.executor is None or not getattr(
                self.executor, "sandbox_dir", None):
            ctx["delivery_filing_error"] = (
                "no office channel stands to file the "
                "deliverable (the loop holds no executor)")
            return
        if not destination.startswith("scratch/") or \
                ".." in destination.split("/"):
            ctx["delivery_filing_error"] = (
                f"the declared destination {destination!r} "
                f"does not stand under the run's scratch")
            return
        data = text.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()
        path = Path(self.executor.sandbox_dir) / \
            destination
        staging = path.with_name(
            path.name + ".filing-staging")
        try:
            prior = path.read_bytes() \
                if path.exists() else None
        except Exception as exc:  # noqa: BLE001 — the
            # prior state cannot even be read: fail closed
            # before anything is written, the destination
            # standing untouched
            ctx["delivery_filing_error"] = (
                f"the deliverable could not be filed: "
                f"the destination's prior state could "
                f"not be read ({type(exc).__name__}: "
                f"{exc})")
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            _filing_write(staging, data)
            staging.replace(path)
            filed_ev = self.doorway.record_deliverable_filed(
                ctx["assembly_id"], ev["event_seq"],
                destination, digest, ctx["seat"])
        except Exception as exc:  # noqa: BLE001 — the
            # filing machinery itself: roll the destination
            # back to its captured prior state and fail
            # closed, claiming no completion and leaving
            # no unaccounted deliverable
            #
            # The record side first (the examiner's
            # round-six correction): the filing's append
            # may have landed while its commit failed, so
            # the filing insert can stand pending in the
            # store's open transaction. Roll the
            # transaction back before anything else is
            # recorded, so the stall's own commit can
            # never land the discarded filing alongside
            # the terminal — the INDEX 314 pattern on the
            # disposition path. The only insert that can
            # stand pending here is the filing's own: the
            # contribution it files was committed by its
            # own route before the filing was attempted.
            # A rollback that itself fails is named in
            # the detail, not hidden — and the pending
            # transaction is then discarded by resetting
            # the store's connection (the examiner's
            # residual path): a later commit on the
            # original connection, the stall's own
            # included, could otherwise land the
            # discarded filing alongside the terminal.
            # If even the discard fails, the context is
            # marked poisoned and _stall records nothing
            # on this connection at all.
            rollback_problem = None
            discarded = False
            try:
                self.doorway.store.rollback()
            except Exception as rb_exc:  # noqa: BLE001
                rollback_problem = (
                    f"{type(rb_exc).__name__}: {rb_exc}")
                try:
                    self.doorway.store.\
                        discard_pending_transaction()
                    discarded = True
                except Exception as d_exc:  # noqa:
                    # BLE001 — named in the detail; the
                    # stall path is poisoned below
                    rollback_problem += (
                        "; discarding the pending "
                        "transaction also failed "
                        f"({type(d_exc).__name__}: "
                        f"{d_exc})")
                    ctx["record_transaction_poisoned"] = \
                        True
            problem = self._restore_filing_destination(
                path, staging, prior)
            detail = (
                f"the deliverable could not be filed: "
                f"{type(exc).__name__}: {exc}")
            if rollback_problem is not None:
                detail += (
                    "; the store transaction could not "
                    f"be rolled back ({rollback_problem})")
                if discarded:
                    detail += (
                        "; the pending transaction was "
                        "discarded by resetting the "
                        "store connection before anything "
                        "else was recorded")
                elif ctx.get(
                        "record_transaction_poisoned"):
                    detail += (
                        "; no stall is recorded on this "
                        "connection, so no later commit "
                        "can land the discarded filing")
            if problem is None:
                detail += ("; the destination was rolled "
                           "back to its prior state")
            else:
                self._leave_filing_reconciliation_note(
                    path, destination=destination,
                    contribution_seq=ev["event_seq"],
                    digest=digest, seat=ctx["seat"],
                    prior=prior,
                    failure=f"{type(exc).__name__}: "
                            f"{exc}",
                    rollback_problem=problem)
                detail += (
                    f"; the rollback also failed "
                    f"({problem}) and a reconciliation "
                    f"note stands beside the destination")
            ctx["delivery_filing_error"] = detail
            return
        try:
            staging.unlink(missing_ok=True)
        except OSError:
            pass
        ctx["recorded"].append(filed_ev)
        ctx["deliverable_filed"] = {
            "destination": destination,
            "sha256": digest,
            "authored_by": ctx["seat"],
            "filed_by": "office",
            "contribution_seq": ev["event_seq"],
            "filing_seq": filed_ev["event_seq"]}

    def _restore_filing_destination(self, path, staging,
                                    prior):
        """Roll a failed filing's destination back to its
        captured prior state, through the same staging +
        atomic-rename route the filing itself used: the
        prior bytes are restored exactly (a pre-existing
        worker draft is preserved, never deleted), or —
        where the destination stood absent — the file the
        office's rename placed there is removed (it is
        the office's own by construction). Staging
        residue is cleared either way. Returns None where
        the prior state stands restored, else a
        description of the rollback's own failure."""
        problem = None
        try:
            if prior is None:
                path.unlink(missing_ok=True)
            else:
                _filing_write(staging, prior)
                staging.replace(path)
        except Exception as exc:  # noqa: BLE001
            problem = f"{type(exc).__name__}: {exc}"
        try:
            staging.unlink(missing_ok=True)
        except OSError:
            pass
        return problem

    def _leave_filing_reconciliation_note(
            self, path, *, destination, contribution_seq,
            digest, seat, prior, failure,
            rollback_problem):
        """The double failure's durable account (the
        examiner's filing-integrity correction): where a
        filing failed AND its rollback failed, a JSON
        note stands beside the destination —
        <destination>.filing-incomplete.json in the run's
        sandbox — carrying what was attempted, the
        contribution the filing files (its record
        position and its content hash), the destination's
        captured prior state, and both failures, so the
        incomplete filing is explicit and recoverable: an
        examiner finds the note beside the deliverable
        destination, and the bytes the destination may
        hold are identified by the contribution's hash.
        A failure to leave even the note is swallowed —
        the stall's detail already names the rollback
        failure; there is no third line of defence to
        pretend at."""
        note = {
            "incomplete_filing": True,
            "destination": destination,
            "attempted": (
                "the office attempted to file the "
                "accepted contribution at the declared "
                "destination and record DELIVERABLE_"
                "FILED; the filing failed and the "
                "rollback to the destination's prior "
                "state also failed, so the destination "
                "may hold the contributed bytes with no "
                "filing event standing in the record"),
            "contribution_seq": contribution_seq,
            "content_sha256": digest,
            "authored_by": seat,
            "filed_by": "office",
            "prior_state": (
                "absent" if prior is None else {
                    "sha256": hashlib.sha256(
                        prior).hexdigest(),
                    "bytes": len(prior)}),
            "failure": failure,
            "rollback_failure": rollback_problem}
        note_path = path.with_name(
            path.name + ".filing-incomplete.json")
        try:
            note_path.write_text(
                json.dumps(note, indent=1) + "\n",
                encoding="utf-8")
        except OSError:
            pass

    def _try_delivery_gate(self, ctx, iteration_seq,
                           failure, seam):
        """The envelope gate's decision (door scope,
        2026-11-24): True where this failure is a
        recognisable attempted contribution under a
        standing delivery declaration in the working-set
        population — the gate event is recorded and the
        correction stashed for the next wake's package.
        The gate fires only on the governed path: the raw
        response and the parse failure stand preserved in
        the iteration's response-evidence artifact and
        disposition, settled before this decision. It may
        fire again on a later iteration within the step
        budget (each firing consumes its step); it grants
        nothing and dispatches nothing."""
        if self.evidence_store is None or \
                ctx.get("delivery") is None or \
                not ctx.get("working_set_declared"):
            return False
        raw = _response_content_of(seam)
        if raw is None or not \
                _recognised_contribution_attempt(raw):
            return False
        try:
            json.loads(raw.strip())
            return False  # it parses: not the gate's case
        except ValueError as exc:
            parse_error = f"{failure.detail} ({exc})"
        excerpt = raw[:500]
        try:
            ev = self.doorway.record_delivery_gate(
                ctx["assembly_id"], iteration_seq, excerpt,
                len(raw), parse_error)
        except Exception as exc:  # noqa: BLE001
            ctx["delivery_gate_error"] = (
                f"the delivery gate could not be "
                f"recorded: {type(exc).__name__}: {exc}")
            return False
        ctx["recorded"].append(ev)
        ctx["delivery_gate_correction"] = {
            "what_arrived": excerpt,
            "response_length": len(raw),
            "what_failed": parse_error,
            "instruction": (
                "Your previous response could not be "
                "read: it arrived as a contribution, but "
                "its envelope was not valid JSON, so "
                "nothing in it was accepted. Resend the "
                "contribution plainly, as one JSON object "
                "and nothing else: {\"outcome\": "
                "\"contribute\", \"text\": \"<your "
                "contribution>\"}.")}
        return True

    def _try_tool_shape_gate(self, ctx, iteration_seq,
                             failure, seam):
        """The tool-shape gate's decision (the
        calibration, from the GPT-OSS worker's
        debrief): True where this provider failure is
        the tool-use shape's refusal — the worker
        called a tool natively in a run judged for the
        text shape, where no native tools were offered,
        and the provider refused the whole generation,
        preserving the failed call in its error body.
        The gate event is recorded and the correction
        stashed for the next wake's package; the firing
        consumes the iteration, as the other gates'
        firings do, and it may fire again on a later
        iteration within the step budget. Narrow by
        construction: any other provider failure —
        rate limits, byte ceilings, timeouts, server
        errors — is not this gate's business and stalls
        as a provider failure exactly as it always
        has. A gate that cannot be recorded names its
        error on the context and returns False, and the
        caller stalls on the error — an unrecorded gate
        never becomes a continuation. The gate fires
        only on the governed path, where the refusal's
        evidence stands preserved and settled before
        this decision, as the envelope gate's does."""
        if ctx.get("adapter_mode") == "native":
            return False
        facts = _tool_shape_failure(failure, seam)
        if facts is None:
            return False
        address = None
        glossary = (ctx.get("content") or {}).get(
            "glossary")
        if isinstance(glossary, list):
            for entry in glossary:
                if isinstance(entry, dict) and \
                        isinstance(
                            entry.get("address"), str):
                    address = entry["address"]
                    break
        if address is None:
            # The correction's example names the case's
            # first glossary file; where no glossary
            # stands there is no example to teach with,
            # and the refusal is not converted.
            return False
        try:
            ev = self.doorway.record_tool_shape_gate(
                ctx["assembly_id"], iteration_seq,
                facts["http_status"], facts["error_code"],
                facts["error_message"],
                facts["tool_name"],
                facts["failed_generation"])
        except Exception as exc:  # noqa: BLE001
            ctx["tool_shape_gate_error"] = (
                f"the tool-shape gate could not be "
                f"recorded: {type(exc).__name__}: {exc}")
            return False
        ctx["recorded"].append(ev)
        ctx["tool_shape_gate_correction"] = \
            _tool_shape_gate_correction(
                facts["tool_name"], address)
        return True

    def _try_delivery_stage_gate(self, ctx, proposal, ev):
        """The stage gate's decision (round nine's
        correction pair, INDEX 548): True where this
        contribution is gated — offered under the
        presentation contract at the memory, case or
        files stage, before its task had been presented.
        The contribution act itself already stands in the
        record (the doorway recorded it before this
        decision, as it records every act); the gate
        records its own event naming that contribution
        and stashes the correction for the next wake's
        package. Nothing is filed and the loop does not
        complete; the firing consumes the iteration, as
        the envelope gate's does, and it may fire again
        on a later pre-task iteration within the step
        budget. A gate that cannot be recorded names its
        error on the context and still returns True —
        an unrecorded gate must never silently become a
        filing — and the caller stalls on the error.
        Everywhere else (no presentation contract, no
        delivery declaration, the task stage or later)
        the contribution is not the gate's business and
        adjudication proceeds exactly as it stands."""
        if not ctx.get("presentation_declared") or \
                ctx.get("delivery") is None:
            return False
        tree_form = ctx.get("presentation_contract") == \
            _tool_policy.PRESENTATION_CONTRACT_V3
        cycle_form = ctx.get("presentation_contract") in (
            _tool_policy.PRESENTATION_CONTRACT_V4,
            _tool_policy.PRESENTATION_CONTRACT_V5,
            _tool_policy.PRESENTATION_CONTRACT_V6,
            _tool_policy.PRESENTATION_CONTRACT_V7,
            _tool_policy.PRESENTATION_CONTRACT_V8,
            _tool_policy.PRESENTATION_CONTRACT_V9,
            _tool_policy.PRESENTATION_CONTRACT_V10,
            _tool_policy.PRESENTATION_CONTRACT_V11,
            _tool_policy.PRESENTATION_CONTRACT_V12)
        if cycle_form:
            # The cycle walk's progression replaces the
            # stage gate's function under this contract
            # (the plan §7): the contribution door opens
            # at SUMMARIZE, and a contribution offered
            # while a cycle stands incomplete — derived
            # from the record at the package head the
            # worker was woken from — is set aside
            # unfiled under the same gate event, its
            # stage the current cycle in cycle words,
            # and its correction names the incomplete
            # blocks explicitly, as blocks mapped to
            # their files.
            events = self.doorway.store.all_events()
            state = self.doorway.state()
            generated = self.doorway._generated_payload(
                ctx["assembly_id"])
            # The file-grain successor (office-cycle-
            # v8): the same gate at the file grain —
            # its stage the current file, its
            # correction naming the incomplete FILES.
            file_grain = ctx.get(
                "presentation_contract") in (
                _tool_policy.PRESENTATION_CONTRACT_V11,
                _tool_policy.PRESENTATION_CONTRACT_V12)
            if file_grain:
                cstate = _cycle_state_v8(
                    events, state["dispatches"],
                    ctx["instance_id"], ctx["cursor"],
                    ctx["content"], generated,
                    ctx["iterations"])
            else:
                cstate = _cycle_state(
                    events, state["dispatches"],
                    ctx["instance_id"], ctx["cursor"],
                    ctx["content"], generated,
                    ctx["iterations"])
            if cstate is None or \
                    cstate["current"] is None:
                return False
            if file_grain:
                stage = (f"file {cstate['current']} of "
                         f"{len(cstate['files'])}")
                cycle_missing = [
                    {"file_id": entry["file_id"],
                     "address": entry["address"]}
                    for entry in cstate["files"]
                    if entry["state"] != "done"]
            else:
                stage = (f"cycle {cstate['current']} of "
                         f"{len(cstate['blocks'])}")
                cycle_missing = [
                    {"block_id": block["block_id"],
                     "address": block["address"]}
                    for block in cstate["blocks"]
                    if block["state"] != "done"]
        elif tree_form:
            # The tree's progression replaces the stage
            # gate's function under this contract (the
            # room rebuild): the contribution door opens
            # at DELIVER, and a contribution offered
            # while the tree stands at an earlier step —
            # derived from the record at the package head
            # the worker was woken from — is set aside
            # unfiled under the same gate event, its
            # stage the tree's current node.
            events = self.doorway.store.all_events()
            state = self.doorway.state()
            tstate = _tree_state(
                events, state["dispatches"],
                ctx["instance_id"], ctx["cursor"],
                ctx["content"], ctx["iterations"])
            if tstate is None or \
                    tstate["current"] is None or \
                    tstate["current"]["kind"] in (
                        "compose", "deliver"):
                return False
            stage = tstate["current"]["id"]
        else:
            stage = _staged_stage(ctx["iterations"])
            if stage not in ("memory", "case", "files"):
                return False
        text = proposal["payload"].get("text")
        if not isinstance(text, str):
            return False
        digest = hashlib.sha256(
            text.encode("utf-8")).hexdigest()
        try:
            gate_ev = \
                self.doorway.record_delivery_stage_gate(
                    ctx["assembly_id"],
                    ctx.get("iteration_event_seq"), stage,
                    ev["event_seq"], digest)
        except Exception as exc:  # noqa: BLE001
            ctx["delivery_stage_gate_error"] = (
                f"the delivery stage gate could not be "
                f"recorded: {type(exc).__name__}: {exc}")
            return True
        ctx["recorded"].append(gate_ev)
        if cycle_form:
            if file_grain:
                ctx["delivery_stage_gate_correction"] = {
                    "what_arrived":
                        _cycle_stage_gate_what_arrived_v8(
                            stage),
                    "stage": stage,
                    "contribution_seq": ev["event_seq"],
                    "text_sha256": digest,
                    "missing_files": cycle_missing,
                    "instruction":
                        CYCLE_STAGE_GATE_INSTRUCTION_V8}
            else:
                ctx["delivery_stage_gate_correction"] = {
                    "what_arrived":
                        _cycle_stage_gate_what_arrived(
                            stage),
                    "stage": stage,
                    "contribution_seq": ev["event_seq"],
                    "text_sha256": digest,
                    "missing_blocks": cycle_missing,
                    "instruction":
                        CYCLE_STAGE_GATE_INSTRUCTION}
        elif tree_form:
            ctx["delivery_stage_gate_correction"] = {
                "what_arrived":
                    _tree_stage_gate_what_arrived(stage),
                "stage": stage,
                "contribution_seq": ev["event_seq"],
                "text_sha256": digest,
                "instruction":
                    TREE_STAGE_GATE_INSTRUCTION}
        else:
            ctx["delivery_stage_gate_correction"] = {
                "what_arrived": _stage_gate_what_arrived(
                    stage),
                "stage": stage,
                "contribution_seq": ev["event_seq"],
                "text_sha256": digest,
                "instruction": STAGED_STAGE_GATE_INSTRUCTION}
        return True

    def _try_delivery_evidence_gate(self, ctx, proposal,
                                    ev):
        """The delivery-evidence gate's decision (round
        ten, INDEX 552): True where this contribution is
        gated — the case declares the evidence a delivery
        must rest on, and at the contribution's own
        position in the record some of that evidence does
        not stand gathered in the worker's working set.
        The standing computation runs over the record at
        the contribution's event position, from the
        recorded dispatches and outcomes alone. The gate
        records its own event naming the contribution and
        the missing addresses, and stashes the correction
        for the next wake's package; nothing is filed and
        the loop does not complete. The firing consumes
        the iteration, as the other gates' do, and it may
        fire again on a later contribution while evidence
        stands missing. A gate that cannot be recorded
        names its error on the context and still returns
        True — an unrecorded gate must never silently
        become a filing — and the caller stalls on the
        error. Everywhere else (no declaration standing)
        the contribution is not the gate's business and
        adjudication proceeds exactly as it stands."""
        declaration = ctx.get("delivery_evidence")
        if declaration is None:
            return False
        text = proposal["payload"].get("text")
        if not isinstance(text, str):
            return False
        events = self.doorway.store.all_events()
        dispatches = self.doorway.state()["dispatches"]
        # Under the office-cycle contract the evidence
        # computation weighs the sealed block map
        # beside the standing rule: a file gathered
        # block by block, every block carried, stands
        # as evidence (the plan §7).
        block_map = None
        if ctx.get("presentation_contract") in (
                _tool_policy.PRESENTATION_CONTRACT_V4,
                _tool_policy.PRESENTATION_CONTRACT_V5,
                _tool_policy.PRESENTATION_CONTRACT_V6,
                _tool_policy.PRESENTATION_CONTRACT_V7,
                _tool_policy.PRESENTATION_CONTRACT_V8,
                _tool_policy.PRESENTATION_CONTRACT_V9,
                _tool_policy.PRESENTATION_CONTRACT_V10,
                _tool_policy.PRESENTATION_CONTRACT_V11,
                _tool_policy.PRESENTATION_CONTRACT_V12):
            generated = self.doorway._generated_payload(
                ctx["assembly_id"])
            block_map = _cycle_blocks(
                ctx["content"], generated)
        missing = _delivery_evidence_missing(
            events, dispatches, ctx["instance_id"],
            ev["event_seq"], declaration["addresses"],
            block_map=block_map)
        if not missing:
            return False
        digest = hashlib.sha256(
            text.encode("utf-8")).hexdigest()
        try:
            gate_ev = \
                self.doorway.record_delivery_evidence_gate(
                    ctx["assembly_id"],
                    ctx.get("iteration_event_seq"),
                    ev["event_seq"], digest, missing)
        except Exception as exc:  # noqa: BLE001
            ctx["delivery_evidence_gate_error"] = (
                f"the delivery evidence gate could not be "
                f"recorded: {type(exc).__name__}: {exc}")
            return True
        ctx["recorded"].append(gate_ev)
        ctx["delivery_evidence_gate_correction"] = \
            _evidence_gate_correction(
                ctx.get("catalogue") or [],
                ev["event_seq"], digest, missing)
        if block_map is not None:
            # The cycle contract's correction names the
            # incomplete cycles explicitly: the missing
            # files' blocks whose reads do not stand,
            # listed as blocks mapped to their files.
            ctx["delivery_evidence_gate_correction"][
                "missing_blocks"] = _missing_blocks(
                    events, dispatches, ctx["instance_id"],
                    ev["event_seq"], block_map, missing)
        return True

    def _try_delivery_length_gate(self, ctx, proposal,
                                  ev):
        """The delivery-length gate's decision (the
        third gate, INDEX 557): True where this
        contribution is gated — the case declares the
        length a delivery must reach, and the
        contribution's text, counted as the office
        counts it, falls short of the floor. The count
        is taken from the contribution's own text, the
        very text the record holds. The gate records
        its own event naming the contribution, the
        count it arrived with and the floor, and
        stashes the correction for the next wake's
        package; nothing is filed and the loop does not
        complete. The firing consumes the iteration, as
        the other gates' do, and it may fire again on a
        later contribution that still falls short. A
        gate that cannot be recorded names its error on
        the context and still returns True — an
        unrecorded gate must never silently become a
        filing — and the caller stalls on the error.
        Everywhere else (no declaration standing, or
        the floor met) the contribution is not the
        gate's business and adjudication proceeds
        exactly as it stands."""
        declaration = ctx.get("delivery_floor")
        if declaration is None:
            return False
        text = proposal["payload"].get("text")
        if not isinstance(text, str):
            return False
        word_count = len(text.split())
        min_words = declaration["min_words"]
        if word_count >= min_words:
            return False
        digest = hashlib.sha256(
            text.encode("utf-8")).hexdigest()
        try:
            gate_ev = \
                self.doorway.record_delivery_length_gate(
                    ctx["assembly_id"],
                    ctx.get("iteration_event_seq"),
                    ev["event_seq"], digest, word_count,
                    min_words)
        except Exception as exc:  # noqa: BLE001
            ctx["delivery_length_gate_error"] = (
                f"the delivery length gate could not be "
                f"recorded: {type(exc).__name__}: {exc}")
            return True
        ctx["recorded"].append(gate_ev)
        ctx["delivery_length_gate_correction"] = \
            _length_gate_correction(
                ev["event_seq"], digest, word_count,
                min_words)
        return True

    # ---------------------------------------------- adjudication
    def _adjudicate(self, ctx, data):
        """Effect a validated response, per act and per
        request: each record act goes through the doorway
        under the instance's credential (provenance stamped
        where the model did not supply it, as the driver
        stamps it); each tool request is presented under a
        loop-assigned identity and, on a standing dispatch,
        performed by the executor. A refusal of one act or
        request is collected and discards nothing independent
        of it.

        An act's doorway view position is the frozen package
        head — the view the model actually received, and the
        close of the cursor range the iteration event carries
        (Piece A3, correction round 1). Anything recorded
        after the freeze — including the iteration event
        itself, which is bookkeeping and not a subject change
        under R31 — does not move the act's basis: the record
        must not claim the act was made from a view the
        worker never saw. A genuine subject change after the
        freeze still refuses the act under R31, as it refuses
        any seat's."""
        doorway = self.doorway
        for proposal in data["proposals"]:
            proposal["payload"].setdefault(
                "case_id", ctx["case_id"])
            proposal["payload"].setdefault(
                "case_version", ctx["case_version"])
            try:
                ev = doorway.act(
                    self.token, proposal["type"],
                    proposal["payload"],
                    view_seq=ctx["cursor"])
                ctx["recorded"].append(ev)
                if proposal["type"] == "CONTRIBUTION" \
                        and ctx.get("delivery") is not None \
                        and ctx.get("deliverable_filed") \
                        is None \
                        and not ctx.get(
                            "delivery_filing_error"):
                    # The stage gate first (round nine's
                    # correction pair, INDEX 548): under
                    # the presentation contract, a
                    # contribution offered before the task
                    # stage is set aside unfiled and
                    # answered with a correction — it is
                    # not adjudicated as a delivery, and
                    # the response's remaining acts and
                    # requests proceed as they ordinarily
                    # would; the gate refuses the
                    # delivery, not the answer.
                    if self._try_delivery_stage_gate(
                            ctx, proposal, ev):
                        continue
                    # The evidence gate (round ten,
                    # INDEX 552): where the case declares
                    # the evidence a delivery must rest
                    # on, a contribution offered while
                    # that evidence does not stand
                    # gathered is set aside unfiled and
                    # answered with a correction naming
                    # what is missing — it is not
                    # adjudicated as a delivery. The
                    # stage gate keeps its own earlier
                    # watch: before the task stage this
                    # gate is never reached.
                    if self._try_delivery_evidence_gate(
                            ctx, proposal, ev):
                        continue
                    # The length gate (the third gate,
                    # INDEX 557): where the case declares
                    # the length a delivery must reach, a
                    # contribution arriving under that
                    # floor is set aside unfiled and
                    # answered with a correction naming
                    # the count it arrived with — it is
                    # not adjudicated as a delivery. It
                    # stands last in the family's order:
                    # the stage gate watches the stages
                    # before the task, the evidence gate
                    # watches the gathering, and a brief
                    # is not judged for sufficiency before
                    # its evidence stands.
                    if self._try_delivery_length_gate(
                            ctx, proposal, ev):
                        continue
                    # The door (door scope, 2026-11-24):
                    # under the sealed declaration this
                    # contribution is the deliverable's
                    # arrival; the office files it, and
                    # the response's remaining acts do not
                    # proceed — the first accepted
                    # contribution completes the assignment.
                    self._file_deliverable(ctx, proposal,
                                           ev)
                    return
            except DoorwayRefusal as refusal:
                ctx["refused"].append(
                    {"type": proposal["type"],
                     "ground": refusal.ground})
        for ordinal, request in enumerate(
                data["tool_requests"], start=1):
            # Request identity is the loop's: deterministic
            # in (activation, iteration, ordinal), so a
            # replay of the same presentation resolves against
            # its standing dispatch and never re-executes.
            request_id = (f"loop-{ctx['instance_id']}-"
                          f"{ctx['iterations']}-{ordinal}")
            remaining, _problem = doorway.activation_remaining(
                ctx["instance_id"])
            try:
                outcome = doorway.request_tool(
                    self.token, request["tool"],
                    request["parameters"], request_id,
                    budget_hint=remaining)
            except DoorwayRefusal as refusal:
                ctx["refused"].append(
                    {"type": "TOOL_REQUESTED",
                     "request_id": request_id,
                     "ground": refusal.ground})
                continue
            ctx["dispatched"].append(outcome)
            if self.executor is not None and \
                    not outcome.get("duplicate"):
                self.executor.execute(outcome["dispatch_id"])

    # --------------------------------------------------- timing
    def _note_call_timing(self, ctx, iteration, package_s,
                          call_started):
        """Collect one iteration's timing evidence (INDEX
        217/219): the package-construction seconds the loop
        measured itself, the callable invocation's total, and
        the stage timings the chain exposes — the adapter's
        prompt rendering (its last_render_s, where the
        callable is the adapter) and the transport's stages
        (the installed transport callable's last_call_timings,
        where it provides them). Anything the chain does not
        expose stands as None — unknown, not estimated — and
        where the transport stages are absent altogether the
        entry says so. Measured directly, here, never mined
        from the iteration event's timestamp."""
        transport = getattr(self.model, "_call", None)
        stages = getattr(transport, "last_call_timings", None) \
            if transport is not None else None
        entry = {
            "iteration": iteration,
            "package_construction_s": package_s,
            "render_s": getattr(self.model, "last_render_s",
                                None),
            "transport_stages": copy.deepcopy(stages)
            if isinstance(stages, dict) else None,
            "total_call_s": time.monotonic() - call_started,
        }
        if entry["transport_stages"] is None:
            entry["note"] = (
                "the callable provided no transport stage "
                "timings; the transport stages are unknown")
        ctx["call_timings"].append(entry)

    # ---------------------------------------------------- stall
    def _deadline_passed(self, ctx):
        remaining, problem = self.doorway.activation_remaining(
            ctx["instance_id"])
        if problem is not None:
            return False
        return remaining is not None and remaining <= 0

    def _close_accounting(self, ctx):
        """Close in-flight dispatch accounting for the
        activation: every dispatch of the instance standing
        without an outcome is performed by the executor where
        one is held and the dispatch is unclaimed; whatever
        still stands without an outcome afterwards is recorded
        uncertain by the executor route — occurrence not
        established, accounted rather than resolved. Returns
        True when accounting stands closed."""
        doorway = self.doorway
        state = doorway.state()
        for did, d in sorted(state["dispatches"].items()):
            if d.get("instance_id") != ctx["instance_id"]:
                continue
            if d.get("outcome") is not None or \
                    d.get("reconciled_seq") is not None:
                continue
            if self.executor is not None and \
                    not self.executor.claimed(did):
                self.executor.execute(did)
                state = doorway.state()
                d = state["dispatches"].get(did) or {}
                if d.get("outcome") is not None or \
                        d.get("reconciled_seq") is not None:
                    continue
            doorway.record_tool_outcome(
                did, "uncertain",
                detail="recorded at the loop's stall: the "
                       "dispatch stands without an outcome "
                       "and its occurrence is not established "
                       "(R50)")
        state = doorway.state()
        return all(
            d.get("outcome") is not None or
            d.get("reconciled_seq") is not None
            for d in state["dispatches"].values()
            if d.get("instance_id") == ctx["instance_id"])

    def _stall(self, ctx, ground, detail=None,
               terminal_step=None):
        """Record the stall — after dispatch accounting has
        closed. Where the record mechanism itself is
        unavailable, fail closed and say so: no stall is
        claimed that was not recorded. Under the response-
        evidence regime a pre-call stall names its
        terminal_step (R4-3), passed through to the
        doorway's route."""
        base = {"ok": False, "outcome": "stalled",
                "ground": ground,
                "instance_id": ctx["instance_id"],
                "assembly_id": ctx["assembly_id"],
                "iterations": ctx["iterations"],
                "recorded": ctx["recorded"],
                "refused": ctx["refused"],
                "dispatched": ctx["dispatched"],
                "call_timings": ctx["call_timings"]}
        if ctx.get("record_transaction_poisoned"):
            # The filing failure path could neither roll
            # its transaction back nor discard it: any
            # commit on this connection — dispatch
            # accounting's or the stall's own — could
            # land the discarded filing insert. Record
            # nothing; fail closed and say so (R50).
            base["stall_recorded"] = False
            base["reason"] = (
                "the stall was not recorded: the store "
                "transaction could not be rolled back or "
                "discarded after the failed filing, so "
                "recording on this connection could "
                "commit the discarded filing insert; no "
                "stall is claimed (R50)")
            return base
        try:
            if not self._close_accounting(ctx):
                base["stall_recorded"] = False
                base["reason"] = (
                    "dispatch accounting could not be closed; "
                    "no stall is claimed (R50)")
                return base
            ev = self.doorway.record_loop_stalled(
                ctx["assembly_id"], ground, detail=detail,
                terminal_step=terminal_step)
        except Exception as exc:  # noqa: BLE001 — the record
            # mechanism itself unavailable: fail closed, claim
            # nothing
            base["stall_recorded"] = False
            base["reason"] = (
                f"the stall could not be recorded "
                f"({type(exc).__name__}: {exc}); no stall is "
                f"claimed (R50)")
            return base
        base["stall_recorded"] = True
        base["stall_event"] = ev
        return base
