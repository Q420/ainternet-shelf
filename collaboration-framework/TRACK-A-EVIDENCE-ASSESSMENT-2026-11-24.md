# Track A — evidence assessment: what the existing record already answers (2026-11-24)

An offline audit under Ben's correction carried by Vane (INDEX 430,
`VANE-EVIDENCE-BEFORE-EXPERIMENTS-2026-11-24.md`): examine the existing
evidence before commissioning another experiment. Every claim below
carries its evidence class and its conditions. **All behavioural
observations are the one pinned model, `openai/gpt-oss-120b`, on the
Groq route, unless a line says otherwise** — nothing here is silently
generalised past its conditions. No provider request was made for this
assessment; no code was changed.

## 1. Established — what the worker has demonstrably done

**E1. The execution reach: name `container.exec`, arguments `{cmd:
[string, …]}`, no other fields.** Twice preserved whole, under two
different configurations. Attempt 8 (`live-demo/first-worker-attempt8/
run-export.json`, LOOP_STALLED detail; INDEX 265): text mode, no tools
offered, provider HTTP 400 `tool_use_failed` — "Tool choice is none, but
model called a tool" — with `failed_generation` a single object
`{name: "container.exec", arguments: {cmd: [...]}}` whose `cmd` is an
array of three strings: a shell name (`bash`), a login-shell flag
(`-lc`), and one string invoking Python reading a program from a heredoc
(the program's content is not reproduced here; its form is a short test
program). Evidenced1 phase 2 (`live-demo/first-worker-evidenced1/
responses/iteration-18.json`, 275 L1 bytes; INDEX 329–330): text mode
again, the identical form — same name, same three-element cmd-array
shape, same heredoc structure. In both generations the arguments object
carried **`cmd` and nothing else** — no session, workdir, timeout, env,
or user field was ever supplied.

**E2. With tools offered natively, it calls the offered tools, in the
standard form.** Native-offer probes (`live-demo/native-offer-offer1/
probe-evidence.json`, `native-offer-paced1/probe-evidence.json`;
INDEX 339, 352–353): the full derived catalogue offered (hash
`4020a870…`), no `tool_choice` field, flag absent. Delivered trials: 6 of
6 produced a single offered call — `sandbox.list` with arguments
`{"path": "sources/stock-take.md"}` — each a standard `tool_calls` entry
(provider call ID `fc_…`, `type: "function"`, arguments a JSON string),
verified from the raw provider bodies.

**E3. Its preferred read tool is `sandbox.read`, chosen over the offered
`read_range`.** P1 (`live-demo/native-probe-p1-p1run1/`; INDEX 366–367):
offered set narrowed to `sandbox.list` + `sandbox.search`, the listing
pre-presented. All 10 trials reached for `sandbox.read` — a real registry
tool that was **not** in `request.tools` — with exactly apt arguments
(`{"path": "sources/stock-take.md"}`). P2 (`native-probe-p2-p2run1/`):
offered set `sandbox.list` + `sandbox.search` + `sandbox.read_range`;
the 4 delivered observations reached for `sandbox.read` again, refused.
So across 14 observations the whole-file read was preferred and
`read_range` was never chosen — under these constructions, where reading
the named source in full was the natural next step.

**E4. The flag's delivery effect, measured.** P1's pair differed in
exactly `disable_tool_validation` (INDEX 366): flag absent → 5/5
responses refused wholesale (HTTP 400), the attempt preserved in
`failed_generation`; flag transmitted `true` → 5/5 unoffered calls
**delivered** to the host as standard `tool_calls` entries with provider
call IDs and parseable arguments. Delivery to the host is established;
nothing about doorway adjudication follows from it (INDEX 367).

**E5. The commentary shape: a channel-named call carrying the
text-contract payload.** Native1 iteration 2 (`live-demo/
first-worker-native1/responses/iteration-26.json`; INDEX 416–417): the
`failed_generation` is `{name: "commentary", arguments: {outcome:
"tool_requests", requests: [ …five retrieval requests… ]}}` — one
provider-reported call whose arguments are the framework's own
text-contract object, not five native calls. The same hybrid shape
appears in the INDEX 274 hand-run artifact (`live-demo/
native-probe-empirical-2026-11-23.json`, trials 3–4: provider failures
whose retained error text carries the commentary attempt) and in the
phase-1 probe classifications of probed1 (trial 4) and evidenced1
(trial 2) as `environment_tool_attempt × provider_refused`.

