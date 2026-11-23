"""The provider adapter — Piece 8 (scope Rev 4, PASSED).

An OpenAI-compatible chat-completions adapter implementing
Piece 4's driver boundary. The division of labour is the
scope's settled ground: the DRIVER owns wake construction,
validation, submission, staleness, acknowledgement sequencing
and failure recording; the ADAPTER does only provider
transport, prompt rendering from the supplied package,
response parsing and contract validation, returning a bounded
typed outcome. It never receives the doorway token, never
submits an act, and never fetches record information behind
the driver's back.

- A1. Written against the OpenAI-compatible shape; endpoint,
  credential and model identifier are configuration. First
  exercised provider: NVIDIA's hosted API. No other provider
  is promised as a configuration-only substitution.
- A2. The prompt is rendered from the wake package only —
  role, case, view, reasons, position, and the response
  contract. The doorway token is never in the package, so it
  is never in the prompt or the provider call.
- A4. The model answers with one JSON object naming exactly
  one outcome — acknowledge / contribute (its own text) /
  decline (its reason). The adapter validates the ENTIRE
  response before returning anything: a malformed or
  off-contract answer raises AdapterFailure and no proposal
  is ever partially formed. Outcomes cross the boundary in
  the driver's typed shape; a decline is returned as the
  decline outcome, never flattened into an empty list.
- A5. `identify()` asks the model to state what it is and
  returns the declaration verbatim beside the provider-
  reported model identifier from the response metadata —
  two distinct attributed claims. Neither is a verdict; the
  adapter records nothing and upgrades nothing.
- A6. Each call has one bounded TOTAL deadline (the transport
  timeout covers connection, response and handling). There
  is no retry, automatic or otherwise: a timeout is an
  ambiguous dispatch and raises no_response; an HTTP error
  raises provider_error; an unusable body raises
  malformed_response.
- A7. The API key comes from the constructor argument or the
  named environment variable at call time. It is sent only
  as the Authorization header — never into the record, a
  package, a prompt, or a log line (this module logs nothing).
"""

from __future__ import annotations

import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request

DEFAULT_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

_CONTRACT = """You are a seat in a recorded collaborative run. \
You are shown your case (your assignment), your view of the \
shared work within your evidence boundary, and the reasons you \
were woken. Answer with exactly one JSON object and nothing \
else, naming exactly one outcome:

{"outcome": "contribute", "text": "<your contribution, in your own words>"}
{"outcome": "decline", "reason": "<why you are not contributing>"}

If your case was revised and you have not yet acknowledged the \
new version, your first answer must instead be the \
acknowledgement alone:

{"outcome": "acknowledge"}

Do not invent identifiers, events, or other seats' work. Your \
contribution text is recorded verbatim under your seat."""


class AdapterFailure(Exception):
    """A boundary failure carrying its kind (A4/A6): one of
    no_response, malformed_response, provider_error. The driver
    records it as a DRIVER_FAILURE; it is never an outcome."""

    def __init__(self, kind, detail=None):
        super().__init__(kind)
        self.kind = kind
        self.detail = detail


def _extract_json_object(text):
    """The model's content as one JSON object, or None. The
    contract is exactly one JSON object and nothing else
    (A4): the ENTIRE content, stripped of surrounding
    whitespace only, must parse as that one object. Prose
    around it, a fence, or a second object makes the whole
    response malformed — nothing is extracted from it."""
    if not isinstance(text, str):
        return None
    try:
        obj = json.loads(text.strip())
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


