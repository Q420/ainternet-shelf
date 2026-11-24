# OFFLINE EXAMINATION — why the provider refused the 'commentary' call in native1 (2026-11-24)

Commissioned by Vane's result examination (INDEX 417), offline only: no
provider requests, no rerun, no code changes. The question, verbatim:
*"Why did the provider reject the commentary call despite BD-1 being
committed true, when P1 delivered an unoffered sandbox.read call under the
same flag?"*

Read first-hand for this memo: the result examination (INDEX 417); the
captured artifacts `live-demo/first-worker-native1/responses/iteration-18.json`
and `iteration-26.json`; the P1 evidence
(`live-demo/native-probe-p1-p1run1/probe-evidence.json`); the INDEX 274 raw
artifact (`live-demo/native-probe-empirical-2026-11-23.json`); the
assembly-probe records inside the probed1 and evidenced1 run exports;
`src/framework/adapter.py`; `src/framework/probe.py`;
`live-demo/groq_connector_transport.py`; `live-demo/first_worker_run.py`
(install sites); the adapter suite's stub construction
(`tests/unit/test_piece_native_adapter.py`); INDEX entries 274, 343,
366–367. Findings are labelled by class throughout: **PROVEN** (retained
evidence or source read first-hand), **CONSISTENT** (a reading the evidence
supports but does not compel), **UNKNOWN**.

---

## PART A — PROVEN

**A1. The refused generation's exact shape (retained, iteration-26.json).**
HTTP 400, `code: tool_use_failed`, `type: invalid_request_error`, message:
*"attempted to call tool 'commentary' which was not in request.tools."* The
preserved `failed_generation` is a single object:
`{"name": "commentary", "arguments": {…}}` whose arguments are an **object**
(not a JSON string) holding the loop's text-contract payload verbatim in
form: `"outcome": "tool_requests"` plus a `"requests"` list of five —
`sandbox.list` on `sources/a3-pass.md`, `sandbox.list` on
`sources/index-tail.md`, `sandbox.read` on all three sources. One
provider-reported call named `commentary` carrying a text-contract payload;
no `tool_calls` entry, no provider call ID, no dispatch. (Her finding 2,
verified.)

**A2. The accepted iteration-1 call's shape (retained, iteration-18.json).**
HTTP 200. A standard native `tool_calls` entry: `id fc_5f4344e5…`,
`type: "function"`, `function.name: "sandbox.list"` (an **offered** tool),
`function.arguments` a **JSON string** (`{"path":"sources/stock-take.md"}`).

**A3. P1's delivered unoffered call's shape (retained, P1 evidence).**
In all five ON trials the delivered call is the same standard form as A2:
a `message.tool_calls` entry with a provider call ID (trial 6:
`fc_8304a48e…`), `type: "function"`, name `sandbox.read` — a real registry
tool, unoffered in that construction — and arguments as a JSON string
(`{"path":"sources/stock-take.md"}`), HTTP 200, `finish_reason:
tool_calls`. The P1 pair was verified at build (INDEX 359) to differ in
exactly one field, `disable_tool_validation` — so in the ON condition the
flag was **in the transmitted body by construction**. In the OFF condition
the identical attempt was refused (HTTP 400) with the attempt preserved in
`failed_generation` under the name `sandbox.read`.

**A4. Every earlier 'commentary' observation has the same shape — and none
carried the flag.** Retained artifacts, three independent occasions:
- **INDEX 274, hand-run trials 3–4** (raw artifact retained): refused,
  `failed_generation` = `{"name":"commentary","arguments":{"tool_requests":
  [probe.lookup …]}}`. The artifact contains **no** `disable_tool_validation`
  anywhere — the flag did not exist in that construction.
- **Assembly-probe trials** (probed1 trial 4; evidenced1 trial 2; provider
  bodies retained inside both run exports, byte-identical, 396 B,
  sha256 `b4e723cd…`): refused with the identical error text;
  `failed_generation` = `{"name":"commentary","arguments":
  {"outcome":"tool_requests","tool_requests":[probe.lookup …]}}`.
  `src/framework/probe.py` contains no `disable_tool_validation` at all —
  its constructions offer `probe.lookup` with `tool_choice: "default"` (or
  no tool_choice) and **no flag**.
