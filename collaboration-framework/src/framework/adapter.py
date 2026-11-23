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
  is never in the prompt or the provider call. Piece A3-CAT:
  where the package carries a tool catalogue (its `tools`
  field), the catalogue is rendered as its own section of
  the prompt, its entries verbatim from the package — the
  adapter invents, renames and supplements nothing, and
  adds only the section's framing lines. A package without
  a tools field renders exactly as before.
- A4. The model answers with one JSON object naming exactly
  one outcome — acknowledge / contribute (its own text) /
  decline (its reason). The adapter validates the ENTIRE
  response before returning anything: a malformed or
  off-contract answer raises AdapterFailure and no proposal
  is ever partially formed. Outcomes cross the boundary in
  the driver's typed shape; a decline is returned as the
  decline outcome, never flattened into an empty list.
  Piece A3 (R49/R51) extends the outcome set at this same
  boundary: a contribution may carry tool requests, a
  tool_requests outcome carries requests alone, and a yield
  carries a summary alone — terminal outcomes are mutually
  exclusive, and any combination is malformed whole. The
  caller may also supply the activation's remaining budget
  as a call parameter (never in the prompt): the activation
  deadline governs, the per-call limit only tightens, and a
  call that cannot begin within budget does not begin.
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

import http.client
import json
import os
import socket
import threading
import time
import urllib.parse
import urllib.request

DEFAULT_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

_CONTRACT = """You are a seat in a recorded collaborative run. \
You are shown your case (your assignment), your view of the \
shared work within your evidence boundary, and the reasons you \
were woken. Answer with exactly one JSON object and nothing \
else, naming exactly one outcome:

{"outcome": "contribute", "text": "<your contribution, in your own words>"}
{"outcome": "decline", "reason": "<why you are not contributing>"}

A contribution may also carry tool requests, and tools may be \
requested on their own (Piece A3):

{"outcome": "contribute", "text": "<your contribution>", \
"tool_requests": [{"tool": "<tool>", "parameters": {...}}]}
{"outcome": "tool_requests", "requests": [{"tool": "<tool>", \
"parameters": {...}}]}

To yield the work, answer with a summary only — a yield \
carries nothing else:

{"outcome": "yield", "summary": "<what stands>"}

If your case was revised and you have not yet acknowledged the \
new version, your first answer must instead be the \
acknowledgement alone:

{"outcome": "acknowledge"}

Do not invent identifiers, events, or other seats' work. Your \
contribution text is recorded verbatim under your seat."""

_TOOL_SECTION = (
    "\n\nYour tool catalogue — the tools your sealed grants "
    "advertise, with their descriptions, parameters and "
    "limits. You may request only these tools, under these "
    "exact names:\n")


def _render_prompt(package):
    """The wake prompt (Piece A3-CAT): the contract, the wake
    package as structured data, and — where the package
    carries a tool catalogue — the catalogue in its own
    section, its entries verbatim from the package. The
    adapter invents, renames and supplements nothing: the
    section's framing lines are the only words it adds. A
    package without a tools field (the seat-driver path)
    renders byte-identically to before."""
    tools = package.get("tools") if isinstance(package, dict) \
        else None
    if tools is None:
        return _CONTRACT + "\n\nYour wake package:\n" + \
            json.dumps(package, indent=1, default=str)
    body = {key: value for key, value in package.items()
            if key != "tools"}
    return _CONTRACT + "\n\nYour wake package:\n" + \
        json.dumps(body, indent=1, default=str) + \
        _TOOL_SECTION + json.dumps(tools, indent=1,
                                   default=str)


