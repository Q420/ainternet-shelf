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
"""

from __future__ import annotations

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
            detail="total deadline exceeded")
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        try:
            stream.close()
        except Exception:
            pass
    raise AdapterFailure(
        "transport_unresolved",
        detail="helper process termination could "
               "not be confirmed after the deadline")


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
        body = json.dumps(
            {"model": model, "messages": messages,
             "temperature": 0.2}).encode("utf-8")
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
                detail="total deadline exceeded")
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
                detail="total deadline exceeded")
        helper_env = dict(os.environ)
        helper_env["GROQ_API_TIMEOUT"] = \
            repr(helper_timeout)
        launch_started = time.monotonic()
        try:
            proc = _Popen(
                [sys.executable, helper_path, "chat", model],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True,
                env=helper_env)
        except OSError as exc:
            timings["helper_launch_s"] = \
                time.monotonic() - launch_started
            raise AdapterFailure("provider_error",
                                 detail=type(exc).__name__)
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
                detail = (err or b"").decode(
                    "utf-8", "replace").strip()
                raise AdapterFailure(
                    "provider_error",
                    detail=f"connector helper exited "
                           f"{proc.returncode}"
                           + (f": {detail[:_DIAGNOSTIC_LIMIT]}"
                              if detail else ""))
            try:
                parsed = json.loads(
                    out.decode("utf-8", "replace"))
            except ValueError:
                raise AdapterFailure(
                    "malformed_response",
                    detail="provider body is not JSON")
            if not isinstance(parsed, dict):
                raise AdapterFailure(
                    "malformed_response",
                    detail="provider body is not an object")
            if parsed.get("error"):
                raise AdapterFailure(
                    "provider_error",
                    detail=f"provider error body: "
                           f"{str(parsed['error'])[:_DIAGNOSTIC_LIMIT]}")
            provider_model_id = parsed.get("model")
            try:
                content = parsed["choices"][0]["message"][
                    "content"]
            except (KeyError, IndexError, TypeError):
                raise AdapterFailure(
                    "malformed_response",
                    detail="no message content in provider "
                           "response")
            return content, provider_model_id
        finally:
            timings["response_parsing_s"] = \
                time.monotonic() - parse_started

    connector_call.last_call_timings = None
    adapter._call = connector_call
    return connector_call
