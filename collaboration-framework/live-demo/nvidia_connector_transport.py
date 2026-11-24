"""Connector transport (NVIDIA route) for the
native-offer probe's raw call — the transport half of
the NVIDIA-route probe build (NVIDIA-PROBE-BUILD-SCOPE-
2026-11-24, S2/S6), as corrected at the examiner's
build examination (2026-11-24): the probe travels the
helper's BOUNDED raw mode, so the capture ceiling is
enforced in the helper and the bounded capture's own
completeness facts form the transport's evidence path.

Why this exists. The probe's raw call must travel the
NVIDIA connector route under the evidence contract the
scope's S2 settled: capture bounded AT the helper, with
the completeness indicators and phase observations the
evidence path consumes. The route's sanctioned
credential path is the connector's own helper
(~/workspace/custom-connectors/custom.nvidia/bin/
nvidia_api.py), which attaches the registered
custom.nvidia credential itself on the approved request
— the working key is deliberately not extractable into
an environment variable, and nothing here touches it.
The helper's bounded raw mode (`chat-raw-bounded`, the
parity mode the build added under scope S2) performs
the same surrogate-credentialed request and frames the
result as a JSON envelope carrying the provider's
ACTUAL HTTP status and the observed response bytes,
base64-encoded (`body_b64`), read incrementally under
the 64,000-byte capture ceiling — on success and on
HTTP error alike — together with the capture's own
completeness facts: body_complete (claimed only on an
observed EOF), stop_reason ("eof", "capture_limit" or
"read_failure"), read_error_kind, and the phase
observation ("response_received" with the observed
status, or "pre_response" with the failure's kind
where no response object ever existed).

This transport threads that envelope through whole:

- the bounded record — provenance, the phase
  observation, the actual status, the captured bytes'
  count and SHA-256, body_complete, stop_reason,
  read_error_kind — is preserved verbatim on the
  capture as its "transport_capture" record, and the
  probe's trial evidence carries it into the record
  (framework.native_probe_nvidia.trial_evidence), so
  the evidence distinguishes a complete provider body
  from a bounded or interrupted capture by the
  transport's own observations, not by later
  inference;
- a COMPLETE capture (body_complete on an observed
  EOF) is decoded under the declared probe-boundary
  policy, the Groq transport's own: STRICT UTF-8. A
  body that is valid UTF-8 crosses byte-exact as the
  capture's body (or, on an HTTP error status, its
  error body); a body that is NOT valid UTF-8 is
  never silently rewritten (no replacement
  characters, no lossy decode): the capture claims
  no body, keeps the actual status, and its
  diagnostics record the body's byte length and the
  SHA-256 of the raw bytes — provenance without
  substitution;
- an INCOMPLETE capture (capture_limit at the
  ceiling, or read_failure midway) is NEVER turned
  into a complete response by decoding its prefix:
  the capture claims no body and no error body,
  keeps the actual status, and its diagnostics name
  the stop reason, the read-error kind where one
  stands, and the captured prefix's byte count and
  SHA-256. The prefix stands as an incomplete
  capture — observed, bounded, and uninterpreted;
- a pre_response envelope (no response object ever
  existed) claims no status and no body: the phase
  observation and the failure's kind stand in the
  transport record and the diagnostics, and the
  failure stands unresolved, never fabricated.

The helper's stderr stands separately as the capture's
diagnostics object — diagnostic output is never
presented as the provider body. No status is ever
manufactured: where the helper's output is not a
bounded raw envelope, or the helper fails before
framing an answer, the capture claims no status and
no body — the absence is recorded honestly, with the
explanation as its diagnostic.

A note on the route difference, so it is never
"corrected" back: the Groq probe's raw call travels
that route's UNBOUNDED `chat-raw` mode under its own
settled contract (INDEX 295 — the helper preserves
whole bodies for the probe, and the probe alone
truncates). This route's passed scope (S2) and the
examiner's build examination settle the opposite
boundary for the NVIDIA probe: the ceiling is the
helper's, and the bounded capture's completeness
facts are part of the evidence. The two routes'
transports differ because their settled contracts
differ; the probe machinery above the capture
protocol is shared, unchanged.

The subprocess discipline is the Groq transport's own,
reused not re-derived (its _Popen and
_terminate_and_confirm, imported): the helper in its
own process group, bounded by a configured timeout —
the fence a probe call runs under (a probe is a
pre-activation assembly act; no activation clock exists
for it) — terminated and confirmed on expiry, the
expiry itself becoming the capture's diagnostic rather
than an exception. A transport failure is itself a
capture, never an exception. There is no retry
anywhere, and no path by which a result can return
after expiry.

The helper's own clock: the helper takes its provider
request timeout from its caller — this transport passes
the effective bound as NVIDIA_API_TIMEOUT in the
helper's environment, and the helper honours it when
set and valid, defaulting to 120s for its ordinary
callers. The transport's bound remains the hard wall —
the group is terminated at the bound whatever the
helper's internal timeout says.
"""

