"""Probe P2: the multi-call response shape
(NATIVE-ADAPTER-P2-PROBE-PROPOSAL-2026-11-24 Rev 1,
PASSED at INDEX 358).

The question: does the pinned model, on this route,
emit more than one native tool call in a single
response when the task's natural opening is two
independent calls — and if it does, in what envelope:
multiple tool_calls entries, each carrying its own
provider call ID, name and arguments, in a definite
emitted order? Across both native-offer runs every
delivered response carried exactly one call, under a
construction whose natural opening was one call.
Whether the model ever sends two at once, under a
construction that invites exactly that, is unobserved
— and the adapter scope's §4 semantics (preflight
classification of the whole list, partial success,
dual ordinals, result ordering) are only as real as
the response shape they govern.

The construction is a disclosed variant of the
standing first-worker material, derived from the
evidenced iteration-1 worker request by the
native-offer probe's reproducible-baseline path:

- the variant assignment requires the brief to rest
  on two named sources — sources/stock-take.md and
  sources/a3-pass.md — both in full, neither's
  inspection dependent on the other's result, so the
  opening is exactly two calls wide;
- the assignment pre-presents the sources listing
  (the source names with their sizes, read from the
  evidenced run's own sandbox files), so the listing
  step is already done and each source's natural
  opening is a read;
- the FULL granted catalogue is offered natively —
  all three retrieval definitions, derived from the
  sealed catalogue by the same derivation as both
  prior probes. Nothing is withheld: P2 varies the
  task construction, not the offer's width.
  disable_tool_validation stands at the provider
  default — it is P1's variable, not this probe's.

The comparison artifact enumerates every differing
path against the admitted native-offer modified
request; the differing paths must be exactly the
task-context path (the user message content, via the
package's case assignment), with the offered tools
canonically unchanged — a diff entry anywhere else
fails the precondition and stops the probe before
any trial runs. Five trials, first response only,
paced at the settled 65-second monotonic floor,
every call's provider call ID, name, arguments and
emitted order preserved per call: the envelope is
the evidence.

Classification notes, within the proposal's text:
the behaviour dimension classifies by call count
and content. A response the provider refused
delivered no response to count, so a refused trial's
behaviour is no_observable_behaviour with the
refusal standing on the delivery axis and any
attributable attempt preserved in the per-call
records and the retained body — the proposal's own
reading table counts refusals among the no-call
trials. The single-call reading is confined to the
first response, as the proposal's correction note
requires: five single-call first responses establish
that the first response contained one call in each
trial, and nothing about what a subsequent response
would propose.
"""

from __future__ import annotations

import copy
import os

from fabric.canonical import canonical, sha256_hex

from . import native_probe as _np
from . import native_probe_paced as _paced
from . import probe as _probe
from .adapter import _render_prompt

__all__ = [
    "OFFERED_TOOLS", "SOURCE_PATHS", "REQUIRED_SOURCES",
    "TRIAL_COUNT", "NativeProbeRefusal",
    "sources_listing", "listing_text",
    "variant_assignment", "build_variant_request",
    "build_comparison", "check_precondition", "prepare",
    "classify_p2_capture", "trial_evidence",
    "summarise_p2", "run_p2_trials",
    "probe_evidence_object", "p2_evidence_hash",
]

NativeProbeRefusal = _np.NativeProbeRefusal

OFFERED_TOOLS = _np.OFFERED_TOOLS

SOURCE_PATHS = ("sources/stock-take.md",
                "sources/a3-pass.md",
                "sources/index-tail.md")
REQUIRED_SOURCES = ("sources/stock-take.md",
                    "sources/a3-pass.md")

TRIAL_COUNT = 5

BEHAVIOURS = (
    "multi_call",
    "single_call",
    "text_contract",
    "mixed",
    "malformed",
    "no_observable_behaviour",
)

# The differing paths the construction admits, stated
# in advance: against the native-offer modified
# request, exactly the task-context path — the tools
# set is the full catalogue and must show as
# unchanged.
TASK_CONTEXT_PATH = "messages[1].content"
VS_NATIVE_PATHS = (TASK_CONTEXT_PATH,)


