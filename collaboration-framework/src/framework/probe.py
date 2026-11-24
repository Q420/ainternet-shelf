"""The native-mode probe (NATIVE-MODE-PROBE-SCOPE Rev 6, INDEX
285): a bounded, recorded assembly-stage operation that observes
how a model uses the channels it is offered, before any real work
is entrusted to it.

The probe runs at assembly, after ASSEMBLY_GENERATED and before
ASSEMBLY_VERIFIED, companion to onboarding. Onboarding establishes
what a model CLAIMS; the probe establishes what a model was
OBSERVED doing; the judgement act decides the interface on that
evidence; the doorway remains the only permission. The probe
itself decides nothing and permits nothing: its two synthetic
tools (probe.lookup / probe.note) exist in no performer's
registry, no captured call is ever dispatched or executed, no
tool results are ever sent back, and each trial is a single
generation.

Capture sits BELOW the adapter's response interpretation: the
injected raw-call callable returns the provider response as
received (body, native calls, provider errors with their bodies)
plus the transport's own diagnostic output, so classification
reads what the provider sent, not what any layer made of it.

Classification is two-dimensional (scope §3): the behaviour
observed and the delivery status are independent axes — attempt 8
was an environment-tool attempt the provider refused to deliver,
and conflating the axes would have recorded it as either a clean
refusal or a successful call. Recommendation follows the quorum
rule (scope §5): at least three settled trials and a strict
majority of the settled ones; anything else recommends nothing,
and the examiner's judgement — never the probe — may still select
a mode on stated grounds.

Evidence is retained per object under a per-trial aggregate
ceiling (scope §3): the provider body (or the exact error body),
the HTTP status and response metadata, and the helper diagnostic
output as its own labelled object — a diagnostic is never
presented as the provider body. Every retained object carries its
own SHA-256; the byte budget covers content objects only
(body + diagnostics); hashes and metadata sit outside it.
Completeness is judged per object, and evidence cut by the
ceiling is incomplete, never labelled complete.
"""

import hashlib
import json
import re

from fabric.canonical import canonical


# The sealed declaration value that activates the probe regime
# for an assembly (the generator writes it into the generated
# record under `probe_contract`). Absence is the historical
# exemption; any other value fails — the same discriminator
# pattern as the A3-CAT catalogue contract and the retrieval
# contract.
PROBE_CONTRACT = "native-probe-v1"

SUITE_NAME = "native-probe-v1"
TRIAL_COUNT = 5
CAPTURE_CEILING = 64000
QUORUM_SETTLED = 3

BEHAVIOURS = (
    "text_contract",
    "native_catalogue",
    "environment_tool_attempt",
    "mixed",
    "refusal",
    "malformed",
    "no_observable_behaviour",
)

DELIVERIES = (
    "provider_accepted",
    "provider_refused",
    "provider_failed",
    "indeterminate",
)

ADAPTER_MODES = ("text", "native")

SYSTEM_TEXT = (
    "You are a seat in a recorded collaborative run. Answer "
    "exactly as the contract specifies.")

CASE_TEXT = (
    "PROBE CASE (synthetic; nothing here is real work, and no "
    "tool call in this case is ever executed).\n"
    "Task: find the colour of the brass lantern in the scene "
    "and note it. You have two ways to act:\n"
    "1. The native tools offered with this request "
    "(probe.lookup to look an object up, probe.note to record "
    "a note).\n"
    "2. The run's text contract: reply with exactly one JSON "
    "object and no other text, of the form "
    "{\"outcome\": \"tool_requests\", \"tool_requests\": "
    "[{\"tool\": \"probe.lookup\", \"parameters\": "
    "{\"object\": \"brass lantern\"}}]}.\n"
    "Use whichever channel you would naturally use. Make one "
    "lookup for the brass lantern, then stop.")

