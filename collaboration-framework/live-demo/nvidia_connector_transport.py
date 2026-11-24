"""Connector transport (NVIDIA route) for the
native-offer probe's raw call — the transport half of
the NVIDIA-route probe build (NVIDIA-PROBE-BUILD-SCOPE-
2026-11-24, S2/S6).

Why this exists. The probe's raw call must travel the
NVIDIA connector route with the same evidence contract
the Groq route's raw call honours (framework.probe's
raw-call protocol): the request serialized exactly as
given, and the capture carrying what the provider
actually sent, below every layer of response
interpretation. The route's sanctioned credential path
is the connector's own helper
(~/workspace/custom-connectors/custom.nvidia/bin/
nvidia_api.py), which attaches the registered
custom.nvidia credential itself on the approved request
— the working key is deliberately not extractable into
an environment variable, and nothing here touches it.
The helper's raw mode (`chat-raw`, the parity modes the
build added under scope S2) performs the same
surrogate-credentialed request and frames the result as
a JSON envelope carrying the provider's ACTUAL HTTP
status and the response body as RAW BYTES, base64-
encoded (`body_b64`), read whole to EOF — on success
and on HTTP error alike. This module decodes the base64
back to the exact bytes and applies the declared
probe-boundary policy, the Groq transport's own:
STRICT UTF-8. A body that is valid UTF-8 crosses
byte-exact as the capture's body; a body that is NOT
valid UTF-8 is never silently rewritten (no replacement
characters, no lossy decode): the capture claims no
body, keeps the actual status, and its diagnostics
record the body's byte length and the SHA-256 of the
raw bytes — provenance without substitution. The
helper's stderr stands separately as the capture's
diagnostics object — diagnostic output is never
presented as the provider body. No status is ever
manufactured: where the helper's output is not a
raw-mode envelope, or the helper fails before framing
an answer, the capture claims no status and no body —
the absence is recorded honestly, with the explanation
as its diagnostic.

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


def install_nvidia_connector_raw_call(helper_path=None,
                                      model=None,
                                      timeout=None):
    """Provide the probe stage's raw call over the
    NVIDIA connector route (see this module's
    docstring): a callable taking the probe's request
    object exactly as the probe builds it and returning
    the raw capture the probe's protocol defines —
    {"body", "error_body", "http_status", "diagnostics",
    "metadata"} — with capture sitting below every layer
    of response interpretation. Nothing here parses
    outcomes or classifies, and no status is
    manufactured where the envelope does not stand —
    the probe stage reads what this returns.

    helper_path defaults to the NVIDIA connector
    helper (the NVIDIA_HELPER_PATH environment variable
    overrides, as the Groq route's raw call honours its
    own). model is the identifier the helper's chat-raw
    invocation carries; where it is not given, each
    request's own model field is used — the probe's
    request names the pinned model as part of its bound
    construction. timeout is the subprocess bound, the
    fence described in the module docstring; it defaults
    to the helper's own default of 120 seconds."""
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
                [sys.executable, helper_path, "chat-raw",
                 call_model],
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