# ----------------------------------------------------------------
# The construction: listing, variant assignment,
# variant request — the same mechanics as P1's (the
# two probes' constructions differ in their assignment
# texts, not in how a variant is built and verified).
# ----------------------------------------------------------------

def sources_listing(source_run_dir):
    """The pre-presented listing's facts: the sources'
    names with their sizes, read from the evidenced
    run's own sandbox files. Refuses where a named
    source is absent."""
    entries = []
    for rel in SOURCE_PATHS:
        path = os.path.join(source_run_dir, "sandbox",
                            rel)
        if not os.path.isfile(path):
            raise NativeProbeRefusal(
                f"the source run holds no {rel} under "
                f"its sandbox; the pre-presented listing "
                f"cannot be constructed from it")
        entries.append({"path": rel,
                        "size_bytes": os.path.getsize(path)})
    return entries


def listing_text(listing):
    """The listing as the assignment presents it: each
    source's path and size, in the executor's own list
    rendering's terms (path — N bytes)."""
    return "; ".join(
        f"{entry['path']} — {entry['size_bytes']} bytes"
        for entry in listing)


def variant_assignment(listing):
    """The P2 variant assignment text: the standing
    assignment's brief, with the sources listing
    pre-presented and the brief required to rest on
    the two named sources, each read in full. The
    text names the two required sources and their
    full-contents requirement; it does not instruct
    the model to call anything in particular, in
    parallel or otherwise. Deterministic in the
    listing."""
    return (
        "The sources in your sandbox are already "
        "listed for you, so there is no need to list "
        f"them again: {listing_text(listing)}. Write "
        "scratch/brief.md: a plain-words brief, at "
        "most ~600 words, that a newcomer could read "
        "to learn what this framework is, what has "
        "actually been proven, what has not been "
        "proven, and what remains to be built. The "
        "brief must rest on two sources, each read "
        f"in full: {REQUIRED_SOURCES[0]} and "
        f"{REQUIRED_SOURCES[1]}. Stay accurate to "
        "the sources; invent nothing; where the "
        "sources disagree with each other, say so.")


def build_variant_request(baseline, package, assignment):
    """The variant request: the baseline object with
    its task context replaced by the variant — the
    package's case assignment swapped for the variant
    text and the prompt re-rendered by the adapter's
    own rendering. Derived from the baseline object
    itself, never rebuilt, and verified: the ONLY
    differing path against the baseline must be the
    task-context path, or the construction refuses."""
    variant_package = copy.deepcopy(package)
    case = variant_package.get("case")
    if not isinstance(case, dict) or \
            "assignment" not in case:
        raise NativeProbeRefusal(
            "the regenerated package carries no case "
            "assignment to vary; the construction has "
            "no standing")
    case["assignment"] = assignment
    prompt = _render_prompt(variant_package)
    request = copy.deepcopy(baseline)
    messages = request.get("messages")
    if not isinstance(messages, list) or len(messages) < 2 \
            or not isinstance(messages[1], dict) \
            or messages[1].get("role") != "user":
        raise NativeProbeRefusal(
            "the baseline request's second message is "
            "not the user message the construction "
            "expects")
    request["messages"][1]["content"] = prompt
    diff = _np.diff_requests(baseline, request)
    if [e["path"] for e in diff] != [TASK_CONTEXT_PATH]:
        raise NativeProbeRefusal(
            "the variant request differs from the "
            f"baseline at {[e['path'] for e in diff]}, "
            f"not exactly the task-context path "
            f"{TASK_CONTEXT_PATH}; the construction "
            f"is not the disclosed one")
    return request


# ----------------------------------------------------------------
# The comparison artifact and its precondition.
# ----------------------------------------------------------------

