"""Connector transport (Groq twin) for the first-worker run harness.

Why this exists (GROQ-TRANSPORT-SCOPE-2026-11-23.md
Rev 2, INDEX 228-231). This is the narrow Groq twin of
connector_transport.py: under Ben's direction and Vane's
settlement, attempt 6 travels a different provider route
(Groq) with a pinned model, everything above the transport
seam unchanged. Like the NVIDIA route (INDEX 191/192), the
working key is Ben's registered connector credential
(custom.groq), held in the Secure Vault — deliberately
not extractable into an environment variable — and the
sanctioned way to spend it is the connector's own helper
(~/workspace/custom-connectors/custom.groq/bin/
groq_api.py), which attaches the credential itself on the
approved request. So this module carries only the adapter's
transport seam — its `_call(messages)` — through that
helper. The adapter, its strict response validation,
outcome typing, identify() and deadline behaviour are
untouched; the A1–A3 lifecycle and the scoped assignment
are untouched. Every guarantee below mirrors the NVIDIA
transport's, word for word where the routes share them.

The cancellation boundary (the examiner's condition,
VANE-FIRST-WORKER-RUN-TRANSPORT-EXAMINATION-2026-11-23.md).
The adapter's own transport enforces one total deadline by
actively terminating its connection and confirming the
worker thread ended (Piece 8, A6) — a wrapper that merely
stops waiting would NOT establish that property. This
wrapper therefore runs the helper as a subprocess in its
own process group and, on expiry of the adapter's total
deadline:

- the subprocess bound is the time REMAINING to the
  deadline the adapter already established
  (`_begin_deadline` sets `adapter._deadline` before every
  public operation, identify() included) — never a fresh
  span, never an extension; if no time remains, the
  helper is not launched at all;
- the remaining time is recomputed immediately AFTER
  the helper is created and before any wait on it:
  process creation can itself consume the rest of the
  deadline, and a stale pre-creation bound would let
  the helper run past it — if the recompute finds the
  deadline gone, the just-launched helper goes through
  the same terminate-and-confirm procedure instead of
  being waited on;
- terminates the helper's whole process group (SIGTERM,
  a brief grace, then SIGKILL) — the group id is a KNOWN
  identity, the helper's own pid (it leads its group,
  start_new_session=True), never a lookup that can fail
  soft into "gone";
- REAPS the child and CONFIRMS the group is gone before
  raising anything;
- only then raises AdapterFailure "no_response" — the
  adapter's own expiry kind, with its own detail;
- if termination cannot be confirmed inside the window,
  raises AdapterFailure with the distinct kind
  "transport_unresolved" — an unresolved transport
  condition, never reported as a terminated one.

There is no retry anywhere, and no path by which a result
can return after expiry: the replacement is synchronous
with a single return point, and on the expiry path that
point is never reached.

The helper's own clock (INDEX 213/215). The helper's
provider request carried its own hardcoded 120s timeout —
a second clock beneath the adapter's span, which is what
attempt 4 died on. The helper now takes its request
timeout from its caller: this transport passes the
effective remaining allowance (the same remaining time it
enforces, computed at launch) as GROQ_API_TIMEOUT in
the helper's environment, and the helper honours it when
set and valid, defaulting to 120s for its ordinary
callers. The transport's bound remains the hard wall —
the group is terminated at the caller's deadline whatever
the helper's internal timeout says.

Timing stages (INDEX 217/219). The installed callable
records the stage timings of its most recent call on its
`last_call_timings` attribute — a plain dict the loop and
the harness read after the call returns or raises: body
preparation, helper launch, the communicate span
(submission, provider wait and receipt — inseparable
through this interface, and labelled as such in the
data), and response parsing. On a failure path the
stages reached stand measured and the rest stand None.
The timings are evidence only; they govern nothing.

Request fidelity. The body sent to the helper mirrors the
adapter's own `_dispatch` byte-for-byte in content:
{"model": <model>, "messages": <messages>,
"temperature": 0.2} — every field the adapter sends. The
one thing that cannot travel through the helper is the
Authorization header: the helper attaches the registered
credential itself, which is the entire point of the route.
(Proxy headers likewise do not apply; the helper owns its
own connection to the one registered host.)

Native-mode staging (native-mode probe piece, INDEX 289
release preparation). In native mode the adapter stages
its offered definitions on the instance for the one call
(`adapter._pending_tools` — adapter A8: the staging exists
precisely so the `_call(messages)` seam keeps its shape),
and `_dispatch` reads them from there. A transport that
replaces `_call` must therefore read the staging itself:
where definitions stand staged, this transport's body
carries them as its "tools" field, exactly as staged, and
a staged tool choice (`adapter._pending_tool_choice`,
where one is staged) as "tool_choice". Where nothing is
staged, the body is byte-identical to the historical
construction above — the text path is untouched.

BD-1's correction (the room rebuild, 2026-11-25). The
adapter stages a second native field for the one call —
`adapter._pending_disable_tool_validation`, the state
its iteration commitment records (INDEX 403) — and the
built-in `_dispatch` carries it in the request body
exactly as staged. This transport read the staged tools
but never the staged flag, so on the live Groq path the
flag fell off between the adapter and the wire and the
provider refused the native call shape the flag exists
to permit (INDEX 411-420: the open BD-1 defect, the
reason the GPT-OSS seat stood judged text). The body
now carries "disable_tool_validation" exactly as staged
wherever a state stands staged, and — where definitions
stand staged with no choice staged — "tool_choice":
"auto", so the request the witness reads permits the
calls it offers.

The probe raw call (same release preparation; capture
contract corrected at INDEX 293). The probe stage's
capture sits BELOW the adapter's response interpretation,
but the adapter's own `probe_raw_call()` rides its
built-in `_exchange` transport — the environment-key
route this harness never uses — and cannot travel the
connector route as built: it never passes through the
replaced `_call` seam. `install_groq_connector_raw_call`
therefore provides the raw call at this layer, against
the same capture contract the adapter's own probe call
honours (framework.probe's raw-call protocol): the
request serialized exactly as given, and the capture
carrying what the provider actually sent. The helper is
invoked in its raw mode (`chat-raw`): it performs the
same surrogate-credentialed request and frames the result
as a JSON envelope carrying the provider's ACTUAL HTTP
status and the response body as RAW BYTES, base64-encoded
(`body_b64`), read whole to EOF — on success and on HTTP
error alike (no retention bound, no collapsing, and no
decoding anywhere on the helper's raw path; the INDEX
261/262 bounded retention governs the helper's ordinary
`chat` failures, not this evidence path). The transport
decodes the base64 back to the exact bytes and applies
the declared probe-boundary policy: STRICT UTF-8. A body
that is valid UTF-8 — the provider's JSON contract —
crosses byte-exact as the capture's body, and the probe
judges retention and completeness over that true body
under its own ceiling. A body that is NOT valid UTF-8 is
never silently rewritten (no replacement characters, no
lossy decode): the capture claims no body, keeps the
actual status, and its diagnostics record the body's byte
length and the SHA-256 of the raw bytes — provenance
without substitution, the body standing unobserved. The
helper's stderr stands separately as the capture's
diagnostics object — diagnostic output is never presented
as the provider body. No status is ever manufactured:
where the helper's output is not a raw-mode envelope (a
helper without the raw mode, answering in the chat shape),
or the helper fails before framing an answer, the capture
claims no status and no body — the absence is recorded
honestly, with the explanation as its diagnostic.
The subprocess discipline is this module's own: the
helper in its own process group, bounded by the adapter's
configured timeout — the fence the adapter's own probe
call runs under, no activation clock existing at assembly
time — terminated and confirmed on expiry, the expiry
itself becoming the capture's diagnostic rather than an
exception, exactly as the adapter's probe call turns its
transport failures into captures.

Failure-kind mapping (mirroring `_dispatch`):
- helper exits non-zero (its HTTP and connection errors
  surface as an uncaught exception and a non-zero exit)
  -> provider_error, as the adapter raises for an HTTP
  error status or a transport-level error;
- the helper cannot be started at all (OSError)
  -> provider_error, mirroring _dispatch's OSError mapping;
- stdout is not JSON / not an object / carries no message
  content -> malformed_response, with the adapter's own
  detail strings;
- an OpenAI-style error body carried through on stdout
  -> provider_error;
- the adapter's deadline expires and, where a helper was
  launched, its termination is confirmed -> no_response,
  detail "total deadline exceeded" (the adapter's own);
  if the deadline had already passed before the call, the
  helper is never launched and the same no_response is
  raised directly; if it expired during process creation,
  the newly launched helper is terminated and confirmed
  first, through the same procedure;
- expiry with termination unconfirmed — including any
  failure to establish the group's identity or emptiness
  -> transport_unresolved (a new kind, used only here).

The worker evidence path (response-evidence piece,
WORKER-RESPONSE-EVIDENCE-SCOPE Rev 8). The worker call
above now travels the helper's BOUNDED raw mode
(`chat-raw-bounded`): the helper reads the provider body
incrementally under the 64,000-byte capture ceiling and
frames the exact observed bytes with their completeness
(body_complete / stop_reason) and, on a pre-response
failure, its phase observation. This transport parses
that envelope itself: the provider body it frames is
the evidence's L1, published on the adapter as
`last_response_evidence` and carried by every
AdapterFailure the call raises, so the loop can persist
and disposition the very answer it worked on. The
failure kinds above are unchanged; what each failure
carries is new. The probe's raw call below is NOT on
this path: it keeps the unbounded `chat-raw` mode and
its own capture contract, exactly as INDEX 295 settled
it — the helper preserves whole bodies for the probe,
and the probe alone truncates.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import signal
import subprocess
import sys
import time

from framework.adapter import AdapterFailure

# The process-group signal/probe, held as a module-level
# alias so the witness can patch it and watch the
# unresolved branch (test_connector_transport.py patches
# _killpg).
_killpg = os.killpg

# The process constructor, likewise a module-level alias
# so the witness can patch it (test 8 makes process
# creation consume the remaining deadline).
_Popen = subprocess.Popen

# The monotonic clock, likewise a module-level alias so
# the witness can substitute a controlled clock and drive
# the deadline boundary deterministically (test 8's
# sweep). connector_call reads the deadline clock only
# through this alias; under the real clock the behaviour
# is identical. (_terminate_and_confirm deliberately
# keeps the real clock: its windows govern physical
# process death, not the adapter's deadline.)
_monotonic = time.monotonic

_TERM_GRACE_SECONDS = 1.0
_CONFIRM_WINDOW_SECONDS = 5.0
_POLL_SECONDS = 0.02

# The bounded length of a diagnostic carried in an
# AdapterFailure detail (the helper's stderr, a provider
# error body): long enough to distinguish causes — the
# full traceback of an ordinary helper failure fits —
# still a bound, so a pathological error body cannot
# grow the record without limit (INDEX 215).
_DIAGNOSTIC_LIMIT = 2000


def _group_gone(pgid):
    """True iff the process group is ESTABLISHED empty —
    only a probe that raises ProcessLookupError establishes
    that. A member answering the probe means not gone;
    PermissionError means a member exists that is not ours
    to signal — still there, not gone; any other probe
    failure propagates, so an unestablishable group is
    never mistaken for an empty one."""
    try:
        _killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def _signal_group(proc, pgid, sig):
    try:
        _killpg(pgid, sig)
        return
    except ProcessLookupError:
        return
    except PermissionError:
        pass  # fall through to the direct child signal
    try:
        proc.send_signal(sig)
    except ProcessLookupError:
        pass


def _terminate_and_confirm(proc):
    """Terminate the helper's whole process group and
    confirm it has ended: SIGTERM, a brief grace, SIGKILL,
    then poll until the child stands reaped (poll() reaps)
    AND the group is empty, inside a bounded confirmation
    window. Returns True only on confirmed termination.

    The group id is KNOWN, not looked up: the helper was
    started with start_new_session=True, so it leads its
    own process group and the group id is the child's pid.
    Any failure to establish the group's emptiness —
    including an exception anywhere in here — leaves the
    termination unconfirmed (the caller maps that to
    transport_unresolved, never no_response)."""
    pgid = proc.pid
    _signal_group(proc, pgid, signal.SIGTERM)
    deadline = time.monotonic() + _TERM_GRACE_SECONDS
    while time.monotonic() < deadline:
        if proc.poll() is not None and _group_gone(pgid):
            return True
        time.sleep(_POLL_SECONDS)
    _signal_group(proc, pgid, signal.SIGKILL)
    deadline = time.monotonic() + _CONFIRM_WINDOW_SECONDS
    while True:
        if proc.poll() is not None and _group_gone(pgid):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(_POLL_SECONDS)


def _worker_seam():
    """A fresh seam observation for the worker evidence
    path (response-evidence piece): the shape
    framework.evidence derives dispositions and artifacts
    from — provenance, the observed status, the L1 bytes
    exactly as observed, the capture's completeness
    facts, the phase observation, and the seam's failure
    facts. Nothing observed yet when this is built."""
    return {
        "provenance": "groq_helper_raw_bounded",
        "http_status": None, "l1_bytes": None,
        "body_complete": None, "stop_reason": None,
        "read_error_kind": None,
        "phase": {"phase": None, "error_kind": None,
                  "http_status": None},
        "seam": {"failure_class": None, "diagnostic": None,
                 "helper_exit": None, "stderr": None,
                 "stdout_bytes": None,
                 "stdout_sha256": None,
                 "termination_confirmed": None,
                 "fence": None},
        "provider_model_id": None, "content": None}


def _timeout_seam(confirmed):
    """The seam observation of a deadline expiry on the
    worker path: the fence expired; where the helper's
    termination was confirmed, the class is
    timeout_after_send — which establishes what the
    PARENT received, not what the helper may already
    have received, and so supports only an unresolved
    disposition (response-evidence scope R5-1); where
    termination is unconfirmed, termination_unconfirmed
    (R4-2)."""
    seam = _worker_seam()
    if confirmed is False:
        seam["seam"]["failure_class"] = \
            "termination_unconfirmed"
    else:
        # Confirmed termination — or no helper was ever
        # launched (confirmed None: the deadline stood
        # expired before the call could begin).
        seam["seam"]["failure_class"] = "timeout_after_send"
    seam["seam"]["fence"] = "adapter_deadline"
    seam["seam"]["termination_confirmed"] = confirmed
    seam["seam"]["diagnostic"] = "total deadline exceeded"
    return seam


def _expire_and_raise(proc):
    """The cancellation boundary, shared by BOTH expiry
    paths — the deadline reached while waiting on the
    helper, and the deadline found already gone
    immediately after the helper was created — so the two
    can never diverge in behaviour: terminate the helper's
    whole process group and CONFIRM it ended before
    raising anything. Confirmed termination raises the
    adapter's own expiry kind, "no_response"; anything
    unconfirmed — including any exception inside the
    termination procedure — raises the distinct kind
    "transport_unresolved", never no_response. This
    function never returns."""
    try:
        confirmed = _terminate_and_confirm(proc)
    except Exception:
        confirmed = False
    if confirmed:
        try:
            proc.communicate(timeout=2.0)  # drain
        except Exception:
            pass
        raise AdapterFailure(
            "no_response",
            detail="total deadline exceeded",
            evidence=_timeout_seam(True))
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        try:
            stream.close()
        except Exception:
            pass
    raise AdapterFailure(
        "transport_unresolved",
        detail="helper process termination could "
               "not be confirmed after the deadline",
        evidence=_timeout_seam(False))


def install_groq_connector_transport(adapter, helper_path=None, model=None):
    """Replace `adapter._call` with a transport carried
    through the connector helper at `helper_path`, calling
    `model`. The replacement keeps the `_call(messages)`
    contract exactly: it returns (content, provider-reported
    model id) taken unaltered from the helper's JSON, and
    raises AdapterFailure under the mapping in this module's
    docstring. Returns the replacement callable.

    The helper path is overridable via the environment
    variable GROQ_HELPER_PATH (default: the real Groq
    connector helper) so witnesses can substitute a stub;
    an explicit helper_path argument takes precedence.
    The model defaults to the adapter's own model."""
    if helper_path is None:
        helper_path = os.environ.get(
            "GROQ_HELPER_PATH") or os.path.expanduser(
            "~/workspace/custom-connectors/custom.groq/bin/"
            "groq_api.py")
    if model is None:
        model = adapter.model

    def connector_call(messages):
        # Stage timings for this call (INDEX 217/219):
        # published on the callable before anything can
        # raise, so a failure path leaves the stages it
        # reached measured and the rest None. The clock
        # here is the real monotonic clock, never the
        # deadline alias the witness patches: these are
        # measurements, not deadline logic.
        timings = {
            "body_preparation_s": None,
            "helper_launch_s": None,
            "submission_provider_wait_receipt_s": None,
            "submission_provider_wait_receipt_note":
                "submission + provider wait + receipt "
                "(inseparable through this interface)",
            "response_parsing_s": None,
        }
        connector_call.last_call_timings = timings
        prep_started = time.monotonic()
        request_obj = {"model": model, "messages": messages,
                       "temperature": 0.2}
        # Native-mode staging (see this module's docstring):
        # the adapter stages its offered definitions on the
        # instance for this one call; a transport replacing
        # _call reads the staging itself, exactly as
        # _dispatch does. Nothing staged -> the body is the
        # historical construction, byte for byte.
        staged_tools = getattr(adapter, "_pending_tools",
                               None)
        if staged_tools:
            request_obj["tools"] = staged_tools
        staged_choice = getattr(adapter,
                                "_pending_tool_choice", None)
        if staged_choice is not None:
            request_obj["tool_choice"] = staged_choice
        elif staged_tools:
            # No choice staged (nothing in the framework
            # stages one): the request must still permit
            # the calls it offers — the provider's own
            # permissive choice, named on the wire rather
            # than left to a default no witness can see.
            request_obj["tool_choice"] = "auto"
        # BD-1's correction (the room rebuild, Ben's
        # direction 2026-11-25: "We need to allow him to
        # use his tools"): the adapter stages its
        # disable_tool_validation state for the one call
        # exactly as it stages the offered definitions —
        # the value the iteration's commitment records —
        # and this transport, which replaces _call on
        # the live Groq path, must carry it to the wire
        # exactly as staged, as the adapter's built-in
        # _dispatch carries it. Before this correction
        # the flag fell off here: the staged tools
        # crossed, the staged flag did not, and the
        # provider refused the native call shape the
        # flag exists to permit (INDEX 411-420). Nothing
        # staged — every text-judged call — the body is
        # the historical construction, byte for byte.
        staged_flag = getattr(
            adapter, "_pending_disable_tool_validation",
            None)
        if staged_flag is not None:
            request_obj["disable_tool_validation"] = \
                staged_flag
        body = json.dumps(request_obj).encode("utf-8")
        timings["body_preparation_s"] = \
            time.monotonic() - prep_started
        # The bound is the time REMAINING to the adapter's
        # own total deadline: _begin_deadline establishes
        # adapter._deadline before every public operation
        # invokes the transport (identify() included), so
        # the helper can never run past the point the
        # adapter itself set. No fresh deadline is created
        # and the existing one is never extended; the
        # adapter's own _check_deadline behaviour is
        # untouched. The only case with no established
        # deadline is a direct _call outside any public
        # operation (the witness does this); then the
        # adapter's configured timeout is the bound.
        call_started = _monotonic()
        established = getattr(adapter, "_deadline", None)
        if established is not None:
            bound = established - call_started
        else:
            bound = adapter.timeout
        if bound <= 0:
            # The adapter's total deadline has already
            # passed: do not launch the helper at all. The
            # adapter's own expiry kind and detail.
            raise AdapterFailure(
                "no_response",
                detail="total deadline exceeded",
                evidence=_timeout_seam(None))
        # The helper receives the effective allowance as
        # its own provider-request timeout (INDEX 215):
        # the same remaining time this transport enforces,
        # computed here at launch with the same formula
        # the post-launch recompute below applies —
        # never the adapter's configured span, never a
        # fresh allowance. The helper's historical 120s
        # default would otherwise stand as a second,
        # hidden clock beneath the caller's deadline
        # (attempt 4). The transport's own bound stays
        # the hard wall regardless: the process group is
        # terminated at the caller's deadline whatever
        # the helper's internal timeout says, so the
        # helper can never outlive the deadline it was
        # handed.
        if established is not None:
            helper_timeout = established - _monotonic()
        else:
            helper_timeout = bound - (_monotonic()
                                      - call_started)
        if helper_timeout <= 0:
            # The deadline passed between the bound check
            # and the launch: the helper is not launched,
            # under the adapter's own expiry kind.
            raise AdapterFailure(
                "no_response",
                detail="total deadline exceeded",
                evidence=_timeout_seam(None))
        helper_env = dict(os.environ)
        helper_env["GROQ_API_TIMEOUT"] = \
            repr(helper_timeout)
        launch_started = time.monotonic()
        try:
            proc = _Popen(
                [sys.executable, helper_path,
                 "chat-raw-bounded", model],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True,
                env=helper_env)
        except OSError as exc:
            timings["helper_launch_s"] = \
                time.monotonic() - launch_started
            seam = _worker_seam()
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = \
                f"the helper could not be started: " \
                f"{type(exc).__name__}"
            raise AdapterFailure("provider_error",
                                 detail=type(exc).__name__,
                                 evidence=seam)
        timings["helper_launch_s"] = \
            time.monotonic() - launch_started
        # Recompute the remaining time now that the helper
        # exists, BEFORE waiting on it: process creation
        # itself can consume the rest of the deadline, and
        # the stale pre-creation bound would then let the
        # helper run past the adapter's actual deadline.
        # With an established deadline the remainder is
        # measured against that deadline; without one, the
        # fallback bound (the adapter's configured timeout)
        # is measured from this call's start, so creation
        # time counts against it the same way.
        if established is not None:
            remaining = established - _monotonic()
        else:
            remaining = bound - (_monotonic()
                                 - call_started)
        if remaining <= 0:
            # The deadline expired during process creation:
            # do not enter the wait at all — put the newly
            # launched helper through the same cancellation
            # procedure as an expiry during the wait.
            # Never returns.
            _expire_and_raise(proc)
        wait_started = time.monotonic()
        try:
            out, err = proc.communicate(input=body,
                                        timeout=remaining)
        except subprocess.TimeoutExpired:
            timings["submission_provider_wait_receipt_s"] = \
                time.monotonic() - wait_started
            # The cancellation boundary: terminate the whole
            # process group and confirm it ended BEFORE
            # raising; an unconfirmed termination is an
            # unresolved transport condition, never a
            # no_response. Nothing returns from this path.
            _expire_and_raise(proc)
        timings["submission_provider_wait_receipt_s"] = \
            time.monotonic() - wait_started
        parse_started = time.monotonic()
        try:
            if proc.returncode != 0:
                # The helper died or errored without
                # framing a bounded envelope: the seam
                # establishes the exit and its stderr, and
                # nothing provider-side (response-evidence
                # scope R5-1: helper_exit_no_envelope,
                # unresolved).
                detail = (err or b"").decode(
                    "utf-8", "replace").strip()
                seam = _worker_seam()
                seam["seam"]["failure_class"] = \
                    "helper_exit_no_envelope"
                seam["seam"]["helper_exit"] = proc.returncode
                seam["seam"]["stderr"] = \
                    detail[:_DIAGNOSTIC_LIMIT]
                seam["seam"]["diagnostic"] = \
                    f"connector helper exited {proc.returncode}"
                raise AdapterFailure(
                    "provider_error",
                    detail=f"connector helper exited "
                           f"{proc.returncode}"
                           + (f": {detail[:_DIAGNOSTIC_LIMIT]}"
                              if detail else ""),
                    evidence=seam)
            envelope = None
            try:
                envelope = json.loads(
                    out.decode("utf-8", "replace"))
            except ValueError:
                envelope = None
            if not isinstance(envelope, dict) or \
                    envelope.get("phase") not in (
                        "pre_response", "response_received") \
                    or "status" not in envelope or \
                    "body_b64" not in envelope:
                # The helper's output is not a bounded raw
                # envelope: what it produced is recorded by
                # count and hash, and nothing about a
                # provider response is claimed from it
                # (envelope_unparseable, unresolved).
                seam = _worker_seam()
                seam["seam"]["failure_class"] = \
                    "envelope_unparseable"
                seam["seam"]["stdout_bytes"] = len(out or b"")
                seam["seam"]["stdout_sha256"] = \
                    hashlib.sha256(out or b"").hexdigest()
                seam["seam"]["diagnostic"] = \
                    "the helper's output was not a bounded " \
                    "raw envelope"
                raise AdapterFailure(
                    "malformed_response",
                    detail="provider body is not JSON",
                    evidence=seam)
            if envelope["phase"] == "pre_response":
                # The helper's own phase observation: the
                # opener failed before any response object
                # existed. Carried to the loop verbatim —
                # the disposition derivation tests it
                # against the promotion rule's three parts.
                seam = _worker_seam()
                seam["phase"] = {
                    "phase": "pre_response",
                    "error_kind": envelope.get("error_kind"),
                    "http_status": None}
                seam["seam"]["diagnostic"] = \
                    "the provider connection failed before " \
                    "a response was received: " \
                    f"{envelope.get('error_kind')}"
                raise AdapterFailure(
                    "provider_error",
                    detail="connection failed before a "
                           "response was received: "
                           f"{envelope.get('error_kind')}",
                    evidence=seam)
            status = envelope["status"]
            raw_b64 = envelope.get("body_b64")
            raw_bytes = None
            if isinstance(raw_b64, str):
                try:
                    raw_bytes = base64.b64decode(
                        raw_b64, validate=True)
                except ValueError:
                    raw_bytes = None
            if raw_bytes is None or \
                    not isinstance(status, int) or \
                    isinstance(status, bool):
                seam = _worker_seam()
                seam["seam"]["failure_class"] = \
                    "envelope_unparseable"
                seam["seam"]["stdout_bytes"] = len(out or b"")
                seam["seam"]["stdout_sha256"] = \
                    hashlib.sha256(out or b"").hexdigest()
                seam["seam"]["diagnostic"] = \
                    "the bounded envelope's body did not " \
                    "decode"
                raise AdapterFailure(
                    "malformed_response",
                    detail="provider body is not JSON",
                    evidence=seam)
            # A response stands observed: the seam's
            # capture is the provider body exactly as the
            # helper framed it — the observed bytes, their
            # completeness and the reason the capture
            # stopped — published on the adapter for the
            # loop's evidence sequence BEFORE any
            # interpretation, and carried by every failure
            # raised from here.
            seam = _worker_seam()
            seam["http_status"] = status
            seam["l1_bytes"] = raw_bytes
            seam["body_complete"] = \
                bool(envelope.get("body_complete"))
            seam["stop_reason"] = envelope.get("stop_reason")
            seam["read_error_kind"] = \
                envelope.get("read_error_kind")
            seam["phase"] = {
                "phase": "response_received",
                "error_kind": None, "http_status": status}
            adapter.last_response_evidence = seam
            if status >= 400:
                # An HTTP error is a response: its body is
                # the captured L1, and the failure is the
                # adapter's provider_error for its status.
                raise AdapterFailure(
                    "provider_error",
                    detail=f"HTTP {status}",
                    evidence=seam)
            try:
                parsed = json.loads(
                    raw_bytes.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                raise AdapterFailure(
                    "malformed_response",
                    detail="provider body is not JSON",
                    evidence=seam)
            if not isinstance(parsed, dict):
                raise AdapterFailure(
                    "malformed_response",
                    detail="provider body is not an object",
                    evidence=seam)
            if parsed.get("error"):
                raise AdapterFailure(
                    "provider_error",
                    detail=f"provider error body: "
                           f"{str(parsed['error'])[:_DIAGNOSTIC_LIMIT]}",
                    evidence=seam)
            provider_model_id = parsed.get("model")
            seam["provider_model_id"] = provider_model_id
            try:
                message = parsed["choices"][0]["message"]
            except (KeyError, IndexError, TypeError):
                raise AdapterFailure(
                    "malformed_response",
                    detail="no message content in provider "
                           "response",
                    evidence=seam)
            if not isinstance(message, dict):
                raise AdapterFailure(
                    "malformed_response",
                    detail="no message content in provider "
                           "response",
                    evidence=seam)
            # The full message is retained on the adapter,
            # exactly as the built-in _dispatch retains it
            # (the native path's translation reads it).
            adapter._last_message = message
            content = message.get("content")
            if content is None and not message.get("tool_calls"):
                raise AdapterFailure(
                    "malformed_response",
                    detail="no message content in provider "
                           "response",
                    evidence=seam)
            seam["content"] = content
            return content, provider_model_id
        finally:
            timings["response_parsing_s"] = \
                time.monotonic() - parse_started

    connector_call.last_call_timings = None
    adapter._call = connector_call
    return connector_call


def install_groq_connector_raw_call(adapter, helper_path=None,
                                    model=None):
    """Provide the probe stage's raw call over this
    transport (see this module's docstring for why it
    lives here and not in the adapter): a callable taking
    the probe's request object exactly as the suite builds
    it and returning the raw capture the probe's protocol
    defines — {"body", "error_body", "http_status",
    "diagnostics", "metadata"} — with capture sitting
    below every layer of response interpretation. The
    helper is invoked in its raw mode (`chat-raw`), whose
    framed envelope carries the provider's actual status
    and the exact response bytes, base64-encoded; the
    bytes are decoded under the declared probe-boundary
    policy (strict UTF-8 — see this module's docstring):
    a body that is not valid UTF-8 stands unobserved,
    its byte length and raw-bytes SHA-256 recorded in
    the diagnostics, never rewritten. Nothing here parses
    outcomes or classifies, and no status is manufactured
    where the envelope does not stand — the probe stage
    reads what this returns. A transport failure is itself
    a capture (its kind as the diagnostic), never an
    exception, exactly as the adapter's own probe_raw_call
    turns its failures into captures.

    The helper path resolution and the model default
    mirror install_groq_connector_transport's. The bound
    is the adapter's configured timeout — the fence the
    adapter's own probe call runs under (a probe is a
    pre-activation assembly act; no activation clock
    exists for it) — enforced by this module's own
    process-group termination, confirmed before the
    capture is returned."""
    if helper_path is None:
        helper_path = os.environ.get(
            "GROQ_HELPER_PATH") or os.path.expanduser(
            "~/workspace/custom-connectors/custom.groq/bin/"
            "groq_api.py")
    if model is None:
        model = adapter.model

    def connector_raw_call(request):
        body = json.dumps(request).encode("utf-8")
        bound = float(adapter.timeout)
        helper_env = dict(os.environ)
        helper_env["GROQ_API_TIMEOUT"] = repr(bound)
        try:
            proc = _Popen(
                [sys.executable, helper_path, "chat-raw",
                 model],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True,
                env=helper_env)
        except OSError as exc:
            return {"body": None, "error_body": None,
                    "http_status": None,
                    "diagnostics": f"provider_error: "
                                   f"{type(exc).__name__}",
                    "metadata": {}}
        try:
            out, err = proc.communicate(input=body,
                                        timeout=bound)
        except subprocess.TimeoutExpired:
            # The cancellation boundary, in capture form:
            # terminate the helper's whole process group
            # and confirm it ended; the expiry — confirmed
            # or unresolved — is the capture's diagnostic.
            try:
                confirmed = _terminate_and_confirm(proc)
            except Exception:
                confirmed = False
            if confirmed:
                try:
                    proc.communicate(timeout=2.0)  # drain
                except Exception:
                    pass
                return {"body": None, "error_body": None,
                        "http_status": None,
                        "diagnostics": "no_response: total "
                                       "deadline exceeded",
                        "metadata": {}}
            for stream in (proc.stdin, proc.stdout,
                           proc.stderr):
                try:
                    stream.close()
                except Exception:
                    pass
            return {"body": None, "error_body": None,
                    "http_status": None,
                    "diagnostics": "transport_unresolved: "
                                   "helper process "
                                   "termination could not "
                                   "be confirmed after the "
                                   "deadline",
                    "metadata": {}}
        out_text = out.decode("utf-8", "replace")
        err_text = err.decode("utf-8", "replace")
        diagnostics = err_text if err_text.strip() else None
        if proc.returncode != 0:
            # The helper itself failed before any provider
            # answer could be framed (a transport-level
            # failure at the helper, or a helper that cannot
            # run at all): no status and no body can be
            # claimed — the helper's own output is the
            # capture's diagnostic, never a body.
            return {"body": None, "error_body": None,
                    "http_status": None,
                    "diagnostics": err_text,
                    "metadata": {}}
        envelope = None
        try:
            envelope = json.loads(out_text)
        except ValueError:
            envelope = None
        raw_bytes = None
        if isinstance(envelope, dict) and \
                isinstance(envelope.get("body_b64"), str):
            try:
                raw_bytes = base64.b64decode(
                    envelope["body_b64"], validate=True)
            except ValueError:
                raw_bytes = None
        if not isinstance(envelope, dict) or \
                not isinstance(envelope.get("status"), int) \
                or isinstance(envelope.get("status"), bool) \
                or raw_bytes is None:
            # The helper's output is not a raw-mode
            # envelope (a helper without the raw mode,
            # answering in the chat shape): the capture
            # claims nothing — no manufactured status, no
            # substituted body — and says why.
            note = ("the helper's output was not a raw-mode "
                    "envelope; no provider status or body "
                    "can be claimed from it")
            return {"body": None, "error_body": None,
                    "http_status": None,
                    "diagnostics": (err_text + "\n" + note)
                    if err_text.strip() else note,
                    "metadata": {}}
        status = envelope["status"]
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # The declared probe-boundary policy (strict
            # UTF-8): a body that is not valid UTF-8 is
            # never silently rewritten — no replacement
            # characters stand in for the provider's
            # bytes. The capture claims no body, keeps the
            # actual status, and records the body's
            # provenance in the diagnostics: its byte
            # length and the SHA-256 of the raw bytes
            # exactly as received.
            note = ("the provider body was not valid "
                    f"UTF-8 ({len(raw_bytes)} bytes, "
                    f"sha256 "
                    f"{hashlib.sha256(raw_bytes).hexdigest()}"
                    "); it stands unobserved rather than "
                    "rewritten")
            return {"body": None, "error_body": None,
                    "http_status": status,
                    "diagnostics": (err_text + "\n" + note)
                    if err_text.strip() else note,
                    "metadata": {}}
        if status >= 400:
            # The provider's error answer, whole: its
            # status, and its exact error body as the
            # error body — retention is the probe's call,
            # over this true body.
            return {"body": None, "error_body": text,
                    "http_status": status,
                    "diagnostics": diagnostics,
                    "metadata": {}}
        metadata = {}
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            for key in ("id", "model"):
                if parsed.get(key) is not None:
                    metadata[key] = parsed[key]
        return {"body": text, "error_body": None,
                "http_status": status,
                "diagnostics": diagnostics,
                "metadata": metadata}

    return connector_raw_call
