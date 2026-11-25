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
        try:
            return self._run(ctx)
        finally:
            # The loop's context is local to the run and is
            # dropped at return; nothing here outlives the
            # call (evidenced disposal is Piece A5's).
            ctx.clear()

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
        if doorway._probe_governed(
                doorway._generated_payload(assembly_id)):
            packed = doorway._event_at(entry.get("packed_seq"))
            adapter_mode = (packed or {}).get(
                "payload", {}).get("adapter_mode")
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
        return {
            "delivery": copy.deepcopy(_delivery),
            "working_set_declared":
                _generated.get("working_set_contract")
                == _tool_policy.WORKING_SET_CONTRACT,
            "deliverable_filed": None,
            "delivery_gate_correction": None,
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
                        "working_set_hash"))
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
        if ws_applies:
            # Working-set carriage: this delta's retrieval
            # results are presented in the working set (the
            # accumulated set built below), so their
            # tool_results entries stand by the same
            # provenance stub the delta's copy carries,
            # pointing at the working set — the content
            # appears exactly once in the package.
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
            package = ordered
        return package, head

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
        rather than silent."""
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
            # the detail, not hidden.
            rollback_problem = None
            try:
                self.doorway.store.rollback()
            except Exception as rb_exc:  # noqa: BLE001
                rollback_problem = (
                    f"{type(rb_exc).__name__}: {rb_exc}")
            problem = self._restore_filing_destination(
                path, staging, prior)
            detail = (
                f"the deliverable could not be filed: "
                f"{type(exc).__name__}: {exc}")
            if rollback_problem is not None:
                detail += (
                    "; the store transaction could not "
                    f"be rolled back ({rollback_problem})")
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
