"""Shared machinery for the native adapter's follow-up
probes (P1 and P2, INDEX 358): the paced trial runner,
the capture retention, and the per-call record
extraction the two probes share.

This module exists so the two probes do not each carry
a copy of the paced runner's subtle sequencing. The
runner follows framework.native_probe.run_native_trials
step for step — it is the same discipline, generalised
over a per-trial request plan (P1 runs two conditions;
P2 one) and a caller-supplied evidence builder:

- the precondition is the caller's, computed before
  the run and passed in as a problem list; a non-empty
  list refuses before ANY provider request and before
  any pacing wait;
- each trial is sequenced prepare → wait → stamp →
  invoke (INDEX 347): the request is deep-copied
  first, the wait phase then runs against the previous
  trial's call-boundary start, the wall clock is read
  for chronology, and the monotonic start is stamped
  immediately before the raw call is invoked — the
  stamp is the final operation before the call
  (INDEX 349);
- the enforced interval between call-boundary starts
  is native_probe.MIN_TRIAL_START_INTERVAL_SECONDS,
  measured on a monotonic clock end to end (INDEX
  342): after every sleep the elapsed time is
  re-measured, so a sleeper that returns early leaves
  the runner waiting again; the wall clock never
  enters the pacing calculation;
- a raw call that raises, or returns no capture, is
  itself evidence — a delivery failure with the
  failure as its diagnostic — never a runner
  exception.

The per-call record extraction extends the native-
offer probe's with the two fields the follow-up
proposals require preserved per call: the provider
call ID (the message entry's `id`, where the message
carries one) and the call's emitted ordinal (its
position in the response's tool_calls array). Error-
body records carry no provider call ID — the error
body names no delivered call — and their ordinal is
their position in the attributed list.

Delivery classification is NOT one shared rule: the
two probes hold different delivery contracts, and
this core carries each probe's policy as its own
named function rather than imposing a single
classifier on both (build examination correction,
INDEX 359):

- P1's policy (delivery_of_refusal_predicate) is a
  narrow, explicit refusal predicate: provider_
  refused only where the capture's error body IS
  the provider's response-level tool refusal — its
  error object's `code` is "tool_use_failed", the
  shape retained from the evidenced run — whether
  or not an attempt is visible in it. P1's central
  case, a refusal whose attempt is NOT visible, is
  expressible only under this predicate. Every other
  failure — an unrelated 400, a 401, a 413, a 429, a
  5xx, a transport failure — is provider_failed:
  none of those is evidence of the provider
  rejecting a model-generated call.
- P2's policy (delivery_of_attribution) is the
  existing attribution-driven taxonomy of the
  native-offer probe, which P2's proposal retains:
  an error body with an attributable attempt is
  provider_refused; an error body with none is
  provider_failed; a 429 is provider_failed even
  though it arrives as an HTTP error body (INDEX
  339/353 practice); a capture carrying only a
  status or diagnostics is provider_failed; an
  empty capture is indeterminate.
"""

from __future__ import annotations

import copy
import json
import time

from fabric.canonical import canonical, sha256_hex

from . import native_probe as _np
from . import probe as _probe

__all__ = [
    "CAPTURE_CEILING", "DELIVERIES",
    "message_from_body", "text_form_of",
    "call_records_from_message",
    "call_records_from_error_body", "is_tool_refusal",
    "delivery_of_refusal_predicate",
    "delivery_of_attribution",
    "retain_capture", "run_paced_trials",
]

CAPTURE_CEILING = _probe.CAPTURE_CEILING

DELIVERIES = _probe.DELIVERIES


def _sha256(data):
    return _np._sha256(data)


# ----------------------------------------------------------------
# Capture reading: the message, its text form, its calls.
# ----------------------------------------------------------------