def build_comparison(baseline, native_modified, request,
                     definitions, catalogue_source,
                     baseline_info, assignment, listing,
                     original_assignment):
    """The comparison artifact (the proposal's
    auditable construction): the request identified by
    canonical hash beside the baseline's and the
    admitted native-offer modified request's; the full
    field-by-field diff against the native-offer
    request, whose differing paths must be exactly the
    declared task-context path with the tools set
    unchanged; the definitions and their catalogue
    source; and the construction record (the original
    and variant assignment texts' hashes, the variant
    text itself, the listing's facts)."""
    diff = _np.diff_requests(native_modified, request)
    return {
        "kind": "native adapter probe P2 request "
                "comparison (NATIVE-ADAPTER-P2-PROBE-"
                "PROPOSAL Rev 1)",
        "baseline_sha256": sha256_hex(canonical(baseline)),
        "native_offer_modified_sha256": sha256_hex(
            canonical(native_modified)),
        "request_sha256": sha256_hex(canonical(request)),
        "definitions_sha256": sha256_hex(
            canonical(definitions)),
        "catalogue_source": catalogue_source,
        "baseline_construction": baseline_info,
        "construction": {
            "original_assignment_sha256": sha256_hex(
                canonical(original_assignment)),
            "variant_assignment": assignment,
            "variant_assignment_sha256": sha256_hex(
                canonical(assignment)),
            "pre_presented_listing": listing,
            "required_sources": list(REQUIRED_SOURCES),
            "designed_differences": [
                "the task context: the brief required "
                "to rest on two named sources, each in "
                "full (sources/stock-take.md and "
                "sources/a3-pass.md), and the sources "
                "listing pre-presented (the request's "
                "user message content, via the "
                "package's case assignment)",
            ],
        },
        "tool_choice": {
            "request": (
                "absent — no tool_choice field stands "
                "in the request; the provider's natural "
                "(automatic) tool choice, as in both "
                "native-offer runs"),
        },
        "disable_tool_validation": (
            "absent — the provider default stands; the "
            "flag is P1's variable and is not varied "
            "in this probe"),
        "vs_native_offer": {
            "differing_paths": [e["path"] for e in diff],
            "diff": diff,
        },
    }


def _expected_prompt(package, assignment):
    variant_package = copy.deepcopy(package)
    variant_package["case"]["assignment"] = assignment
    return _render_prompt(variant_package)