class OpenAICompatibleAdapter:
    """Callable with the driver's boundary signature:
    adapter(package) -> typed outcome (or raises AdapterFailure).
    Also the onboarding identity call: adapter.identify()."""

    def __init__(self, endpoint=DEFAULT_ENDPOINT, model=None,
                 api_key=None, api_key_env="NVIDIA_API_KEY",
                 timeout=120.0):
        self.endpoint = endpoint
        self.model = model
        self._api_key = api_key
        self._api_key_env = api_key_env
        self.timeout = timeout
        self._contribution_counter = 0

    # ----------------------------------------------------- deadline
    def _begin_deadline(self):
        """Open the operation's TOTAL deadline (A6): one
        absolute point on a monotonic clock covering transport,
        response AND the adapter's own handling, through the
        final outcome. Begun by every public operation."""
        self._deadline = time.monotonic() + self.timeout
        return self._deadline

    def _check_deadline(self):
        """Fail the operation if its deadline has passed. A
        successful adapter outcome after the deadline is
        impossible: every public operation checks the clock
        after handling, before returning."""
        if getattr(self, "_deadline", None) is not None and \
                time.monotonic() > self._deadline:
            raise AdapterFailure(
                "no_response", detail="total deadline exceeded")

    # ---------------------------------------------------- transport
    def _call(self, messages):
        """One provider call under the operation's total
        deadline. The transport runs on a daemon worker thread
        and the calling thread enforces the deadline with a
        timed join: EVERY phase — connection, request, the
        response headers urlopen acquires internally, the body,
        parsing — sits under the same absolute point, and on
        expiry the call fails AT the deadline, not on a
        post-return clock check. A timed-out worker is inert:
        its socket timeout (the budget at dispatch) ends it
        within roughly another budget, its late result is
        discarded unread, and nothing can be submitted from
        it — submission happens only on this thread's success
        path. Returns (content, provider_model_id). No retry,
        ever."""
        deadline = getattr(self, "_deadline", None) or \
            self._begin_deadline()
        box = {}

        def work():
            try:
                box["value"] = self._dispatch(messages, deadline)
            except BaseException as exc:  # carried, re-raised here
                box["error"] = exc

        worker = threading.Thread(target=work, daemon=True)
        worker.start()
        worker.join(max(0.0, deadline - time.monotonic()))
        if worker.is_alive():
            raise AdapterFailure(
                "no_response", detail="total deadline exceeded")
        if "error" in box:
            raise box["error"]
        return box["value"]

    def _dispatch(self, messages, deadline):
        """The blocking transport itself (runs on _call's
        worker thread): one urlopen dispatch, the body read
        via read1 with the socket timeout reset to the current
        remaining time before every read — a provider
        drip-feeding inside each socket window cannot hold
        the call open — and the read path FAILS CLOSED: no
        unbounded fallback, no silently ignored inability to
        bound a read."""


        def remaining():
            left = deadline - time.monotonic()
            if left <= 0:
                raise AdapterFailure(
                    "no_response", detail="total deadline exceeded")
            return left

        key = self._api_key or os.environ.get(self._api_key_env)
        body = {"model": self.model, "messages": messages,
                "temperature": 0.2}
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     **({"Authorization": f"Bearer {key}"}
                        if key else {})},
            method="POST")
        try:
            with urllib.request.urlopen(
                    req, timeout=remaining()) as resp:
                chunks = []
                # read1 returns after at most one socket read, so
                # control comes back here between drips and the
                # clock check — not the socket's inactivity
                # window — is what bounds the total. There is no
                # fallback: a stream without a bounded read, or a
                # socket whose timeout cannot be set, fails the
                # call closed rather than reading unbounded.
                read1 = getattr(resp, "read1", None)
                if read1 is None:
                    raise AdapterFailure(
                        "provider_error",
                        detail="response stream offers no bounded "
                               "read; failing closed")
                while True:
                    left = remaining()
                    if getattr(resp, "length", None) == 0:
                        # Completion path, handled explicitly:
                        # a Content-Length body is fully received,
                        # and http.client has retired the stream
                        # (resp.fp is None from here) — no further
                        # read is needed and no timeout is set on
                        # the retired socket.
                        break
                    try:
                        resp.fp.raw._sock.settimeout(left)
                    except Exception:
                        raise AdapterFailure(
                            "provider_error",
                            detail="cannot bound the response "
                                   "read; failing closed")
                    chunk = read1(65536)
                    remaining()
                    if not chunk:
                        break
                    chunks.append(chunk)
                raw = b"".join(chunks).decode("utf-8", "replace")
        except AdapterFailure:
            raise
        except urllib.error.HTTPError as exc:
            raise AdapterFailure("provider_error",
                                 detail=f"HTTP {exc.code}")
        except (socket.timeout, TimeoutError):
            raise AdapterFailure("no_response",
                                 detail="total deadline exceeded")
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (socket.timeout, TimeoutError)):
                raise AdapterFailure("no_response",
                                     detail="total deadline exceeded")
            raise AdapterFailure("provider_error",
                                 detail=type(exc.reason).__name__)
        remaining()
        try:
            parsed = json.loads(raw)
        except ValueError:
            raise AdapterFailure("malformed_response",
                                 detail="provider body is not JSON")
        remaining()
        if not isinstance(parsed, dict):
            raise AdapterFailure("malformed_response",
                                 detail="provider body is not an object")
        provider_model_id = parsed.get("model")
        try:
            content = parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise AdapterFailure("malformed_response",
                                 detail="no message content in "
                                        "provider response")
        return content, provider_model_id

    # --------------------------------------------------------- wake
    def __call__(self, package):
        self._begin_deadline()
        prompt = _CONTRACT + "\n\nYour wake package:\n" + \
            json.dumps(package, indent=1, default=str)
        content, _provider_model = self._call([
            {"role": "system",
             "content": "You are a seat in a recorded "
                        "collaborative run. Answer exactly as "
                        "the contract specifies."},
            {"role": "user", "content": prompt}])
        obj = _extract_json_object(content)
        self._check_deadline()
        if obj is None:
            raise AdapterFailure("malformed_response",
                                 detail="answer is not one JSON "
                                        "object")
        outcome = obj.get("outcome")
        result = None
        if outcome == "acknowledge":
            if set(obj) != {"outcome"}:
                raise AdapterFailure(
                    "malformed_response",
                    detail="acknowledge carries extra fields")
            result = {"outcome": "proposals", "proposals": [{
                "type": "CASE_ACKNOWLEDGED",
                "payload": {"case_id": package["case_id"],
                            "version": package["case_version"]}}]}
        elif outcome == "contribute":
            if set(obj) != {"outcome", "text"} or \
                    not isinstance(obj.get("text"), str) or \
                    not obj["text"].strip():
                raise AdapterFailure(
                    "malformed_response",
                    detail="contribute requires its own text")
            self._contribution_counter += 1
            part = (package.get("case") or {}).get("part")
            result = {"outcome": "proposals", "proposals": [{
                "type": "CONTRIBUTION",
                "payload": {
                    "contribution_id":
                        f"{package['seat']}-live-"
                        f"{package['position']}-"
                        f"{self._contribution_counter}",
                    "tree_part": part,
                    "text": obj["text"]}}]}
        elif outcome == "decline":
            if set(obj) != {"outcome", "reason"} or \
                    not isinstance(obj.get("reason"), str):
                raise AdapterFailure(
                    "malformed_response",
                    detail="decline requires a reason string")
            result = {"outcome": "decline", "reason": obj["reason"]}
        if result is None:
            raise AdapterFailure(
                "malformed_response",
                detail=f"unknown outcome {outcome!r}")
        # The deadline governs through the final outcome (A6):
        # handling that overruns it turns the would-be outcome
        # into a failure — nothing succeeds after the deadline.
        self._check_deadline()
        return result

    # --------------------------------------------------- onboarding
    def identify(self):
        """A5: ask the model to state what it is. Returns
        {"declaration": <the model's words, verbatim>,
         "provider_model_id": <the provider's reported model
        identifier, verbatim, or None>}. Two attributed claims;
        no verdict is formed here."""
        self._begin_deadline()
        content, provider_model_id = self._call([
            {"role": "user",
             "content": "You are being onboarded as a seat in a "
                        "recorded collaborative run. State your "
                        "identity: what model are you, who "
                        "provides you, and what are your "
                        "capabilities and limits? Answer in "
                        "plain text, in your own words."}])
        if not isinstance(content, str) or not content.strip():
            raise AdapterFailure("malformed_response",
                                 detail="empty identity declaration")
        self._check_deadline()
        return {"declaration": content,
                "provider_model_id": provider_model_id}