def message_from_body(body_text):
    """The assistant message of an accepted completion
    body, or None where the body is not a readable
    completion (the native-offer probe's readability
    rule, shared verbatim)."""
    completion = None
    try:
        completion = json.loads(body_text)
    except ValueError:
        completion = None
    if not isinstance(completion, dict):
        return None
    try:
        candidate = completion["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return None
    return candidate if isinstance(candidate, dict) \
        else None


def text_form_of(message):
    """The message's text channel: "text_contract"
    where its content is the contract's JSON object
    (an object carrying an outcome), "other" where it
    carries other non-empty text, "none" where it
    carries none."""
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        obj = _probe._json_object(content)
        return "text_contract" if (
            obj is not None and "outcome" in obj) \
            else "other"
    return "none"


def _record(name, call_id, ordinal, source, raw_arguments,
            parsed, classify_call):
    return {
        "name": name,
        "id": call_id,
        "ordinal": ordinal,
        "source": source,
        "arguments_raw": raw_arguments,
        "arguments": parsed
        if parsed is not _probe._UNPARSEABLE else None,
        "arguments_parseable":
            parsed is not _probe._UNPARSEABLE,
        "classification": classify_call(name, parsed),
    }


def call_records_from_message(message, classify_call):
    """The per-call records of an accepted completion's
    message: None where the message carries no readable
    call set (no tool_calls, or an empty list). Each
    record carries the provider call ID and the emitted
    ordinal beside the native-offer probe's fields. An
    unreadable call entry stands as one malformed
    record — the response did attempt a call; its
    unreadability is the fact."""
    raw_calls = message.get("tool_calls")
    if not isinstance(raw_calls, list) or not raw_calls:
        return None
    records = []
    for ordinal, call in enumerate(raw_calls):
        function = call.get("function") \
            if isinstance(call, dict) else None
        call_id = call.get("id") \
            if isinstance(call, dict) else None
        if not isinstance(call_id, str) or not call_id:
            call_id = None
        if not isinstance(function, dict) or \
                not isinstance(function.get("name"), str):
            records.append(_record(
                None, call_id, ordinal, "message", None,
                _probe._UNPARSEABLE, classify_call))
            continue
        raw_arguments = function.get("arguments")
        records.append(_record(
            function["name"], call_id, ordinal, "message",
            raw_arguments,
            _probe._parse_arguments(raw_arguments),
            classify_call))
    return records


def call_records_from_error_body(error_body, classify_call):
    """The per-call records attributable from a provider
    error body, through the base probe's own attribution
    (the failed-generation object the provider refused
    to deliver): None where no attempt is attributable.
    Error-body records carry no provider call ID — the
    error body names no delivered call — and the raw
    generation string stands in the retained provider
    body; the record carries the parsed arguments."""
    pairs = _probe._calls_from_error_body(error_body)
    if pairs is None:
        return None
    return [_record(name, None, ordinal, "error_body",
                    None, parsed, classify_call)
            for ordinal, (name, parsed)
            in enumerate(pairs)]


def _http_status(capture):
    """The capture's HTTP status as an int, or None
    where it carries none (a bool is not a status)."""
    status = capture.get("http_status")
    if not isinstance(status, int) or \
            isinstance(status, bool):
        return None
    return status


def is_tool_refusal(error_body):
    """Whether an error body IS the provider's
    response-level tool refusal: the body's error
    object's `code` is "tool_use_failed" — the error
    shape retained from the evidenced run (the
    iteration-18 capture: HTTP 400, error type
    invalid_request_error, code tool_use_failed, a
    failed_generation naming the call the provider
    refused to deliver). The predicate reads the
    code alone: the refusal stands whether or not
    the body also carries a visible attempt;
    attempt visibility is a separate fact the
    caller records, never part of this test."""
    if not isinstance(error_body, str):
        return False
    obj = _probe._json_object(error_body)
    if obj is None:
        return False
    error = obj.get("error")
    return isinstance(error, dict) \
        and error.get("code") == "tool_use_failed"


def delivery_of_refusal_predicate(capture):
    """P1's delivery policy — the narrow refusal
    predicate (see the module docstring): an
    accepted body is provider_accepted; an error
    body that is the provider's response-level tool
    refusal (is_tool_refusal) is provider_refused,
    whether or not an attempt is visible in it;
    every other failure — an unrelated HTTP error
    of any status (an unrelated 400, a 401
    authentication failure, a 413 payload-size
    rejection), a 429 rate limit, a 5xx server
    error, a transport failure standing as a status
    or diagnostics — is provider_failed; an empty
    capture is indeterminate."""
    if isinstance(capture.get("body"), str):
        return "provider_accepted"
    if is_tool_refusal(capture.get("error_body")):
        return "provider_refused"
    if isinstance(capture.get("error_body"), str) \
            or _http_status(capture) is not None \
            or capture.get("diagnostics"):
        return "provider_failed"
    return "indeterminate"


def delivery_of_attribution(capture):
    """P2's delivery policy — the native-offer
    probe's attribution-driven taxonomy, which
    P2's proposal retains (see the module
    docstring): an accepted body is
    provider_accepted; a 429 is provider_failed;
    an error body with an attempt attributable
    through the base probe's own attribution is
    provider_refused; an error body with no
    attributable attempt is provider_failed; a
    capture carrying only a status or diagnostics
    is provider_failed; an empty capture is
    indeterminate."""
    if isinstance(capture.get("body"), str):
        return "provider_accepted"
    if _http_status(capture) == 429:
        return "provider_failed"
    error_body = capture.get("error_body")
    if isinstance(error_body, str):
        return "provider_refused" if (
            _probe._calls_from_error_body(error_body)
            is not None) else "provider_failed"
    if _http_status(capture) is not None \
            or capture.get("diagnostics"):
        return "provider_failed"
    return "indeterminate"


# ----------------------------------------------------------------
# Retention: the capture's durable form under the
# ceiling, on the native-offer probe's discipline.
# ----------------------------------------------------------------

def retain_capture(capture):
    """The retained-evidence fields of one capture: the
    provider body (the response body, or the error body
    where the response was refused) retained whole under
    the capture ceiling, the diagnostics retained in the
    budget the body leaves, each with its byte count and
    hash, and the capture's status and metadata — the
    fields framework.native_probe.trial_evidence records,
    shared so both follow-up probes retain identically.
    `settled` is the body's completeness: settled is
    evidence-complete."""
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
        retained_diag, diag_complete = _probe._retain(
            diag_text, diag_budget)
    else:
        retained_diag, diag_complete = None, True
    if body_text is not None:
        retained_body, body_complete = _probe._retain(
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
    if not isinstance(status, int) or \
            isinstance(status, bool):
        status = None
    return {
        "settled": body_complete,
        "provider_body": retained_body,
        "provider_body_bytes": body_bytes,
        "provider_body_sha256": _sha256(
            retained_body.encode("utf-8"))
        if retained_body is not None else None,
        "provider_body_complete": body_complete,
        "http_status": status,
        "metadata": metadata,
        "metadata_sha256": sha256_hex(canonical(metadata)),
        "diagnostics": retained_diag,
        "diagnostics_bytes": diag_bytes,
        "diagnostics_sha256": _sha256(
            retained_diag.encode("utf-8"))
        if retained_diag is not None else None,
        "diagnostics_complete": diag_complete,
        "aggregate_bytes": body_bytes + diag_bytes,
        "evidence_complete": body_complete,
    }


# ----------------------------------------------------------------
# The paced runner.
# ----------------------------------------------------------------

def _prepare_request(request):
    """The runner's request-preparation step: a deep
    copy of the trial's admitted request, so an
    invocation can never mutate the standing request
    the comparison describes. Preparation runs BEFORE
    the trial's wait phase (INDEX 347), so its cost
    sits outside both the enforced start interval and
    the recorded wait."""
    return copy.deepcopy(request)


def run_paced_trials(raw_call, requests, problems,
                     make_evidence, clock=None,
                     sleeper=None, monotonic_clock=None,
                     wall_clock=None):
    """The bounded paced trial run over a per-trial
    request plan: `requests` holds one admitted request
    per trial, in trial order; `problems` is the
    caller's precondition verdict — a non-empty list
    refuses (NativeProbeRefusal) before any provider
    request and before any pacing wait; `make_evidence`
    (index, capture, wall_start, monotonic_offset,
    wait_phase_seconds) builds each trial's evidence
    record from its capture and pacing fields.

    Exactly one generation request per trial, each
    ending at its first response: no follow-up request,
    no dispatch, no execution, no tool-result response,
    ever. The pacing discipline is the native-offer
    probe's, verbatim in substance (see the module
    docstring): strictly sequential trials, each
    request starting at least
    MIN_TRIAL_START_INTERVAL_SECONDS after the previous
    request's call-boundary start, the wait the
    shortfall re-measured on the monotonic clock after
    every sleep, the wall clock read once per trial
    immediately before the stamp for chronology only.
    The clocks and sleeper are injectable seams so the
    pacing is witnessable without real waiting; the
    legacy `clock` seam, where a caller supplies it,
    serves as both clocks."""
    if problems:
        raise _np.NativeProbeRefusal(
            "the request comparison fails the probe's "
            "precondition; no trial runs: "
            + "; ".join(problems))
    if monotonic_clock is None:
        monotonic_clock = clock if clock is not None \
            else time.monotonic
    if wall_clock is None:
        wall_clock = clock if clock is not None \
            else time.time
    if sleeper is None:
        sleeper = time.sleep
    trials = []
    first_boundary_start = None
    previous_boundary_start = None
    for index, planned in enumerate(requests, start=1):
        request = _prepare_request(planned)
        wait = 0.0
        wait_began = None
        if previous_boundary_start is not None:
            wait_began = monotonic_clock()
            while True:
                shortfall = \
                    _np.MIN_TRIAL_START_INTERVAL_SECONDS \
                    - (monotonic_clock()
                       - previous_boundary_start)
                if shortfall <= 0:
                    break
                sleeper(shortfall)
        wall_start = wall_clock()
        boundary_start = monotonic_clock()
        if wait_began is not None:
            wait = boundary_start - wait_began
        if first_boundary_start is None:
            first_boundary_start = boundary_start
        previous_boundary_start = boundary_start
        try:
            capture = raw_call(request)
            if not isinstance(capture, dict):
                capture = {
                    "diagnostics": "the raw call returned "
                                   "no capture object"}
        except Exception as exc:  # the capture IS the
            # failure, as in the assembly probe's runner
            capture = {
                "diagnostics": f"{type(exc).__name__}: {exc}"}
        trials.append(make_evidence(
            index, capture,
            request_started_wall_at=wall_start,
            request_start_monotonic_offset_seconds=(
                boundary_start - first_boundary_start),
            pacing_wait_phase_seconds=wait))
    return trials