def check_precondition(baseline, native_modified, request,
                       comparison, package, catalogue_hash):
    """The release precondition, checked — never
    asserted (the INDEX 336/337 standard): every
    recorded hash recomputes from the actual objects;
    the recorded diff against the admitted native-offer
    request equals the recomputed diff in full, entries
    and both sides' hashes, at exactly the declared
    task-context path; the request's actual tools field
    is canonically identical to the native-offer
    request's tools (the full catalogue, unchanged)
    and hashes to the recorded definitions hash, which
    itself recomputes from a fresh derivation over the
    package; the catalogue source hash agrees with the
    baseline construction's commitment; the request
    carries neither tool_choice nor the validation
    flag; and the request's user message is exactly
    the rendering of the package carrying the recorded
    variant assignment — a tampered assignment, in the
    request or in the artifact, fails here. Returns
    the list of problems; empty is a pass."""
    problems = []

    def expect_hash(label, recorded, obj):
        if recorded != sha256_hex(canonical(obj)):
            problems.append(
                f"the comparison's recorded {label} hash "
                f"does not recompute from the actual "
                f"object")

    expect_hash("baseline", comparison.get(
        "baseline_sha256"), baseline)
    expect_hash("native-offer modified", comparison.get(
        "native_offer_modified_sha256"), native_modified)
    expect_hash("request", comparison.get(
        "request_sha256"), request)
    try:
        definitions, _ = _np.derive_offered_definitions(
            package, catalogue_hash)
    except NativeProbeRefusal as refusal:
        problems.append(
            f"the catalogue derivation refuses: {refusal}")
        definitions = None
    if definitions is not None:
        expect_hash("definitions", comparison.get(
            "definitions_sha256"), definitions)
    # The diff against the admitted native-offer
    # request: exactly the task-context path, in full.
    diff = _np.diff_requests(native_modified, request)
    if [e["path"] for e in diff] != list(VS_NATIVE_PATHS):
        problems.append(
            "the request differs from the admitted "
            f"native-offer request at "
            f"{[e['path'] for e in diff]}, not exactly "
            f"the declared task-context path "
            f"{list(VS_NATIVE_PATHS)}")
    vs = comparison.get("vs_native_offer")
    if not isinstance(vs, dict):
        vs = {}
    if vs.get("diff") != diff:
        problems.append(
            "the comparison's recorded vs-native-offer "
            "diff entries do not equal the recomputed "
            "diff in full")
    if vs.get("differing_paths") != \
            [e["path"] for e in diff]:
        problems.append(
            "the comparison's recorded vs-native-offer "
            "differing paths are not the recomputed "
            "diff's paths")
    # The tools field: byte-unchanged from the
    # native-offer construction (canonical equality),
    # and the recorded definitions hash is the hash of
    # the request's actual tools.
    if canonical(request.get("tools")) != \
            canonical(native_modified.get("tools")):
        problems.append(
            "the request's tools field differs from "
            "the admitted native-offer request's; this "
            "probe offers the full catalogue unchanged")
    if comparison.get("definitions_sha256") != \
            sha256_hex(canonical(request.get("tools"))):
        problems.append(
            "the comparison's recorded definitions "
            "hash does not equal the canonical hash of "
            "the request's actual tools field")
    if "tool_choice" in request:
        problems.append(
            "the request carries a tool_choice field; "
            "this probe sends none")
    if "disable_tool_validation" in request:
        problems.append(
            "the request carries the validation flag; "
            "the flag is P1's variable and stands at "
            "the provider default in this probe")
    # The catalogue source agrees with the baseline
    # construction's commitment.
    catalogue_source = comparison.get("catalogue_source")
    if not isinstance(catalogue_source, dict):
        catalogue_source = {}
    construction = comparison.get("baseline_construction")
    if not isinstance(construction, dict):
        construction = {}
    if not catalogue_source.get("catalogue_hash") or \
            catalogue_source.get("catalogue_hash") != \
            construction.get("catalogue_hash"):
        problems.append(
            "the comparison's recorded catalogue source "
            "hash does not agree with the baseline "
            "construction's catalogue commitment")
    # The task context: the request's user message is
    # exactly the recorded variant assignment's
    # rendering over this package.
    recorded_construction = comparison.get("construction")
    if not isinstance(recorded_construction, dict):
        recorded_construction = {}
    assignment = recorded_construction.get(
        "variant_assignment")
    if not isinstance(assignment, str) or \
            recorded_construction.get(
                "variant_assignment_sha256") != \
            sha256_hex(canonical(assignment)):
        problems.append(
            "the comparison's recorded variant "
            "assignment does not stand under its "
            "recorded hash")
    else:
        expected = _expected_prompt(package, assignment)
        messages = request.get("messages")
        content = None
        if isinstance(messages, list) \
                and len(messages) >= 2 \
                and isinstance(messages[1], dict):
            content = messages[1].get("content")
        if content != expected:
            problems.append(
                "the request's user message is not the "
                "rendering of the recorded variant "
                "assignment over this package")
    return problems


def prepare(source_run_dir, work_dir, model):
    """The whole construction, in one step (the driver
    and the suite both build through here): regenerate
    the baseline by the real construction path, derive
    the full definitions, build the variant request
    and the native-offer modified request, and the
    comparison artifact. Returns the prepared pieces
    as a dict. No provider request is made anywhere in
    this step."""
    baseline, package, info = _np.build_baseline(
        source_run_dir, work_dir, model)
    definitions, catalogue_source = \
        _np.derive_offered_definitions(
            package, info["catalogue_hash"])
    listing = sources_listing(source_run_dir)
    assignment = variant_assignment(listing)
    original_assignment = package["case"]["assignment"]
    variant = build_variant_request(
        baseline, package, assignment)
    native_modified = _np.build_modified_request(
        baseline, definitions)
    request = _np.build_modified_request(
        variant, definitions)
    comparison = build_comparison(
        baseline, native_modified, request, definitions,
        catalogue_source, info, assignment, listing,
        original_assignment)
    return {
        "baseline": baseline,
        "package": package,
        "info": info,
        "definitions": definitions,
        "catalogue_source": catalogue_source,
        "listing": listing,
        "assignment": assignment,
        "variant_request": variant,
        "native_modified": native_modified,
        "request": request,
        "comparison": comparison,
    }