- **native1 iteration 2** (A1): the inner list key is `"requests"` where
  the probe constructions' payloads use `"tool_requests"` — the payload
  inside the commentary call tracks whichever text contract the
  construction in force presented. The constant across all occasions is
  the shape: **the model's text-contract answer emitted as the arguments
  of a call named `commentary`** — a channel name from the model's own
  Harmony format (INDEX 274, 343), never a `tool_calls` entry.

**A5. The flag was committed and staged — and the live transport never
transmitted it.** This is the load-bearing source finding, both paths read
first-hand:
- The loop snapshots the flag per iteration and stages it into the adapter
  (INDEX 405); both native1 iteration commitments record
  `disable_tool_validation: true` (her finding 3).
- The adapter's **built-in** call construction honours the staging:
  `adapter.py` builds its payload with `tools` from `_pending_tools` and
  adds `payload["disable_tool_validation"] = True` when
  `_pending_disable_tool_validation` is staged.
- But the connector transports **replace** that call seam. The harness
  installed `install_groq_connector_transport` for this run
  (`first_worker_run.py`), whose single request construction
  (`connector_call` in `live-demo/groq_connector_transport.py`) builds
  `{model, messages, temperature}` and adds **only** the staged `tools`
  and a staged `tool_choice`. A full-file search finds **zero occurrences
  of `disable` in the transport** — it never reads
  `_pending_disable_tool_validation` and never puts the flag in the body.
  The Groq helper likewise adds nothing; it sends the body it is given.
- Therefore, on the construction evidence, **neither native1 request
  carried `disable_tool_validation` on the wire.** Iteration 1 succeeded
  because `sandbox.list` was offered — validation passes offered calls
  with or without the flag. Iteration 2's unoffered `commentary` attempt
  met the provider's validation **enabled, at its default**, and was
  refused wholesale — the identical outcome to every flag-absent
  commentary observation in A4 and to P1's OFF condition in A3.

**A6. The BD-1 witnesses never exercised the live path.** The adapter
suite's flag witnesses capture bodies at a local stub HTTP endpoint that
the adapter's **built-in** `_exchange` posts to — the path in A5 that
*does* carry the flag. No witness in the record captures a body built by
the Groq connector transport with the flag present, and none could: the
transport source contains no reference to it. The binding proved at
INDEX 405 (record → staging → built-in construction) is real; its last
hop, staging → transmitted body through the connector transport, was
never built and never witnessed. (The same check-shape as the INDEX 400
NVIDIA miss: the check cited did not exercise the path claimed.)

**A7. The framework's refusal-side part is nil; its construction-side
part is A5 plus the follow-up package.** The refusal happened before
translation, adjudication, or dispatch (her finding 2): the framework
refused nothing and bypassed nothing. What the framework contributed to
iteration 2's request, construction-derived: a follow-up package
presenting dispatch-1's `sandbox.list` result in the package's text form,
the catalogue re-offered (iteration 2's commitment carries the same
catalogue hash `4020a870…`), the flag staged true (A5). Nothing in that
construction names or invites `commentary`.

## PART B — CONSISTENT (supported, not compelled)

**B1.** Groq's validation, when enabled, refuses a generation whose call
names a tool outside `request.tools` **wholesale** — offered-ness is the
only question it asks; it does not distinguish a well-formed function name
(`sandbox.read`, P1-OFF) from a channel name (`commentary`, A4/A1). Every
retained refusal under enabled validation has this shape, and the
provider's own error text states the criterion in so many words.

**B2.** The model's commentary emission is a **per-generation variation**,
not a position effect: it appears in first responses (INDEX 274 trials
3–4; both assembly-probe occasions) and in a follow-up after a tool result
(native1 iteration 2), under text, probe, and native constructions alike;
the same model in the same native1 run produced a clean native call at
iteration 1. This matches INDEX 274's standing finding (genuinely
bilingual, varies per generation) and INDEX 343's (the reach is a
documented failure mode of the format, not a registry lookup).