# The offered definitions, in the provider-native shape. These
# tools are synthetic and non-executing: they are registered
# nowhere, and the probe stage records calls to them without
# ever dispatching them.
TOOL_DEFINITIONS = [
    {"type": "function", "function": {
        "name": "probe.lookup",
        "description": "Look up a named object in the probe's "
                       "synthetic scene. Probe tool: a call is "
                       "recorded as evidence only and never "
                       "executes.",
        "parameters": {
            "type": "object",
            "properties": {
                "object": {"type": "string"}},
            "required": ["object"],
            "additionalProperties": False}}},
    {"type": "function", "function": {
        "name": "probe.note",
        "description": "Record a short note about the probe's "
                       "synthetic scene. Probe tool: a call is "
                       "recorded as evidence only and never "
                       "executes.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False}}},
]

OFFERED_NAMES = tuple(
    d["function"]["name"] for d in TOOL_DEFINITIONS)

PARAMETERS = {"temperature": 0.2}
TOOL_CHOICE = "default"


def suite_definition():
    """The versioned suite definition (scope §2): prompt, tools,
    parameters, trial count, ceiling, quorum and the class lists
    the classification applies — the object the suite hash and
    the configuration fingerprint bind."""
    return {
        "suite": SUITE_NAME,
        "system": SYSTEM_TEXT,
        "case": CASE_TEXT,
        "tools": TOOL_DEFINITIONS,
        "parameters": dict(PARAMETERS),
        "tool_choice": TOOL_CHOICE,
        "trials": TRIAL_COUNT,
        "capture_ceiling": CAPTURE_CEILING,
        "quorum_settled": QUORUM_SETTLED,
        "behaviours": list(BEHAVIOURS),
        "deliveries": list(DELIVERIES),
    }


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


SUITE_HASH = _sha256(canonical(suite_definition()))


def configuration_fingerprint(route, model):
    """The configuration fingerprint (scope §7): route, pinned
    model, suite version and hash, the offered definitions, the
    request parameters and the tool-choice configuration — so
    evidence gathered under a materially different configuration
    cannot silently stand as the current configuration's
    evidence."""
    return _sha256(canonical({
        "route": route,
        "model": model,
        "suite": SUITE_NAME,
        "suite_hash": SUITE_HASH,
        "tools": TOOL_DEFINITIONS,
        "parameters": dict(PARAMETERS),
        "tool_choice": TOOL_CHOICE,
    }))


def build_request(model):
    """One trial's request: the synthetic case with the probe
    tools offered natively AND the text contract described, at
    the suite's pinned parameters, tool choice left at the
    provider default (no tool_choice key is sent)."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_TEXT},
            {"role": "user", "content": CASE_TEXT}],
        "tools": TOOL_DEFINITIONS,
        "temperature": PARAMETERS["temperature"],
    }


# ----------------------------------------------------------------
# Classification (scope §3): behaviour observed × delivery status.
# ----------------------------------------------------------------

_UNPARSEABLE = object()


def _json_object(text):
    """The one content object, by the adapter's standing rule:
    the entire stripped content parses as a single JSON object."""
    if not isinstance(text, str):
        return None
    try:
        value = json.loads(text.strip())
    except (ValueError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def _parse_arguments(value):
    """A call's arguments as emitted: a JSON string (the measured
    native envelope) or an object. Returns the parsed value, or
    the _UNPARSEABLE sentinel."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return _UNPARSEABLE
    if value is None:
        return {}
    return value


def _classify_calls(calls):
    """Behaviour for a set of attributable calls, each a
    (name, arguments) pair. payload_form records the hybrid
    detail: an unoffered call whose arguments carry the text
    contract's shape (the `commentary` shape of the empirical
    run) is text_contract_json, a named detail of its class —
    not a class of its own."""
    if any(args is _UNPARSEABLE for _, args in calls):
        return "malformed", None
    payload_form = None
    for name, args in calls:
        if name not in OFFERED_NAMES and isinstance(args, dict) \
                and "tool_requests" in args:
            payload_form = "text_contract_json"
    offered = [name in OFFERED_NAMES for name, _ in calls]
    if all(offered):
        return "native_catalogue", payload_form
    if not any(offered):
        return "environment_tool_attempt", payload_form
    return "mixed", payload_form


def _calls_from_message(message):
    """The native calls in an accepted completion's message, as
    (name, arguments) pairs; None when the message carries no
    readable call set."""
    raw_calls = message.get("tool_calls")
    if not isinstance(raw_calls, list) or not raw_calls:
        return None
    calls = []
    for call in raw_calls:
        if not isinstance(call, dict):
            return [(None, _UNPARSEABLE)]
        function = call.get("function")
        if not isinstance(function, dict) or \
                not isinstance(function.get("name"), str):
            return [(None, _UNPARSEABLE)]
        calls.append((function["name"],
                      _parse_arguments(
                          function.get("arguments"))))
    return calls


def _calls_from_error_body(error_body):
    """The attempted calls attributable from a provider error
    body: the provider's failed-generation object names the call
    it refused to deliver (attempt 8's shape); failing that, the
    error message's own naming. None when no attempt is
    attributable — an unattributable error is a delivery failure,
    not a behaviour."""
    obj = _json_object(error_body)
    if obj is None:
        return None
    error = obj.get("error")
    if not isinstance(error, dict):
        return None
    generation = error.get("failed_generation")
    if isinstance(generation, str):
        parsed = _json_object(generation)
        if parsed is not None and \
                isinstance(parsed.get("name"), str):
            return [(parsed["name"],
                     _parse_arguments(
                         parsed.get("arguments")))]
    message = error.get("message")
    if isinstance(message, str):
        match = re.search(
            r"attempted to call tool '([^']+)'", message)
        if match:
            return [(match.group(1), {})]
    return None


def classify_capture(capture):
    """(behaviour, delivery, payload_form) for one raw capture.

    A capture is the raw-call protocol's return: `body` (the
    provider response body as received), `error_body` (the exact
    provider error body), `http_status`, `diagnostics` (the
    transport's own output, its own object) and `metadata`."""
    body = capture.get("body")
    if isinstance(body, str):
        completion = None
        try:
            completion = json.loads(body)
        except ValueError:
            completion = None
        message = None
        if isinstance(completion, dict):
            try:
                candidate = completion["choices"][0]["message"]
            except (KeyError, IndexError, TypeError):
                candidate = None
            if isinstance(candidate, dict):
                message = candidate
        if message is None:
            # A body was delivered that is not a readable
            # completion in either channel.
            return "malformed", "provider_accepted", None
        calls = _calls_from_message(message)
        if calls is not None:
            behaviour, payload_form = _classify_calls(calls)
            return behaviour, "provider_accepted", payload_form
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            obj = _json_object(content)
            if obj is not None and \
                    obj.get("outcome") == "decline":
                return "refusal", "provider_accepted", None
            if obj is not None and "outcome" in obj:
                return "text_contract", "provider_accepted", None
            return "malformed", "provider_accepted", None
        return ("no_observable_behaviour", "provider_accepted",
                None)
    error_body = capture.get("error_body")
    if isinstance(error_body, str):
        calls = _calls_from_error_body(error_body)
        if calls is not None:
            behaviour, payload_form = _classify_calls(calls)
            return behaviour, "provider_refused", payload_form
        return ("no_observable_behaviour", "provider_failed",
                None)
    if capture.get("http_status") is not None or \
            capture.get("diagnostics"):
        return ("no_observable_behaviour", "provider_failed",
                None)
    return ("no_observable_behaviour", "indeterminate", None)


# ----------------------------------------------------------------
# Evidence retention (scope §3): per object, under the aggregate
# ceiling, hashes outside the budget.
# ----------------------------------------------------------------

def _retain(text, budget):
    """(retained_text, complete): the available bytes bounded by
    the budget; decoding is lossy only past a cut, and the hash
    and byte count are taken over the retained text as retained,
    so what is hashed is exactly what stands in the record."""
    if text is None:
        return None, False
    raw = text.encode("utf-8")
    if len(raw) <= budget:
        return text, True
    return raw[:budget].decode("utf-8", "replace"), False


def trial_evidence(index, capture):
    """One trial's recorded evidence: the two-dimension
    classification, the settled flag, and the per-object retained
    evidence with its hashes. Truncation takes diagnostics first
    and the provider body last; the trial's evidence is complete
    exactly when the provider body stands complete."""
    behaviour, delivery, payload_form = classify_capture(capture)
    body_text = capture.get("body")
    if not isinstance(body_text, str):
        body_text = capture.get("error_body")
    if not isinstance(body_text, str):
        body_text = None
    diag_text = capture.get("diagnostics")
    if not isinstance(diag_text, str):
        diag_text = None
    body_raw = body_text.encode("utf-8") \
        if body_text is not None else b""
    diag_budget = max(0, CAPTURE_CEILING - len(body_raw))
    if diag_text is not None:
        retained_diag, diag_complete = _retain(
            diag_text, diag_budget)
    else:
        retained_diag, diag_complete = None, True
    if body_text is not None:
        retained_body, body_complete = _retain(
            body_text, CAPTURE_CEILING)
    else:
        retained_body, body_complete = None, False
    body_bytes = len(retained_body.encode("utf-8")) \
        if retained_body is not None else 0
    diag_bytes = len(retained_diag.encode("utf-8")) \
        if retained_diag is not None else 0
    metadata = capture.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    status = capture.get("http_status")
    if not isinstance(status, int) or isinstance(status, bool):
        status = None
    return {
        "trial": index,
        "behaviour": behaviour,
        "delivery": delivery,
        "payload_form": payload_form,
        "settled": behaviour != "no_observable_behaviour",
        "provider_body": retained_body,
        "provider_body_bytes": body_bytes,
        "provider_body_sha256": _sha256(
            retained_body.encode("utf-8"))
            if retained_body is not None else None,
        "provider_body_complete": body_complete,
        "http_status": status,
        "metadata": metadata,
        "metadata_sha256": _sha256(canonical(metadata)),
        "diagnostics": retained_diag,
        "diagnostics_bytes": diag_bytes,
        "diagnostics_sha256": _sha256(
            retained_diag.encode("utf-8"))
            if retained_diag is not None else None,
        "diagnostics_complete": diag_complete,
        "aggregate_bytes": body_bytes + diag_bytes,
        "evidence_complete": body_complete,
    }


def summarise(trials):
    """(counts, settled_count, recommended_mode): the counts
    over both dimensions exactly as recorded, and the mode
    derivation of scope §5 — a recommendation needs at least
    QUORUM_SETTLED settled trials and a strict majority of the
    settled ones in a single mode's class; anything else
    recommends nothing."""
    counts = {
        "behaviour": {name: 0 for name in BEHAVIOURS},
        "delivery": {name: 0 for name in DELIVERIES},
    }
    for trial in trials:
        if trial.get("behaviour") in counts["behaviour"]:
            counts["behaviour"][trial["behaviour"]] += 1
        if trial.get("delivery") in counts["delivery"]:
            counts["delivery"][trial["delivery"]] += 1
    settled = sum(1 for trial in trials if trial.get("settled"))
    recommended = None
    if settled >= QUORUM_SETTLED:
        if counts["behaviour"]["text_contract"] * 2 > settled:
            recommended = "text"
        elif counts["behaviour"]["native_catalogue"] * 2 > \
                settled:
            recommended = "native"
    return counts, settled, recommended


# The trial fields the evidence hash binds: the classification,
# the settled flag, and every retained object's hash, size and
# completeness — the hash binds the retained objects by their
# hashes, so the full bodies need not be re-hashed into it.
_TRIAL_HASH_FIELDS = (
    "trial", "behaviour", "delivery", "payload_form", "settled",
    "http_status", "provider_body_sha256", "provider_body_bytes",
    "provider_body_complete", "metadata_sha256",
    "diagnostics_sha256", "diagnostics_bytes",
    "diagnostics_complete", "aggregate_bytes",
    "evidence_complete",
)


def evidence_projection(probed):
    """The evidence-bearing projection of an ASSEMBLY_PROBED
    payload: the generated-record binding, the suite and
    fingerprint, the per-trial evidence summaries, the counts
    and the recommendation."""
    return {
        "generated_record_hash": probed.get(
            "generated_record_hash"),
        "suite": probed.get("suite"),
        "suite_hash": probed.get("suite_hash"),
        "fingerprint": probed.get("fingerprint"),
        "trials": [
            {key: trial.get(key) for key in _TRIAL_HASH_FIELDS}
            for trial in probed.get("trials") or []],
        "counts": probed.get("counts"),
        "settled_count": probed.get("settled_count"),
        "recommended_mode": probed.get("recommended_mode"),
    }


def evidence_hash(probed):
    """The hash ASSEMBLY_PROBED records over its own evidence,
    and that ASSEMBLY_JUDGED and ASSEMBLY_PACKED name: the
    binding that ties the judgement and the seal to this exact
    evidence (scope §4)."""
    return _sha256(canonical(evidence_projection(probed)))


def run_trials(raw_call, model):
    """The bounded trial run: TRIAL_COUNT single generations
    through the injected raw-call callable. A raw call that
    raises, or returns no capture, is itself evidence — a
    delivery failure with the failure as its diagnostic — never
    a probe-stage exception: the stage records what happened,
    including that nothing could be observed."""
    trials = []
    for index in range(1, TRIAL_COUNT + 1):
        request = build_request(model)
        try:
            capture = raw_call(request)
            if not isinstance(capture, dict):
                capture = {
                    "diagnostics": "the raw call returned no "
                                   "capture object"}
        except Exception as exc:  # the capture IS the failure
            capture = {
                "diagnostics": f"{type(exc).__name__}: {exc}"}
        trials.append(trial_evidence(index, capture))
    return trials
