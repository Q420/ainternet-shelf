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
  as a call parameter (never in the prompt): a budget-
  carrying call is governed EXCLUSIVELY by that budget —
  the remaining activation deadline is its one clock, and
  the configured per-call timeout plays no part in it
  (INDEX 219, an adapter deadline-semantics change: the
  earlier rule, under which the per-call limit only
  tightened the budget, silently reintroduced a subordinate
  per-call span over every worker call). The configured
  timeout survives ONLY as the finite fence for calls
  carrying no budget — identify() and the other
  pre-activation calls, made before any activation clock
  exists. A call that cannot begin within budget does not
  begin. Where the caller also supplies the activation's
  ABSOLUTE deadline — a monotonic instant propagated from
  the framework (INDEX 222) — that point is the call's
  deadline VERBATIM: the adapter enforces the framework's
  one clock rather than reconstructing a deadline from the
  sampled budget, so no interval between the framework's
  sampling and the adapter's establishment can push the
  cancellation boundary past the activation deadline. The
  adapter also times its own prompt rendering
  (last_render_s) — timing evidence under INDEX 217/219;
  it governs nothing.
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
- A8. Native mode (native-mode probe piece, probe scope §6):
  where the sealed package's judged mode is native, the call
  additionally offers tool definitions derived from the
  package's own catalogue — the same per-grant derivation the
  loop renders as text. The mode is read only from the
  sealed package (the loop passes it from the ASSEMBLY_PACKED
  act); the text path is otherwise byte-identical, and from
  the doorway onward nothing differs. Translation never
  normalises an invalid request into an authorised one: a
  translated request faces the doorway exactly as its
  text-form twin does. `probe_raw_call()` serves the probe
  stage: one generation whose response is returned as a raw
  capture — body, error body, status, diagnostics — below
  this module's own response interpretation.
- A9. Per-call extraction (native adapter piece,
  NATIVE-ADAPTER-SCOPE Rev 3 — N6/N13, build brief B1):
  a native response's tool_calls are no longer translated
  fail-whole. Each call is EXTRACTED — one record per call
  in emitted order, carrying the provider call ID exactly
  as emitted, the name, the arguments (the JSON-string and
  object forms both accepted, N40), and the call's provider
  ordinal — and the records cross the boundary as the
  `native_calls` outcome, for the loop's classification,
  translation record and dispatch (the loop's corridor,
  not this module's). A defect inside one call — an
  unreadable name, an arguments value in a shape
  classification must refuse — is carried in that call's
  record for the loop to refuse per call; it no longer
  ends the response. Defects
  of the response as a whole still fail whole here: a
  tool_calls structure that is not a list of objects, and
  a response carrying both content and tool calls (the
  channels are not mixed, N12). In native mode the prompt
  also carries the examined contract wording of N30 —
  native calls are proposals, their outcomes or refusals
  arrive in the next package under the call's own ID —
  and the request carries `disable_tool_validation` as
  the constructor's flag state stands (BD-1: enabled by
  default, so an unoffered call is DELIVERED to the
  framework's own resolver instead of dying at the
  provider; the flag changes where an unoffered call is
  stopped, never whether it may take effect).
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import socket
import threading
import time
import urllib.parse
import urllib.request

from . import nemotron_names as _nemotron_names

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

# The native arrangement, named to the model (native
# adapter piece, N30 — examined scope wording, implemented
# as written): native calls are proposals, not actions,
# and every call's outcome or refusal arrives in the next
# package under the call's own ID. Rendered only in native
# mode; the text path's prompt is byte-identical without it.
_NATIVE_CONTRACT = (
    "You are offered the tools in this package as native "
    "tool calls. A tool call is a proposal, not an action: "
    "it happens only if the framework accepts it and "
    "performs it. The outcome of every call — its result, "
    "or a refusal stating that nothing was dispatched — "
    "will be presented in your next package, under the "
    "call's own ID.")