import base64
import hashlib
import json
import os
import subprocess
import sys

from groq_connector_transport import (  # noqa: E402
    _Popen, _terminate_and_confirm)

DEFAULT_HELPER_PATH = os.path.expanduser(
    "~/workspace/custom-connectors/custom.nvidia/bin/"
    "nvidia_api.py")
DEFAULT_TIMEOUT = 120.0


def _capture(body=None, error_body=None, http_status=None,
             diagnostics=None, metadata=None,
             transport_capture=None):
    """One raw capture in the probe's protocol, with
    the transport's bounded-capture record threaded
    beside the protocol's own fields (see this
    module's docstring): the record stands None where
    no bounded envelope was ever framed — a helper
    that could not start, an expiry, a helper failure
    before framing — and stands as the envelope's own
    observations where one was."""
    return {"body": body, "error_body": error_body,
            "http_status": http_status,
            "diagnostics": diagnostics,
            "metadata": metadata if metadata is not None
            else {},
            "transport_capture": transport_capture}


def _bounded_record(phase, error_kind, status, captured,
                    body_complete, stop_reason,
                    read_error_kind):
    """The transport's bounded-capture record: the
    bounded envelope's own observations, preserved
    verbatim — the phase observation, the actual
    status, the captured bytes' count and SHA-256
    (of exactly the bytes the helper framed), and the
    completeness facts. Nothing here is inferred:
    every field is the helper's framed observation or
    a direct measure of the framed bytes."""
    return {
        "provenance": "nvidia_helper_raw_bounded",
        "phase": phase,
        "phase_error_kind": error_kind,
        "http_status": status,
        "captured_bytes":
            len(captured) if captured is not None
            else None,
        "captured_sha256":
            hashlib.sha256(captured).hexdigest()
            if captured is not None else None,
        "body_complete": body_complete,
        "stop_reason": stop_reason,
        "read_error_kind": read_error_kind,
    }