# ----------------------------------------------------------------
# Classification: by call count and content, behaviour
# × delivery on separate axes.
# ----------------------------------------------------------------

def _classify_call(name, parsed):
    """One call's classification against the full
    offered set: a readable name outside it is an
    unoffered attempt whatever its arguments (under a
    full offer it is preserved and named, per the
    proposal); an offered call whose arguments do not
    parse to a JSON object is malformed; an unreadable
    call is malformed."""
    if not isinstance(name, str) or not name:
        return "malformed"
    if name not in OFFERED_TOOLS:
        return "unoffered_tool_attempt"
    if parsed is _probe._UNPARSEABLE or \
            not isinstance(parsed, dict):
        return "malformed"
    return "offered_tool_call"


def _addressed_source(call):
    """The required source a call addresses, where its
    parsed arguments name one as the path; else None."""
    arguments = call.get("arguments")
    if isinstance(arguments, dict):
        path = arguments.get("path")
        if path in REQUIRED_SOURCES:
            return path
    return None


def _multi_shape(records):
    """A multi-call response's shape, reported not
    flattened into the count: a mixture including an
    unoffered name; the two independent openings the
    construction invites (exactly two calls, each
    required source addressed); or some other shape
    (a duplicate, two calls on one source, extra
    calls)."""
    if any(r["classification"] == "unoffered_tool_attempt"
           for r in records):
        return "mixture_including_unoffered"
    addressed = {s for s in
                 (_addressed_source(r) for r in records)
                 if s is not None}
    if len(records) == 2 and \
            addressed == set(REQUIRED_SOURCES):
        return "two_independent_openings"
    return "other_shape"


def classify_p2_capture(capture):
    """The classification of one raw capture: the
    behaviour (by call count and content), the
    delivery on its own axis, the per-call records —
    every call with its provider call ID, name,
    arguments and emitted ordinal — the text channel's
    form, and the shape facts the readings read: the
    call count, a multi-call response's shape, the
    required sources the calls address, and, for a
    single call, the required source it addresses."""
    delivery = _paced.delivery_of(capture)
    body = capture.get("body")
    if isinstance(body, str):
        message = _paced.message_from_body(body)
        if message is None:
            return _classification(
                "malformed", "provider_accepted", [],
                "none")
        records = _paced.call_records_from_message(
            message, _classify_call)
        text_form = _paced.text_form_of(message)
        if records is None:
            behaviour = {
                "text_contract": "text_contract",
                "other": "malformed",
                "none": "no_observable_behaviour",
            }[text_form]
            return _classification(
                behaviour, "provider_accepted", [],
                text_form)
        if text_form != "none":
            return _classification(
                "mixed", "provider_accepted", records,
                text_form)
        if len(records) >= 2:
            if all(r["classification"] == "malformed"
                   for r in records):
                return _classification(
                    "malformed", "provider_accepted",
                    records, text_form)
            return _classification(
                "multi_call", "provider_accepted",
                records, text_form)
        only = records[0]
        if only["classification"] == "malformed":
            return _classification(
                "malformed", "provider_accepted",
                records, text_form)
        return _classification(
            "single_call", "provider_accepted", records,
            text_form)
    # No response was delivered: the refusal or failure
    # stands on the delivery axis; any attributable
    # attempt is preserved in the per-call records.
    records = []
    error_body = capture.get("error_body")
    if isinstance(error_body, str):
        attributed = _paced.call_records_from_error_body(
            error_body, _classify_call)
        if attributed is not None:
            records = attributed
    return _classification(
        "no_observable_behaviour", delivery, records,
        "none")


def _classification(behaviour, delivery, records,
                    text_form):
    return {
        "behaviour": behaviour,
        "delivery": delivery,
        "calls": records,
        "text_form": text_form,
        "call_count": len(records),
        "shape": _multi_shape(records)
        if behaviour == "multi_call" else None,
        "sources_addressed": sorted({
            s for s in
            (_addressed_source(r) for r in records)
            if s is not None}),
        "addresses_required_source":
            _addressed_source(records[0])
            if behaviour == "single_call" and records
            else None,
        "has_offered_call": any(
            r["classification"] == "offered_tool_call"
            for r in records),
        "has_unoffered_call": any(
            r["classification"] == "unoffered_tool_attempt"
            for r in records),
        "has_malformed_call": any(
            r["classification"] == "malformed"
            for r in records),
    }