class AdapterFailure(Exception):
    """A boundary failure carrying its kind (A4/A6): one of
    no_response, malformed_response, provider_error — or
    transport_unresolved, raised only by the connector
    transport (live-demo/connector_transport.py) when a
    helper process's termination after the deadline could
    not be confirmed. That kind names a transport failure,
    not an adapter outcome. The driver records it as a
    DRIVER_FAILURE; it is never an outcome."""

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
    def _begin_deadline(self, budget=None):
        """Open the operation's TOTAL deadline (A6): one
        absolute point on a monotonic clock covering transport,
        response AND the adapter's own handling, through the
        final outcome. Begun by every public operation. A
        supplied activation budget (Piece A3, R49/R51) only
        tightens the span: the activation deadline is the
        governing limit and the per-call limit never extends
        past it."""
        span = self.timeout
        if budget is not None:
            span = min(span, budget)
        self._deadline = time.monotonic() + span
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
        over a connection this adapter owns from creation
        (http.client, not urlopen), and the calling thread
        enforces the deadline with a timed join: EVERY phase
        -- connection, request, response headers, body,
        parsing -- sits under the same absolute point. On
        expiry the caller ACTIVELY TERMINATES the transport:
        the published connection's socket is shut down and
        closed, which interrupts whatever blocking read the
        worker is inside, and the worker is joined for a
        short grace period to confirm it ended. A provider
        operation therefore cannot outlive its deadline on
        any path where a socket exists; the only phase no
        shutdown can reach is a connection attempt whose
        socket has not been created yet, and that is bounded
        by the dispatch-time socket timeout. Nothing can be
        submitted from a terminated worker: submission
        happens only on this thread's success path. Returns
        (content, provider_model_id). No retry, ever."""
        deadline = getattr(self, "_deadline", None) or \
            self._begin_deadline()
        self._active_conn = None
        box = {}

        def work():
            try:
                box["value"] = self._dispatch(messages, deadline)
            except BaseException as exc:  # carried, re-raised here
                box["error"] = exc

        worker = threading.Thread(target=work, daemon=True)
        self._last_worker = worker
        worker.start()
        worker.join(max(0.0, deadline - time.monotonic()))
        if worker.is_alive():
            conn = self._active_conn
            if conn is not None:
                try:
                    if conn.sock is not None:
                        conn.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass
            worker.join(1.0)
            self._worker_terminated = not worker.is_alive()
            raise AdapterFailure(
                "no_response", detail="total deadline exceeded")
        if "error" in box:
            raise box["error"]
        return box["value"]

    def _open_connection(self, remaining):
        """Build (not yet connect) the connection for the
        endpoint, honouring the environment's proxy
        configuration the way urllib would (getproxies +
        proxy_bypass): direct, absolute-form through an HTTP
        proxy, or a CONNECT tunnel for HTTPS. The connection
        is published to self._active_conn BEFORE any blocking
        operation, so the calling thread can terminate the
        transport at the deadline. Returns (conn, path)."""
        parsed = urllib.parse.urlsplit(self.endpoint)
        scheme = parsed.scheme or "http"
        host = parsed.hostname
        port = parsed.port or (443 if scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        proxy_url = None
        if not urllib.request.proxy_bypass(host):
            proxies = urllib.request.getproxies()
            proxy_url = proxies.get(scheme) or proxies.get("all")
        timeout = remaining()
        extra_headers = {}
        if proxy_url:
            p = urllib.parse.urlsplit(proxy_url)
            phost = p.hostname
            pport = p.port or 8080
            if p.username:
                import base64 as _b64
                cred = _b64.b64encode(
                    f"{urllib.parse.unquote(p.username)}:"
                    f"{urllib.parse.unquote(p.password or '')}"
                    .encode()).decode()
                extra_headers["Proxy-Authorization"] = \
                    f"Basic {cred}"
            if scheme == "https":
                conn = http.client.HTTPSConnection(
                    phost, pport, timeout=timeout)
                conn.set_tunnel(host, port,
                                headers=extra_headers or None)
            else:
                conn = http.client.HTTPConnection(
                    phost, pport, timeout=timeout)
                path = self.endpoint  # absolute-form
        elif scheme == "https":
            conn = http.client.HTTPSConnection(host, port,
                                               timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, port,
                                              timeout=timeout)
        self._active_conn = conn
        self._proxy_headers = extra_headers if \
            (proxy_url and scheme == "http") else {}
        return conn, path

    def _dispatch(self, messages, deadline):
        """The blocking transport itself (runs on _call's
        worker thread) over the owned connection: request,
        header acquisition, and the body read via read1 with
        the socket timeout reset to the current remaining
        time before every read -- a provider drip-feeding
        inside each socket window cannot hold the read loop
        open -- and the read path FAILS CLOSED: no unbounded
        fallback, no silently ignored inability to bound a
        read. Phases outside the read loop (connect, headers)
        are bounded by the calling thread's active
        termination at the deadline (see _call)."""

        def remaining():
            left = deadline - time.monotonic()
            if left <= 0:
                raise AdapterFailure(
                    "no_response", detail="total deadline exceeded")
            return left

        key = self._api_key or os.environ.get(self._api_key_env)
        payload = json.dumps(
            {"model": self.model, "messages": messages,
             "temperature": 0.2}).encode("utf-8")
        conn, path = self._open_connection(remaining)
        try:
            headers = {"Content-Type": "application/json",
                       **({"Authorization": f"Bearer {key}"}
                          if key else {}),
                       **getattr(self, "_proxy_headers", {})}
            conn.request("POST", path, body=payload,
                         headers=headers)
            if conn.sock is not None:
                conn.sock.settimeout(remaining())
            resp = conn.getresponse()
            if resp.status >= 400:
                raise AdapterFailure(
                    "provider_error", detail=f"HTTP {resp.status}")
            chunks = []
            read1 = getattr(resp, "read1", None)
            if read1 is None:
                raise AdapterFailure(
                    "provider_error",
                    detail="response stream offers no bounded "
                           "read; failing closed")
            while True:
                left = remaining()
                if getattr(resp, "length", None) == 0:
                    # Completion path, handled explicitly: a
                    # Content-Length body is fully received and
                    # http.client has retired the stream -- no
                    # further read, no timeout set on it.
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
        except (socket.timeout, TimeoutError):
            raise AdapterFailure("no_response",
                                 detail="total deadline exceeded")
        except (http.client.HTTPException, OSError) as exc:
            raise AdapterFailure("provider_error",
                                 detail=type(exc).__name__)
        finally:
            try:
                conn.close()
            except Exception:
                pass
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
    def __call__(self, package, budget=None):
        """One bounded call. budget (Piece A3, R49/R51) is the
        activation's remaining budget in seconds, supplied by
        the caller as a call parameter — it never enters the
        prompt the model sees. The activation deadline governs:
        the call's span is the tighter of the per-call limit
        and the budget, and a call that cannot begin within
        budget does not begin at all."""
        if budget is not None:
            if isinstance(budget, bool) or \
                    not isinstance(budget, (int, float)):
                raise AdapterFailure(
                    "malformed_response",
                    detail="the supplied budget is not a number")
            if budget <= 0:
                raise AdapterFailure(
                    "no_response",
                    detail="the activation deadline has "
                           "passed; the call cannot begin "
                           "within budget")
        self._begin_deadline(budget)
        prompt = _render_prompt(package)
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
            if set(obj) not in ({"outcome", "text"},
                                {"outcome", "text",
                                 "tool_requests"}) or \
                    not isinstance(obj.get("text"), str) or \
                    not obj["text"].strip():
                raise AdapterFailure(
                    "malformed_response",
                    detail="contribute requires its own text")
            requests = None
            if "tool_requests" in obj:
                # Piece A3: a contribution may carry tool
                # requests — one response, two kinds of act,
                # validated whole like everything else here.
                requests = self._tool_requests(
                    obj["tool_requests"])
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
            if requests is not None:
                result["tool_requests"] = requests
        elif outcome == "tool_requests":
            # Piece A3 (R49): tool requests on their own —
            # requests only, no contribution, nothing else.
            if set(obj) != {"outcome", "requests"}:
                raise AdapterFailure(
                    "malformed_response",
                    detail="a tool_requests outcome carries "
                           "its requests and nothing else")
            result = {"outcome": "tool_requests",
                      "tool_requests": self._tool_requests(
                          obj.get("requests"))}
        elif outcome == "yield":
            # Piece A3 (R49/R54): a yield carries a summary
            # only — combined with anything else it is not a
            # yield, and the whole response is malformed.
            if set(obj) != {"outcome", "summary"} or \
                    not isinstance(obj.get("summary"), str) or \
                    not obj["summary"].strip():
                raise AdapterFailure(
                    "malformed_response",
                    detail="a yield carries a summary only")
            result = {"outcome": "yield",
                      "summary": obj["summary"]}
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

    @staticmethod
    def _tool_requests(value):
        """Validate a tool-request list whole (Piece A3): a
        non-empty list of objects each naming exactly a tool
        (a non-empty string) and its parameters (an object).
        Anything else makes the whole response malformed —
        no request is ever partially formed. Returns the
        requests in the caller's shape."""
        if not isinstance(value, list) or not value:
            raise AdapterFailure(
                "malformed_response",
                detail="tool requests are a non-empty list")
        requests = []
        for entry in value:
            if not isinstance(entry, dict) or \
                    set(entry) != {"tool", "parameters"} or \
                    not isinstance(entry.get("tool"), str) or \
                    not entry["tool"] or \
                    not isinstance(entry.get("parameters"), dict):
                raise AdapterFailure(
                    "malformed_response",
                    detail="each tool request names exactly a "
                           "tool and its parameters object")
            requests.append({"tool": entry["tool"],
                             "parameters": entry["parameters"]})
        return requests

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