def install_nvidia_connector_raw_call(helper_path=None,
                                      model=None,
                                      timeout=None):
    """Provide the probe stage's raw call over the
    NVIDIA connector route (see this module's
    docstring): a callable taking the probe's request
    object exactly as the probe builds it and returning
    the raw capture the probe's protocol defines —
    {"body", "error_body", "http_status", "diagnostics",
    "metadata"} — carrying, beside them, the bounded
    transport record as "transport_capture", with
    capture sitting below every layer of response
    interpretation. The helper is invoked in its
    bounded raw mode (`chat-raw-bounded`): the capture
    ceiling is enforced in the helper, and only a
    capture the helper framed complete is ever decoded
    into a body. Nothing here parses outcomes or
    classifies, and no status is manufactured where
    the envelope does not stand — the probe stage
    reads what this returns.

    helper_path defaults to the NVIDIA connector
    helper (the NVIDIA_HELPER_PATH environment variable
    overrides, as the Groq route's raw call honours its
    own). model is the identifier the helper's
    chat-raw-bounded invocation carries; where it is
    not given, each request's own model field is used
    — the probe's request names the pinned model as
    part of its bound construction. timeout is the
    subprocess bound, the fence described in the
    module docstring; it defaults to the helper's own
    default of 120 seconds."""
    if helper_path is None:
        helper_path = os.environ.get(
            "NVIDIA_HELPER_PATH") or DEFAULT_HELPER_PATH
    bound = float(timeout) if timeout is not None \
        else DEFAULT_TIMEOUT

    def connector_raw_call(request):
        call_model = model if model is not None \
            else request.get("model")
        body = json.dumps(request).encode("utf-8")
        helper_env = dict(os.environ)
        helper_env["NVIDIA_API_TIMEOUT"] = repr(bound)
        try:
            proc = _Popen(
                [sys.executable, helper_path,
                 "chat-raw-bounded", call_model],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True,
                env=helper_env)
        except OSError as exc:
            return _capture(
                diagnostics=f"provider_error: "
                            f"{type(exc).__name__}")
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
                return _capture(
                    diagnostics="no_response: total "
                                "deadline exceeded")
            for stream in (proc.stdin, proc.stdout,
                           proc.stderr):
                try:
                    stream.close()
                except Exception:
                    pass
            return _capture(
                diagnostics="transport_unresolved: "
                            "helper process "
                            "termination could not "
                            "be confirmed after the "
                            "deadline")
        out_text = out.decode("utf-8", "replace")
        err_text = err.decode("utf-8", "replace")
        diagnostics = err_text if err_text.strip() else None

        def with_note(note):
            return (err_text + "\n" + note) \
                if err_text.strip() else note

        if proc.returncode != 0:
            # The helper itself failed before any provider
            # answer could be framed (a transport-level
            # failure at the helper, or a helper that cannot
            # run at all): no status and no body can be
            # claimed — the helper's own output is the
            # capture's diagnostic, never a body.
            return _capture(diagnostics=err_text)
        envelope = None
        try:
            envelope = json.loads(out_text)
        except ValueError:
            envelope = None
        if not isinstance(envelope, dict) or \
                envelope.get("phase") not in (
                    "pre_response", "response_received") \
                or "status" not in envelope or \
                "body_b64" not in envelope:
            # The helper's output is not a bounded raw
            # envelope: the capture claims nothing — no
            # manufactured status, no substituted body —
            # and says why.
            return _capture(diagnostics=with_note(
                "the helper's output was not a bounded "
                "raw envelope; no provider status or "
                "body can be claimed from it"))
        if envelope["phase"] == "pre_response":
            # The helper's own phase observation: the
            # opener failed before any response object
            # existed. No status and no body stand; the
            # phase and the failure's kind are carried
            # verbatim — in the diagnostics and in the
            # transport record — and the failure stands
            # unresolved, never fabricated.
            record = _bounded_record(
                "pre_response",
                envelope.get("error_kind"),
                None, None,
                envelope.get("body_complete"),
                envelope.get("stop_reason"),
                envelope.get("read_error_kind"))
            return _capture(
                diagnostics=with_note(
                    "the provider connection failed "
                    "before a response was received: "
                    f"{envelope.get('error_kind')}"),
                transport_capture=record)
        status = envelope["status"]
        raw_b64 = envelope.get("body_b64")
        captured = None
        if isinstance(raw_b64, str):
            try:
                captured = base64.b64decode(
                    raw_b64, validate=True)
            except ValueError:
                captured = None
        if captured is None or \
                not isinstance(status, int) or \
                isinstance(status, bool):
            # The envelope's framed body did not decode,
            # or its status does not stand: the envelope
            # itself cannot be trusted, so nothing about
            # a provider response is claimed from it.
            return _capture(diagnostics=with_note(
                "the bounded envelope's body did not "
                "decode; no provider status or body "
                "can be claimed from it"))
        record = _bounded_record(
            "response_received",
            envelope.get("error_kind"),
            status, captured,
            envelope.get("body_complete"),
            envelope.get("stop_reason"),
            envelope.get("read_error_kind"))
        if record["body_complete"] is not True:
            # An INCOMPLETE capture — bounded at the
            # ceiling, or interrupted by a read failure:
            # the captured prefix is NEVER decoded into
            # a response. The capture claims no body and
            # no error body; the actual status stands;
            # the diagnostics and the transport record
            # carry the capture's own facts — the stop
            # reason, the read-error kind where one
            # stands, and the prefix's byte count and
            # SHA-256 — provenance without substitution.
            note = (
                "the provider response was captured "
                "incompletely by the bounded capture: "
                f"{record['captured_bytes']} bytes stand "
                f"captured (sha256 "
                f"{record['captured_sha256']}), "
                f"stop_reason {record['stop_reason']}"
                + (f", read error "
                   f"{record['read_error_kind']}"
                   if record["read_error_kind"] else "")
                + "; the captured prefix is not decoded, "
                "classified or retained as a response "
                "body — it stands as an incomplete "
                "capture, its completeness facts "
                "carried in the capture's "
                "transport_capture record")
            return _capture(
                http_status=status,
                diagnostics=with_note(note),
                transport_capture=record)
        try:
            text = captured.decode("utf-8")
        except UnicodeDecodeError:
            # The declared probe-boundary policy (strict
            # UTF-8): a COMPLETE body that is not valid
            # UTF-8 is never silently rewritten — no
            # replacement characters stand in for the
            # provider's bytes. The capture claims no
            # body, keeps the actual status, and records
            # the body's provenance in the diagnostics:
            # its byte length and the SHA-256 of the raw
            # bytes exactly as received.
            note = ("the provider body was not valid "
                    f"UTF-8 ({len(captured)} bytes, "
                    f"sha256 "
                    f"{hashlib.sha256(captured).hexdigest()}"
                    "); it stands unobserved rather than "
                    "rewritten")
            return _capture(
                http_status=status,
                diagnostics=with_note(note),
                transport_capture=record)
        if status >= 400:
            # The provider's error answer, complete: its
            # status, and its exact error body as the
            # error body — the bounded path carried it
            # whole under the ceiling, and retention is
            # the probe's call over this true body.
            return _capture(
                error_body=text, http_status=status,
                diagnostics=diagnostics,
                transport_capture=record)
        metadata = {}
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            for key in ("id", "model"):
                if parsed.get(key) is not None:
                    metadata[key] = parsed[key]
        return _capture(
            body=text, http_status=status,
            diagnostics=diagnostics, metadata=metadata,
            transport_capture=record)

    return connector_raw_call