def _render_prompt(package, native=False):
    """The wake prompt (Piece A3-CAT): the contract, the wake
    package as structured data, and — where the package
    carries a tool catalogue — the catalogue in its own
    section, its entries verbatim from the package. The
    adapter invents, renames and supplements nothing: the
    section's framing lines are the only words it adds. A
    package without a tools field (the seat-driver path)
    renders byte-identically to before. In native mode
    (the native adapter piece, N30) the contract also
    names the native arrangement, in the examined wording;
    the text path renders exactly as before."""
    contract = _CONTRACT
    if native:
        contract = _CONTRACT + "\n\n" + _NATIVE_CONTRACT
    tools = package.get("tools") if isinstance(package, dict) \
        else None
    if tools is None:
        return contract + "\n\nYour wake package:\n" + \
            json.dumps(package, indent=1, default=str)
    body = {key: value for key, value in package.items()
            if key != "tools"}
    return contract + "\n\nYour wake package:\n" + \
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
    DRIVER_FAILURE; it is never an outcome.

    Response-evidence piece: a failure may also carry the
    seam's response-evidence observation (`evidence`) —
    the response the failure arose from, where one was
    observed — so the loop can persist and disposition
    the very answer that failed, instead of recording a
    verdict over a discarded response."""

    def __init__(self, kind, detail=None, evidence=None):
        super().__init__(kind)
        self.kind = kind
        self.detail = detail
        self.evidence = evidence


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


def _native_parameters_schema(parameters):
    """The JSON Schema a native definition carries for a
    catalogue entry's list-form parameter metadata — the
    registry's one schema form: a list of declarations, each
    naming exactly a name, a required flag and a meaning.
    The translation is the metadata's own, field for field:
    one property per declared parameter, the declaration's
    meaning standing as the property's description, and the
    required declarations as the schema's required list, in
    declaration order. The metadata declares no
    machine-readable parameter types, so no property asserts
    one: a parameter's form stands in its meaning's words,
    exactly as the catalogue's own text rendering presents
    it, and the doorway's ceiling check — not this schema —
    enforces the shape. A declaration that is not a
    well-formed name/required/meaning mapping contributes
    nothing: definition construction stays total over its
    input, and a malformed schema is the translation
    boundary's refusal, not the offer's to repair."""
    properties = {}
    required = []
    for declaration in parameters:
        if not isinstance(declaration, dict):
            continue
        name = declaration.get("name")
        if not isinstance(name, str) or not name \
                or name in properties:
            continue
        prop = {}
        meaning = declaration.get("meaning")
        if isinstance(meaning, str) and meaning:
            prop["description"] = meaning
        properties[name] = prop
        if declaration.get("required") is True:
            required.append(name)
    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


class OpenAICompatibleAdapter:
    """Callable with the driver's boundary signature:
    adapter(package) -> typed outcome (or raises AdapterFailure).
    Also the onboarding identity call: adapter.identify()."""

    def __init__(self, endpoint=DEFAULT_ENDPOINT, model=None,
                 api_key=None, api_key_env="NVIDIA_API_KEY",
                 timeout=120.0, mode="text",
                 disable_tool_validation=True, route=None):
        if mode not in ("text", "native"):
            raise ValueError(
                f"adapter mode {mode!r} is not a mode; the "
                f"modes are text and native (probe scope §6)")
        self.endpoint = endpoint
        self.model = model
        # The assembly's route, as the driver that
        # assembled it recorded it (the value the run's
        # ASSEMBLY_PROBED act carries) — a provider field
        # of this adapter's configuration, supplied by
        # that driver. The adapter never infers a route
        # from the model name string. Its one consequence
        # is the Nemotron name translation (Ben's ruling,
        # 2026-11-24; framework.nemotron_names): on the
        # NVIDIA route the offered definitions carry the
        # route's wire names and extraction translates an
        # emitted wire name back; on every other route —
        # and where no route was supplied — nothing is
        # translated and the definitions and extraction
        # are exactly as they have always been.
        self.route = route
        self._active_name_translator = None
        self._api_key = api_key
        self._api_key_env = api_key_env
        self.timeout = timeout
        # BD-1 (native adapter piece): a native-mode
        # request carries Groq's disable_tool_validation
        # flag in this state — enabled by default, so an
        # unoffered call is delivered to the framework's
        # own resolver rather than refused at the provider.
        # The flag is a request-construction property of
        # native mode. The loop reads this attribute ONCE
        # per iteration — a snapshot — records the snapshot
        # in the iteration's commitment (the LOOP_ITERATION
        # event), and stages the same snapshot back through
        # stage_disable_tool_validation for the call's
        # construction (build-examination correction,
        # INDEX 403): the committed state and the
        # transmitted state are the one snapshot value,
        # never two reads of this mutable attribute. A
        # caller that stages nothing stands under this
        # attribute's settled state, as before. Disabled,
        # the field is omitted from the request — the
        # provider's default condition the P1 probe
        # measured.
        self.disable_tool_validation = \
            bool(disable_tool_validation)
        self._pending_disable_tool_validation = None
        self._staged_disable_tool_validation = None
        # The interface mode (probe scope §6): the constructor
        # value is the default only — a call under a sealed
        # package's judged mode passes that mode per call, and
        # the per-call value governs. Text is the historical
        # default: an adapter constructed as before behaves
        # exactly as before.
        self.mode = mode
        self._contribution_counter = 0
        # Timing evidence (INDEX 217/219): the prompt-
        # rendering seconds of the most recent __call__, or
        # None where no package was rendered (identify()).
        self.last_render_s = None
        # Response-evidence piece: the seam observation of
        # the most recent __call__ — the captured response
        # (or the seam's failure facts where none was
        # observed), with the adapter's verdict recorded
        # into it — published for the loop's evidence
        # sequence, and attached to any AdapterFailure the
        # call raises. None where the call's seam supplied
        # no observation (a replaced _call that captures
        # nothing).
        self.last_response_evidence = None
        self._last_evidence = None
        self._exchange_status = None

    # ----------------------------------------------------- deadline
    def _begin_deadline(self, budget=None, deadline=None):
        """Open the operation's TOTAL deadline (A6): one
        absolute point on a monotonic clock covering transport,
        response AND the adapter's own handling, through the
        final outcome. Begun by every public operation. The
        point's authority is settled by INDEX 219 as corrected
        by INDEX 222, in this order:

        - A supplied ABSOLUTE deadline (a monotonic instant
          propagated from the framework — the activation's own
          deadline, doorway-derived) is used VERBATIM: no
          now + anything. The adapter enforces the framework's
          deadline; it does not reconstruct one, so the
          transport cancellation boundary derived from this
          point is the activation deadline itself, never that
          point drifted forward by a sampling-to-establishment
          interval.
        - Otherwise a supplied activation budget (Piece A3,
          R49/R51) governs EXCLUSIVELY — the effective deadline
          is now + budget and the configured timeout plays no
          part, so no shorter per-call span can be reintroduced
          over a worker call.
        - A call carrying neither (identify(), the
          pre-activation calls) keeps the finite fence,
          now + the configured timeout."""
        if deadline is not None:
            self._deadline = deadline
        elif budget is not None:
            self._deadline = time.monotonic() + budget
        else:
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
    def _run_transport(self, fn):
        """Run one blocking transport function on the daemon
        worker thread under the operation's total deadline,
        with the calling thread's active termination on expiry
        (see _call). Returns fn's value; re-raises its failure."""
        deadline = getattr(self, "_deadline", None) or \
            self._begin_deadline()
        self._active_conn = None
        box = {}

        def work():
            try:
                box["value"] = fn(deadline)
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
        return self._run_transport(
            lambda deadline: self._dispatch(messages, deadline))

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

    def _exchange(self, payload_obj, deadline):
        """The raw HTTP exchange (runs on the transport worker
        thread) over the owned connection: request, header
        acquisition, and the body read via read1 with the
        socket timeout reset to the current remaining time
        before every read -- a provider drip-feeding inside
        each socket window cannot hold the read loop open --
        and the read path FAILS CLOSED: no unbounded fallback,
        no silently ignored inability to bound a read. Phases
        outside the read loop (connect, headers) are bounded
        by the calling thread's active termination at the
        deadline (see _call). Returns (status, raw body text)
        for ANY status — interpreting the status is the
        caller's; the probe capture needs the error body this
        exchange now reads whole."""

        def remaining():
            left = deadline - time.monotonic()
            if left <= 0:
                raise AdapterFailure(
                    "no_response", detail="total deadline exceeded")
            return left

        self._exchange_status = None
        key = self._api_key or os.environ.get(self._api_key_env)
        payload = json.dumps(payload_obj).encode("utf-8")
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
            status = resp.status
            # Response-evidence piece: from here a response
            # object exists at this seam — the phase fact
            # the evidence synthesis in __call__ reads when
            # a later phase of the exchange fails.
            self._exchange_status = status
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
        return status, raw

    def _dispatch(self, messages, deadline):
        """The blocking transport itself (runs on _call's
        worker thread): one chat-completions call and its
        interpretation — an HTTP error is a provider_error, an
        unusable body malformed. In native mode (A8) the
        request additionally offers the pending tool
        definitions the caller staged, and the full response
        message is retained on the instance for the caller's
        translation step: content is ABSENT (not empty) when a
        native response carries tool calls instead, and only
        a response with neither is malformed."""
        payload = {"model": self.model, "messages": messages,
                   "temperature": 0.2}
        tools = getattr(self, "_pending_tools", None)
        if tools:
            payload["tools"] = tools
        # BD-1: the flag the caller staged for this call,
        # carried in the request body exactly in the staged
        # state — present and true where enabled; omitted
        # where disabled (the provider's default condition).
        if getattr(self, "_pending_disable_tool_validation",
                   None):
            payload["disable_tool_validation"] = True
        status, raw = self._exchange(payload, deadline)
        # Response-evidence piece: the seam's capture of
        # this response, taken before any interpretation —
        # the response text this transport received (the
        # built-in exchange decodes the body as UTF-8; the
        # capture's provenance names that seam honestly),
        # retained whole whatever the interpretation below
        # concludes, HTTP errors included.
        self._last_evidence = {
            "provenance": "adapter_builtin_text",
            "capture_representation":
                "the response text the built-in exchange "
                "received (its body decoded as UTF-8), "
                "base64 of its UTF-8 bytes in L1",
            "http_status": status,
            "l1_bytes": raw.encode("utf-8"),
            "body_complete": True,
            "stop_reason": "eof",
            "read_error_kind": None,
            "phase": {"phase": "response_received",
                      "error_kind": None,
                      "http_status": status},
            "seam": {"failure_class": None,
                     "diagnostic": None, "helper_exit": None,
                     "stderr": None, "stdout_bytes": None,
                     "stdout_sha256": None,
                     "termination_confirmed": None,
                     "fence": None},
            "provider_model_id": None,
            "content": None,
        }
        if status >= 400:
            raise AdapterFailure(
                "provider_error", detail=f"HTTP {status}")
        try:
            parsed = json.loads(raw)
        except ValueError:
            raise AdapterFailure("malformed_response",
                                 detail="provider body is not JSON")
        if not isinstance(parsed, dict):
            raise AdapterFailure("malformed_response",
                                 detail="provider body is not an object")
        provider_model_id = parsed.get("model")
        try:
            message = parsed["choices"][0]["message"]
        except (KeyError, IndexError, TypeError):
            raise AdapterFailure("malformed_response",
                                 detail="no message content in "
                                        "provider response")
        if not isinstance(message, dict):
            raise AdapterFailure("malformed_response",
                                 detail="no message content in "
                                        "provider response")
        self._last_message = message
        content = message.get("content")
        if self._last_evidence is not None:
            self._last_evidence["provider_model_id"] = \
                provider_model_id
            self._last_evidence["content"] = content
        if content is None and not message.get("tool_calls"):
            raise AdapterFailure("malformed_response",
                                 detail="no message content in "
                                        "provider response")
        return content, provider_model_id

    # --------------------------------------------------------- probe
    def probe_raw_call(self, request):
        """The probe stage's raw call (probe scope §2/§8): one
        generation of the request exactly as given, returned
        as a raw capture BELOW this module's response
        interpretation — the provider body as received on
        success, the exact error body on an HTTP error, the
        HTTP status, response metadata, and the transport's
        own failure as the capture's diagnostic object when no
        provider response stands. Nothing here parses outcomes
        or classifies; the probe stage does that over what
        this returns. The call runs under the configured
        timeout fence, like identify(): the probe is a
        pre-activation assembly act and no activation clock
        exists for it."""
        self._begin_deadline()
        payload = dict(request)
        if payload.get("model") is None:
            payload["model"] = self.model
        try:
            status, raw = self._run_transport(
                lambda deadline: self._exchange(payload, deadline))
        except AdapterFailure as failure:
            return {"http_status": None, "body": None,
                    "error_body": None,
                    "diagnostics": f"{failure.kind}: "
                                   f"{failure.detail}",
                    "metadata": {}}
        metadata = {}
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            for key in ("id", "model"):
                if parsed.get(key) is not None:
                    metadata[key] = parsed[key]
        return {"http_status": status,
                "body": raw if status < 400 else None,
                "error_body": raw if status >= 400 else None,
                "diagnostics": None,
                "metadata": metadata}

    def stage_disable_tool_validation(self, value):
        """Stage the disable_tool_validation state the
        next call is to carry (BD-1): the loop hands the
        iteration's snapshot — the very value its
        commitment records — and the next call's request
        construction consumes exactly that value, never a
        fresh read of this instance's mutable attribute.
        The stage is consumed by the one call: a later
        call that stages nothing stands under the
        constructor's settled state. Staging None stages
        nothing."""
        self._staged_disable_tool_validation = \
            None if value is None else bool(value)

    # --------------------------------------------------------- wake
    def __call__(self, package, budget=None, deadline=None,
                 mode=None):
        """One bounded call, with the response-evidence
        piece's capture wrapped around it: the seam's
        observation of the call — the captured response
        and the adapter's verdict over it — is finalised
        onto `last_response_evidence` and attached to any
        AdapterFailure the call raises, so the loop's
        evidence sequence can persist and disposition the
        very answer the call worked on. The typed outcome
        and the failure kinds are exactly _call_typed's;
        the wrapper interprets nothing."""
        self.last_response_evidence = None
        self._last_evidence = None
        self._exchange_status = None
        try:
            result = self._call_typed(
                package, budget=budget, deadline=deadline,
                mode=mode)
        except AdapterFailure as failure:
            evidence = failure.evidence or \
                self._finalise_evidence(failure=failure)
            if evidence is not None:
                self.last_response_evidence = evidence
                if failure.evidence is None:
                    failure.evidence = evidence
            raise
        evidence = self._finalise_evidence(result=result)
        if evidence is not None:
            self.last_response_evidence = evidence
        return result

    def _finalise_evidence(self, result=None, failure=None):
        """Record the adapter's verdict into the seam's
        observation of this call and return it (response-
        evidence piece; the verdict total per R3-3). The
        seam is _dispatch's capture where the built-in
        transport ran; where the exchange itself failed
        before any capture, the observation is synthesised
        from what this seam established — a status the
        exchange observed, a pre-response connection
        failure it raised, a deadline expiry. Where a
        replaced _call supplied no observation at all,
        None stands: no evidence is fabricated for a seam
        that captured nothing."""
        seam = self._last_evidence
        if seam is None:
            # A replaced _call's own capture (the connector
            # transports): the verdict is recorded into the
            # transport's seam, exactly as into the built-in
            # one's — the seam differs, the discipline does
            # not.
            seam = self.last_response_evidence
        if seam is None:
            if failure is None:
                return None
            if failure.kind == "no_response":
                seam = {
                    "provenance": "adapter_builtin_text",
                    "http_status": None, "l1_bytes": None,
                    "body_complete": None, "stop_reason": None,
                    "read_error_kind": None,
                    "phase": {"phase": None,
                              "error_kind": None,
                              "http_status": None},
                    "seam": {"failure_class":
                             "timeout_after_send",
                             "diagnostic": failure.detail,
                             "helper_exit": None,
                             "stderr": None,
                             "stdout_bytes": None,
                             "stdout_sha256": None,
                             "termination_confirmed":
                                 getattr(self,
                                         "_worker_terminated",
                                         None),
                             "fence": "adapter_deadline"},
                    "provider_model_id": None, "content": None}
            elif self._exchange_status is not None:
                # A response object existed; the exchange
                # failed after it. The status is a fact;
                # the body is unestablished at this seam.
                seam = {
                    "provenance": "adapter_builtin_text",
                    "http_status": self._exchange_status,
                    "l1_bytes": None, "body_complete": None,
                    "stop_reason": None, "read_error_kind": None,
                    "phase": {"phase": "response_received",
                              "error_kind": None,
                              "http_status":
                                  self._exchange_status},
                    "seam": {"failure_class":
                             "transport_internal_error",
                             "diagnostic":
                                 f"{failure.kind}: "
                                 f"{failure.detail}",
                             "helper_exit": None,
                             "stderr": None,
                             "stdout_bytes": None,
                             "stdout_sha256": None,
                             "termination_confirmed": None,
                             "fence": None},
                    "provider_model_id": None, "content": None}
            elif failure.kind == "provider_error":
                # The exchange raised before any response
                # object existed at this seam — its own
                # pre-response observation, error kind the
                # exception's name _exchange recorded.
                seam = {
                    "provenance": "adapter_builtin_text",
                    "http_status": None, "l1_bytes": None,
                    "body_complete": None, "stop_reason": None,
                    "read_error_kind": None,
                    "phase": {"phase": "pre_response",
                              "error_kind": failure.detail,
                              "http_status": None},
                    "seam": {"failure_class": None,
                             "diagnostic": failure.detail,
                             "helper_exit": None,
                             "stderr": None,
                             "stdout_bytes": None,
                             "stdout_sha256": None,
                             "termination_confirmed": None,
                             "fence": None},
                    "provider_model_id": None, "content": None}
            else:
                return None
        content = seam.get("content")
        content_hash = None
        if isinstance(content, str):
            content_hash = hashlib.sha256(
                content.encode("utf-8")).hexdigest()
        if failure is not None:
            if failure.kind == "malformed_response":
                verdict = {"state": "failure",
                           "kind": failure.kind,
                           "detail": failure.detail,
                           "content_hash": content_hash,
                           "reason": None}
            elif failure.kind == "provider_error" and \
                    seam.get("http_status") is not None:
                verdict = {"state": "not_reached",
                           "kind": None, "detail": None,
                           "content_hash": None,
                           "reason": f"provider HTTP error "
                                     f"{seam['http_status']}"}
            else:
                verdict = {"state": "not_reached",
                           "kind": None, "detail": None,
                           "content_hash": None,
                           "reason": f"interpretation could "
                                     f"not begin: "
                                     f"{failure.kind}: "
                                     f"{failure.detail}"}
        else:
            verdict = {"state": "outcome",
                       "kind": result.get("outcome")
                       if isinstance(result, dict) else None,
                       "detail": None,
                       "content_hash": content_hash,
                       "reason": None}
        seam["adapter_verdict"] = verdict
        return seam

    def _call_typed(self, package, budget=None, deadline=None,
                    mode=None):
        """One bounded call. budget (Piece A3, R49/R51) is the
        activation's remaining budget in seconds, supplied by
        the caller as a call parameter — it never enters the
        prompt the model sees. A budget-carrying call is
        governed exclusively by that budget (INDEX 219): the
        remaining activation deadline is its one clock and
        the configured timeout plays no part. A call that
        cannot begin within budget does not begin at all.

        deadline (INDEX 222) is the activation's ABSOLUTE
        deadline — a monotonic instant propagated from the
        framework alongside the budget. Where it is supplied
        it is the call's deadline verbatim (see
        _begin_deadline): the budget keeps its
        response-acceptance role, but the cancellation
        boundary follows the original point, not a
        reconstruction from the sampled budget. A supplied
        deadline already in the past refuses before any
        provider call, exactly as an exhausted budget does.

        mode (probe scope §6) is the interface mode for this
        call — under a probe-governed assembly the loop passes
        the mode sealed in the packed package; absent, the
        constructor's mode stands, which defaults to text, the
        historical behaviour. In native mode the request
        offers the tool definitions derived from the package's
        catalogue, carries BD-1's flag in its staged state,
        and a native tool_calls response is extracted per
        call into the native_calls outcome (A9) for the
        loop's classification and dispatch; the prompt also
        carries the examined native contract wording (N30).
        A response without tool calls is read on the text
        path exactly as before."""
        # BD-1: the staged flag snapshot is consumed by
        # this call, whatever its outcome — a stage never
        # leaks into a later call.
        staged_flag = self._staged_disable_tool_validation
        self._staged_disable_tool_validation = None
        effective_mode = self.mode if mode is None else mode
        if effective_mode not in ("text", "native"):
            raise AdapterFailure(
                "malformed_response",
                detail=f"adapter mode {effective_mode!r} is "
                       f"not a mode; the modes are text and "
                       f"native")
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
        if deadline is not None:
            if isinstance(deadline, bool) or \
                    not isinstance(deadline, (int, float)):
                raise AdapterFailure(
                    "malformed_response",
                    detail="the supplied deadline is not a "
                           "number")
            if deadline <= time.monotonic():
                raise AdapterFailure(
                    "no_response",
                    detail="the activation deadline has "
                           "passed; the call cannot begin")
        self._begin_deadline(budget, deadline)
        self.last_render_s = None
        self._last_message = None
        self._active_name_translator = None
        render_started = time.monotonic()
        prompt = _render_prompt(
            package, native=effective_mode == "native")
        self.last_render_s = time.monotonic() - render_started
        # Native mode stages its offered definitions for the
        # one call: _dispatch reads them from the instance so
        # the _call(messages) seam — the seam the connector
        # transports replace — keeps its exact shape. A
        # transport that does not stage definitions simply
        # makes the text offer, and the response is read on
        # the text path. BD-1's flag is staged the same way:
        # the state this construction carries for the call is
        # the snapshot staged for it — the value the
        # iteration's commitment records — and only where
        # nothing was staged, the constructor's settled
        # state (build-examination correction, INDEX 403).
        self._pending_tools = None
        self._pending_disable_tool_validation = None
        if effective_mode == "native":
            # The route's name translator for this call,
            # built over the package's own offered names:
            # on the NVIDIA route the definitions carry
            # the wire names, and the same translator
            # stands stashed for the extraction of this
            # call's response. Off that route it is None
            # and nothing in this call is translated.
            translator = _nemotron_names.translator_for_package(
                self.route, package)
            self._active_name_translator = translator
            definitions = self._native_tool_definitions(
                package, translator=translator)
            if definitions:
                self._pending_tools = definitions
            self._pending_disable_tool_validation = \
                self.disable_tool_validation \
                if staged_flag is None else staged_flag
        try:
            content, _provider_model = self._call([
                {"role": "system",
                 "content": "You are a seat in a recorded "
                            "collaborative run. Answer exactly as "
                            "the contract specifies."},
                {"role": "user", "content": prompt}])
        finally:
            self._pending_tools = None
            self._pending_disable_tool_validation = None
        if effective_mode == "native":
            message = getattr(self, "_last_message", None)
            calls = message.get("tool_calls") \
                if isinstance(message, dict) else None
            if calls:
                if isinstance(content, str) and content.strip():
                    raise AdapterFailure(
                        "malformed_response",
                        detail="the native response carries "
                               "both content and tool calls; "
                               "the channels are not mixed")
                records = self._extract_tool_calls(calls)
                self._check_deadline()
                return {"outcome": "native_calls",
                        "native_calls": records}
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
    def _native_tool_definitions(package, translator=None):
        """The native tool definitions for a package (A8):
        derived from the package's own tool catalogue — the
        same per-grant derivation the loop renders as text —
        one definition per tool name (the catalogue may carry
        a tool once per grant; a native offer names it once —
        the doorway still adjudicates per grant). Name,
        description and parameters are the catalogue's own;
        the adapter invents, renames and supplements nothing.
        A dictionary-form parameters value is the catalogue's
        own schema and stands exactly as it stands; the
        registry's list-form metadata is translated by
        _native_parameters_schema, field for field; anything
        else carries the empty object schema, as before.

        Where a name translator stands (the NVIDIA route's,
        Ben's ruling 2026-11-24), a definition's name is the
        name's wire form — the one renaming this derivation
        performs, at the route's boundary, of the name
        alone: description and parameters remain the
        catalogue's own, and the framework's name for the
        tool is unchanged everywhere else. Without a
        translator the definitions are exactly as they have
        always been."""
        tools = package.get("tools") \
            if isinstance(package, dict) else None
        definitions = []
        seen = set()
        for entry in tools or []:
            if not isinstance(entry, dict):
                continue
            # The catalogue's own field for the tool's name
            # is `tool` (Piece A3-CAT's entry shape).
            name = entry.get("tool") or entry.get("name")
            if not isinstance(name, str) or not name \
                    or name in seen:
                continue
            seen.add(name)
            description = entry.get("description")
            parameters = entry.get("parameters")
            if isinstance(parameters, dict):
                schema = parameters
            elif isinstance(parameters, list):
                schema = _native_parameters_schema(parameters)
            else:
                schema = {"type": "object", "properties": {}}
            wire = translator.to_wire(name) \
                if translator is not None else None
            definitions.append({"type": "function", "function": {
                "name": wire if wire is not None else name,
                "description": description
                if isinstance(description, str) else "",
                "parameters": schema}})
        return definitions

    def _extract_tool_calls(self, calls):
        """Extract a native response's tool_calls, one record
        per call in emitted order (native adapter piece,
        N6/N13 — build brief B1): the provider call ID
        exactly as emitted, the name, the arguments, and the
        call's provider ordinal. The arguments arrive as a
        JSON string (the measured native envelope) or as an
        object; both forms are accepted (N40). Extraction
        is STRUCTURAL ONLY (build-examination correction,
        INDEX 406): it parses nothing — a string stands raw
        under the form "string", an object under "object",
        any other shape under "non_object". Whether a
        string parses, and into what, is classification's
        determination, made in the loop only for a call
        that survives call-ID integrity and the cap;
        extraction claims neither. A defect inside one
        call — an absent or unreadable name, an arguments
        value in a shape classification must refuse — is
        carried in that call's own record (its
        arguments_form names the delivered shape) for the
        loop to refuse per call; it no longer fails the
        response.
        Defects of the response as a whole still fail whole:
        a tool_calls value that is not a non-empty list, or
        an entry that is not an object — a structure from
        which per-call extraction cannot begin at all (N13's
        boundary). Extraction classifies nothing and permits
        nothing: resolution, validation, the translation
        record and dispatch are the loop's corridor. The one
        transformation extraction performs is the route's
        name translation (Ben's ruling, 2026-11-24): where
        the call's translator stands, an emitted wire name
        is carried back to its canonical name and the wire
        name kept beside it in the record — a renaming at
        the route's boundary, deciding nothing about the
        call."""
        if not isinstance(calls, list) or not calls:
            raise AdapterFailure(
                "malformed_response",
                detail="native tool calls are a non-empty list")
        records = []
        for ordinal, call in enumerate(calls, start=1):
            if not isinstance(call, dict):
                raise AdapterFailure(
                    "malformed_response",
                    detail="a native tool call is not an object")
            call_id = call.get("id")
            if not isinstance(call_id, str) or not call_id:
                call_id = None
            function = call.get("function")
            if not isinstance(function, dict):
                function = {}
            name = function.get("name")
            if not isinstance(name, str) or not name:
                name = None
            arguments = function.get("arguments")
            if isinstance(arguments, str):
                form, value = "string", arguments
            elif isinstance(arguments, dict):
                form, value = "object", arguments
            else:
                form, value = "non_object", arguments
            record = {
                "provider_ordinal": ordinal,
                "provider_call_id": call_id,
                "name": name,
                "arguments_form": form,
                "arguments": value}
            # The route's name translation, inbound (the
            # NVIDIA route's translator, Ben's ruling
            # 2026-11-24): an emitted name that is a wire
            # form in the translator's map is translated
            # back to its canonical name here, before
            # classification, and the record carries the
            # emitted wire name beside it — both names
            # visible downstream. An emitted name that is
            # not in the map is NOT guessed back: it stands
            # exactly as emitted, for classification's
            # closed-world catalogue determination to
            # refuse like any unknown tool. Off the route
            # no translator stands and nothing here runs.
            translator = self._active_name_translator
            if translator is not None and name is not None:
                wire_canonical = translator.to_canonical(name)
                if wire_canonical is not None:
                    record["wire_name"] = name
                    record["name"] = wire_canonical
            records.append(record)
        return records

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
        self.last_render_s = None
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