# ----------------------------------------------------------------
# Trial evidence and the run.
# ----------------------------------------------------------------

def trial_evidence(index, capture,
                   request_started_wall_at=None,
                   request_start_monotonic_offset_seconds=None,
                   pacing_wait_phase_seconds=0.0):
    """One trial's recorded evidence: the
    classification (aggregate and per call — every
    call's provider call ID, name, arguments and
    emitted order preserved: the envelope is the
    evidence), the shape facts, the settled flag, the
    pacing record (the wall start for chronology, the
    monotonic start offset and the wait-phase
    seconds), and the retained provider body and
    diagnostics under the capture ceiling, each with
    its hash."""
    result = classify_p2_capture(capture)
    evidence = {
        "trial": index,
        "request_started_wall_at": request_started_wall_at,
        "request_start_monotonic_offset_seconds":
            request_start_monotonic_offset_seconds,
        "pacing_wait_phase_seconds":
            pacing_wait_phase_seconds,
        "behaviour": result["behaviour"],
        "delivery": result["delivery"],
        "calls": result["calls"],
        "text_form": result["text_form"],
        "call_count": result["call_count"],
        "shape": result["shape"],
        "sources_addressed": result["sources_addressed"],
        "addresses_required_source":
            result["addresses_required_source"],
        "has_offered_call": result["has_offered_call"],
        "has_unoffered_call": result["has_unoffered_call"],
        "has_malformed_call": result["has_malformed_call"],
    }
    evidence.update(_paced.retain_capture(capture))
    return evidence


def summarise_p2(trials):
    """(counts, settled_count, reading): the counts
    over both dimensions exactly as recorded, and the
    reading the proposal predeclared, read over the
    settled, delivered trials (delivery failures
    excluded from the denominator): three or more
    multi_call trials live-evidence multi-call
    emission; every delivered trial single_call is
    the first-response observation, stated at that
    width; a majority of delivered trials with no
    calls at all (text, no observable behaviour, or
    refusals) is a construction finding —
    inconclusive for the multi-call question; anything
    else is a split, reported as exactly that. Five
    observations establish what happened in five
    controlled trials."""
    counts = {
        "behaviour": {name: 0 for name in BEHAVIOURS},
        "delivery": {name: 0 for name in _paced.DELIVERIES},
    }
    for trial in trials:
        if trial.get("behaviour") in counts["behaviour"]:
            counts["behaviour"][trial["behaviour"]] += 1
        if trial.get("delivery") in counts["delivery"]:
            counts["delivery"][trial["delivery"]] += 1
    settled = sum(1 for trial in trials
                  if trial.get("settled"))
    delivered = [t for t in trials
                 if t.get("settled")
                 and t.get("delivery") != "provider_failed"]
    multi = sum(1 for t in delivered
                if t["behaviour"] == "multi_call")
    single = sum(1 for t in delivered
                 if t["behaviour"] == "single_call")
    no_calls = sum(
        1 for t in delivered
        if t["delivery"] == "provider_refused"
        or t["behaviour"] in ("text_contract",
                              "no_observable_behaviour"))
    if not delivered:
        reading = "no_delivered_trials"
    elif multi >= 3:
        reading = "multi_call_live_evidenced"
    elif no_calls > len(delivered) / 2:
        reading = "construction_inconclusive"
    elif single == len(delivered):
        reading = "single_call_first_response_only"
    else:
        reading = "split_reported"
    return counts, settled, reading