**B3.** Had the flag been transmitted, the documented provider behaviour
(INDEX 343: `disable_tool_validation=true` returns unvalidated calls and
does not override `tool_choice`; no tool_choice was staged here) makes
delivery of the commentary generation **plausible** — the host's resolver
would then have refused the unknown name at translation as a recorded
decision. Plausible is all it is: see C1.

## PART C — UNKNOWN

**C1. Whether a transmitted flag would have delivered *this* shape.** P1
proves delivery of a well-formed **function call** (a `tool_calls` entry
with an ID and JSON-string arguments) under the flag. The commentary
generation is a different output shape — it exists only inside
`failed_generation` as `{name, arguments-object}` and never stood as a
`tool_calls` entry in any retained observation. Whether Groq's
validation bypass covers channel-name emissions reported this way, or
only function-call validation, **no retained observation decides**. The
flag's documented scope is "tool validation"; the commentary emission may
or may not be inside it.

**C2.** Why the model chose the commentary channel at iteration 2 of
native1 specifically (after a successful native exchange) — per-generation
variation (B2) is a description, not a cause; nothing retained measures
the trigger.

**C3.** The exact bytes of the outbound second request — see the
retention answer below. Every statement in this memo about that request
(A5, A7) is **construction-derived** from the adapter staging, the
transport source, and the sealed catalogue hash — except one provider-side
corroboration retained in the response artifact itself: the error's
*"which was not in request.tools"* establishes that a `tools` field stood
on the request and did not contain `commentary`.

## THE RETENTION ANSWER, EXPLICITLY

**The exact outbound second request was not retained anywhere.** The
evidence regime (response-evidence piece, Rev 8) preserves provider
*responses* whole; no request body stands in the run directory, the
report, or the export — those carry the iteration commitments (including
the flag state), the catalogue hash, timings, and the response artifacts.
Nothing in this memo reconstructs the request as though it were captured;
A5 is a source-level proof about the construction path the harness
installed, labelled as such.

## THE THREE LOCI, DISTINGUISHED

- **Provider validation behaviour:** enabled validation refused an
  unoffered name wholesale (B1). In native1 it was enabled **because the
  flag never reached it** (A5) — the provider behaved exactly as it does
  in every flag-absent observation. No provider anomaly is evidenced.
- **Model output shape:** the commentary hybrid — a text-contract payload
  emitted as a call to the model's own commentary channel (A4, B2). A
  real and recurring shape, and the reason the attempt existed at all;
  under a delivered flag it would have been the resolver's recorded
  refusal, not a stall (B3, subject to C1).
- **Framework translation:** no part in the refusal (it preceded
  translation). The framework's part is upstream, in **carriage**: the
  BD-1 binding stopped at the adapter's staging because the connector
  transport that replaced the call seam does not carry the flag (A5),
  and the witnesses that certified the binding exercised the built-in
  path instead (A6).

## THE STRONGEST STATEMENT THE EVIDENCE SUPPORTS

**The two "flag-on" cases were not both flag-on at the provider.** P1's
ON condition transmitted `disable_tool_validation=true` in the body by
construction, and the provider delivered a well-formed unoffered function
call. In native1 the flag was committed in the record and staged in the
adapter, but the Groq connector transport — the seam that built the
transmitted body — does not carry it, so the provider validated iteration
2's generation at its default and refused the unoffered `commentary`
attempt exactly as it has refused every commentary attempt ever observed,
all of which were flag-absent. **Confidence class: PROVEN as to the
construction and the transport omission (source read first-hand, live
path identified); the causal step — that the provider therefore validated
with the flag off — is the only reading the retained evidence supports,
there being no retained outbound body to inspect (C3).** The residual
question the evidence cannot decide is C1: whether a transmitted flag
would have delivered a *commentary-shaped* generation, as distinct from
the well-formed function call P1 delivered. The observation that would
decide it is a future one — a native request with the flag **verifiably
on the wire** (captured at the transport seam, not inferred from a
commitment) that elicits a commentary emission, whose delivery or refusal
would settle the flag's scope over channel-name calls. It is named here
as future evidence only; this examination commissions nothing, and the
release is spent.