**E6. It continues after a tool result carried back in the framework's
package form.** Native1 (INDEX 416–417; `run-export.json` events 18–25):
iteration 1's `sandbox.list` call was dispatched; its outcome — a result
object `{path, content, content_bytes, content_sha256, authority_path,
size_bytes, line_count}` whose content was 110 bytes of listing metadata
— was carried into iteration 2's request inside the package as a
`tool_results` entry bearing the provider call ID beside the request and
dispatch IDs (the framework's package-mediated carriage, **not** a
provider `role: "tool"` message; construction at `src/framework/loop.py`
§tool_results, examined for INDEX 419's memo). The model produced a next
response that continued the assignment coherently — its five requests
were listings of the remaining sources — visible in iteration 2's
`failed_generation` (E5). The provider refused that response on the
unoffered-name ground, so the continuation is established as a
*generation*, not as a delivered turn. One observation, not a rate.

**E7. Conditions correction (INDEX 419–420), applied throughout this
assessment:** native1's `disable_tool_validation` was committed in the
record and staged in the adapter but **never transmitted** — the live
harness transport does not carry the flag. Native1's iteration-2 refusal
is therefore a flag-absent observation, exactly comparable to P1's OFF
condition, and establishes nothing about provider behaviour with the
flag actually on the wire.

## 2. Supported by documentation — what the specifications say

From the existing research (`NATIVE-TOOL-USE-RESEARCH-2026-11-24.md`,
INDEX 343; sources verified live on 2026-11-24). Documentation class
throughout: it specifies interfaces; it does not demonstrate this
worker's behaviour.

**D1. The Harmony format** (OpenAI's specification for gpt-oss): a tool
call is a commentary-channel message addressed to `functions.<name>`
ending in the call stop token, body = JSON arguments; **results return
as a `tool`-role message from the tool to the assistant**, and prior
reasoning is passed back in the tool-calling case. The format presumes
the act→observe→act loop.

**D2. `container.exec` is a documented tool — in ChatGPT's environment,
not in gpt-oss's documented set.** The elicited GPT-5.2 Thinking tool
list (Willison, Jan 2026) gives `container.exec({ cmd: string[],
session_name?, workdir?, timeout?, env?, user? })` — "Run a command
inside the container and return stdout/stderr" — in a `container`
namespace alongside session-oriented siblings. Two things follow at
documentation level: the documented argument form (**`cmd` as an array
of strings**, the remaining fields optional) converges with the model's
own demonstrated generation form (E1); and the documented result is
described only in prose — **return stdout/stderr** — with no
machine-readable result schema specified. Gpt-oss's documented built-ins
are `browser` and `python` only; no source states gpt-oss was trained
with a `container` namespace (the name's provenance for this checkpoint
is inference, flagged as such in the research).

**D3. Groq's documented semantics.** `disable_tool_validation=true`
returns called tools without validating their presence in
`request.tools`; `tool_choice=none/required` enforcement is **not**
relaxed by it. Groq validates generated tool-call objects and returns
HTTP 400 with `failed_generation` (code `tool_use_failed`) when
validation fails. The documented host pattern (Groq's own examples, and
the OpenAI-compatible convention generally): the host executes and
returns the result as a tool message **under the call's ID** — the
provider-side carriage form for a result is the `role: "tool"` message
keyed by `tool_call_id`, its content the tool's output.

## 3. Unresolved — what neither evidence nor documentation answers

**U1. Whether a call to an offered `container.exec` definition is
delivered.** Every preserved `container.exec` generation (E1, ×2)
occurred with **no tools offered at all**; the provider refused on the
tool-choice-none ground. No observation in the record offers an
execution tool — under that name or any other — so delivery under offer
is unobserved. Supporting-but-not-decisive evidence exists: dotted,
host-defined names (`sandbox.*`) deliver cleanly when offered (E2), and
an unoffered registry-sibling name was delivered when validation was
disabled (E4). Neither is the proposed condition: a host-defined
definition carrying the very name from the model's own environment
priors.

**U2. The execution result form — what the model expects back after an
exec call.** No execution has ever occurred in this programme, so no
exec result has ever been returned or consumed: zero observations.
Documentation (D2) specifies the result only as prose — return
stdout/stderr — for a different product's environment; it does not
specify field structure (stdout/stderr as separate fields or one
stream; an exit-code field; truncation marking), nor whether the model
expects the session continuity the documented optional `session_name`
implies. E6 establishes consumption of a *retrieval* result in the
*framework's package carriage*, once; it says nothing about an exec
result's content shape, and nothing about consumption of a provider
`role: "tool"` result (D3's form), which this framework has never sent
in any run or probe.

**U3. Multi-call and next-action behaviour after an exec result.**
All delivered calls in the record are single calls. What the model
invokes *after* an execution result — the observation Track A's Stage 2
sought for Track C's stock evidence — has no exec-specific instance;
E6's continuation followed a listing result, not an execution.

## 4. Design consequence — what actually waits on the unresolved points

**The interface's name and argument form can be closed now.** Track A's
Stage 1 asked what name the model answers to and which representation
it uses. The record answers both without another probe: the model's own
generations, twice preserved under different configurations, used
`container.exec` with `{cmd: string[]}` and no further fields (E1), and
the documented signature for that name independently specifies the same
form (D2). The probe's ARRAY-vs-STRING comparison would have spent
requests re-asking a question the worker has already answered twice —
the STRING condition tested whether it adapts to our withdrawn
assumption, which Ben's direction expressly retires. **Design decision
taken from evidence:** offer the tool under the name `container.exec`,
arguments an object whose `cmd` is an array of strings, the documented
optional fields not required. No design decision waits on U1's answer
for the *form*; U1 bears only on delivery, below.

**U1 (delivery under offer) does not block designing the room.** The
room's architecture — walls, stocking, record, checker, doorway
translation — is independent of the offered tool's name. U1 touches
exactly one interface-section line: whether the offered definition can
carry the name `container.exec` or must carry a framework name with the
model's reach translated. If the name failed under offer, the first
demonstration would record a refused first response and the name would
change; nothing else in the design moves. That is a demonstration-time
discovery with a bounded cost, not a design blocker — and it is the
*only* point in this audit where a small live confirmation would settle
something the record cannot. Whether even that is worth any requests
before the demonstration is the examiner's call; the Track A proposal
as written (16 requests, two stages) is not needed to reach it.

**U2 (exec result form) does not block designing the room.** The
executor's side is fully designable from the framework's own side:
capture stdout, stderr, and exit status, bounded, with truncation
marked — the documented "return stdout/stderr" (D2) read together with
an exit status is the only form the documentation supports, and the
carriage is already demonstrated: results travel in the package's
`tool_results` under the provider call ID, and the model continued
coherently after exactly that carriage once (E6). What the record
cannot settle is whether the model consumes a particular exec-result
*object layout* as fluently as it consumed the listing result — a
behavioural unknown whose resolution would change a field layout in the
carriage, not the room's design. It is properly discovered at the first
demonstration, inside the claim fence, not probed in advance: a Stage-2
style simulated-result probe would in any case only have tested our own
candidate fixture (the proposal's stated limitation), which is the
assumption-shaped evidence Ben's correction retires.

**U3 does not block design.** The loop's existing machinery (translation
record, per-call classification, CAP) already specifies how multi-call
responses are handled; the room design adopts it unchanged. The
next-action-after-exec evidence Track C wanted arrives with the first
demonstration's record, where it is real evidence rather than a
simulated fixture's.

**The commission's closing question, answered directly:** the existing
material **is sufficient** to close Track A's interface questions for
design purposes. The name, the argument representation, the absence of
further fields, the carriage mechanism, and the result's documented
content are all established or documentation-supported above. **One
residual uncertainty remains, stated precisely:** whether Groq delivers
a well-formed native call when `container.exec` is offered as a
host-defined tool definition (U1) — unresolvable from the record
because every preserved generation of that name occurred with no tools
offered, and the two neighbouring conditions (offered dotted names;
unoffered name with validation disabled) each differ from it in one
variable. The single design decision it touches is the offered tool's
name in the interface section. It does not block the room's design, and
no other Track A question survives the audit.