def run_p2_trials(raw_call, prepared, clock=None,
                  sleeper=None, monotonic_clock=None,
                  wall_clock=None):
    """The bounded trial run: the precondition verified
    first — a failure refuses before any provider
    request and before any pacing wait — then exactly
    TRIAL_COUNT trials over the shared paced runner,
    each ONE generation request through the injected
    raw-call callable, each ending at its first
    response. No follow-up request, no dispatch, no
    execution, no tool-result response, ever."""
    problems = check_precondition(
        prepared["baseline"], prepared["native_modified"],
        prepared["request"], prepared["comparison"],
        prepared["package"],
        prepared["info"]["catalogue_hash"])
    plan = [prepared["request"]] * TRIAL_COUNT

    def make_evidence(index, capture, **pacing):
        return trial_evidence(index, capture, **pacing)

    return _paced.run_paced_trials(
        raw_call, plan, problems, make_evidence,
        clock=clock, sleeper=sleeper,
        monotonic_clock=monotonic_clock,
        wall_clock=wall_clock)


# ----------------------------------------------------------------
# The evidence artifact.
# ----------------------------------------------------------------

_TRIAL_HASH_FIELDS = (
    "trial", "request_started_wall_at",
    "request_start_monotonic_offset_seconds",
    "pacing_wait_phase_seconds",
    "behaviour", "delivery", "text_form", "call_count",
    "shape", "addresses_required_source",
    "has_offered_call", "has_unoffered_call",
    "has_malformed_call", "settled", "http_status",
    "provider_body_sha256", "provider_body_bytes",
    "provider_body_complete", "metadata_sha256",
    "diagnostics_sha256", "diagnostics_bytes",
    "diagnostics_complete", "aggregate_bytes",
    "evidence_complete",
)


def _evidence_projection(evidence):
    """The evidence-bearing projection the evidence
    hash binds: the comparison's hashes, the per-trial
    classifications — aggregate AND per call, each
    call's provider call ID, name, emitted ordinal,
    classification and arguments hash — the counts and
    the reading, so the reading is reconstructable
    from the hash-bound projection alone."""
    trials = []
    for trial in evidence.get("trials") or []:
        entry = {key: trial.get(key)
                 for key in _TRIAL_HASH_FIELDS}
        entry["sources_addressed"] = trial.get(
            "sources_addressed")
        entry["calls"] = [{
            "name": call.get("name"),
            "id": call.get("id"),
            "ordinal": call.get("ordinal"),
            "classification": call.get("classification"),
            "arguments_sha256": sha256_hex(canonical(
                call.get("arguments")))
            if call.get("arguments") is not None else None,
            "arguments_parseable":
                call.get("arguments_parseable"),
        } for call in trial.get("calls") or []]
        trials.append(entry)
    return {
        "baseline_sha256": evidence.get("baseline_sha256"),
        "native_offer_modified_sha256": evidence.get(
            "native_offer_modified_sha256"),
        "definitions_sha256": evidence.get(
            "definitions_sha256"),
        "comparison_sha256": evidence.get(
            "comparison_sha256"),
        "trials": trials,
        "counts": evidence.get("counts"),
        "settled_count": evidence.get("settled_count"),
        "reading": evidence.get("reading"),
    }


def p2_evidence_hash(evidence):
    """The hash over the evidence artifact's own
    projection — the binding that ties any later
    judgement of this probe to this exact evidence."""
    return sha256_hex(canonical(
        _evidence_projection(evidence)))


def probe_evidence_object(comparison, trials):
    """The probe's evidence artifact: the comparison
    referenced by its hash (the artifact itself stands
    as its own durable file), the per-trial evidence,
    the counts, and the reading the predeclared
    thresholds produce — with the evidence hash
    computed over the artifact's projection."""
    counts, settled, reading = summarise_p2(trials)
    evidence = {
        "kind": "native adapter probe P2 evidence "
                "(NATIVE-ADAPTER-P2-PROBE-PROPOSAL "
                "Rev 1)",
        "comparison_sha256": sha256_hex(
            canonical(comparison)),
        "baseline_sha256": comparison["baseline_sha256"],
        "native_offer_modified_sha256": comparison[
            "native_offer_modified_sha256"],
        "definitions_sha256":
            comparison["definitions_sha256"],
        "trial_count": len(trials),
        "trials": trials,
        "counts": counts,
        "settled_count": settled,
        "reading": reading,
    }
    evidence["evidence_hash"] = p2_evidence_hash(evidence)
    return evidence
