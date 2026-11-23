"""Connector transport for the first-worker run harness.

Why this exists (INDEX 191/192). The harness's first attempt
died before activation: the Piece 8 adapter authenticates
from an environment-variable key, and the key that route
surfaced was rejected by the provider (HTTP 401); no
reliable environment key exists in this environment. The
working NVIDIA key is Ben's registered connector credential
(custom.nvidia), held in the Secure Vault — deliberately
not extractable into an environment variable — and the
sanctioned way to spend it is the connector's own helper
(~/workspace/custom-connectors/custom.nvidia/bin/
nvidia_api.py), which attaches the credential itself on the
approved request. So this module carries only the adapter's
transport seam — its `_call(messages)` — through that
helper. The adapter, the model, its strict response
validation, outcome typing, identify() and deadline
behaviour are untouched; the A1–A3 lifecycle and the scoped
assignment are untouched.

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
  raised directly;
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

_TERM_GRACE_SECONDS = 1.0
_CONFIRM_WINDOW_SECONDS = 5.0
_POLL_SECONDS = 0.02


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


def install_connector_transport(adapter, helper_path, model):
    """Replace `adapter._call` with a transport carried
    through the connector helper at `helper_path`, calling
    `model`. The replacement keeps the `_call(messages)`
    contract exactly: it returns (content, provider-reported
    model id) taken unaltered from the helper's JSON, and
    raises AdapterFailure under the mapping in this module's
    docstring. Returns the replacement callable."""

    def connector_call(messages):
        body = json.dumps(
            {"model": model, "messages": messages,
             "temperature": 0.2}).encode("utf-8")
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
        established = getattr(adapter, "_deadline", None)
        if established is not None:
            bound = established - time.monotonic()
        else:
            bound = adapter.timeout
        if bound <= 0:
            # The adapter's total deadline has already
            # passed: do not launch the helper at all. The
            # adapter's own expiry kind and detail.
            raise AdapterFailure(
                "no_response",
                detail="total deadline exceeded")
        try:
            proc = subprocess.Popen(
                [sys.executable, helper_path, "chat", model],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True)
        except OSError as exc:
            raise AdapterFailure("provider_error",
                                 detail=type(exc).__name__)
        try:
            out, err = proc.communicate(input=body,
                                        timeout=bound)
        except subprocess.TimeoutExpired:
            # The cancellation boundary: terminate the whole
            # process group and confirm it ended BEFORE
            # raising; an unconfirmed termination is an
            # unresolved transport condition, never a
            # no_response. Nothing returns from this path.
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
            for stream in (proc.stdin, proc.stdout,
                           proc.stderr):
                try:
                    stream.close()
                except Exception:
                    pass
            raise AdapterFailure(
                "transport_unresolved",
                detail="helper process termination could "
                       "not be confirmed after the deadline")
        if proc.returncode != 0:
            detail = (err or b"").decode(
                "utf-8", "replace").strip()
            raise AdapterFailure(
                "provider_error",
                detail=f"connector helper exited "
                       f"{proc.returncode}"
                       + (f": {detail[:200]}" if detail
                          else ""))
        try:
            parsed = json.loads(out.decode("utf-8", "replace"))
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
                       f"{str(parsed['error'])[:200]}")
        provider_model_id = parsed.get("model")
        try:
            content = parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise AdapterFailure(
                "malformed_response",
                detail="no message content in provider "
                       "response")
        return content, provider_model_id

    adapter._call = connector_call
    return connector_call
