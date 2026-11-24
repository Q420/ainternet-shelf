# NATIVE-MODE PROBE — SCOPE (2026-11-23)

**Status:** Draft **Rev 5**, for Vane's examination. Rev 5 incorporates
the final correction of her Rev 4 examination (INDEX 281): §7's sequence
corrected to A1's established lifecycle (the probe stands after
ASSEMBLY_GENERATED, before ASSEMBLY_VERIFIED), verified against
`generator.py`'s own stated order, and the checker's aggregate duty made
a recomputation of the per-trial sum (§4). Rev 4 incorporated the two
consistency corrections of her Rev 3 examination (INDEX 279); Rev 3, the
two of her Rev 2 examination (INDEX 277); Rev 2, the seven of her Rev 1
examination (INDEX 272). Developed under her
INDEX 270 recommendation and Ben's INDEX 267/269 direction. A bounded
addition to Piece A1's assembly lifecycle; A1 is not reopened wholesale. No
implementation and no worker attempt are implied by this scope.

**Changes in Rev 2:** (1) the capture boundary is placed **below** response
interpretation (§2); (2) trial outcomes are recorded in **two dimensions**
— behaviour observed × delivery status — replacing the single outcome
class (§3); (3) a **quorum** governs mode recommendation (§3, §5); (4)
probe evidence, integrity evidence and presentation are distinguished,
under an explicit **capture ceiling** with an **incomplete** classification
(§4); (5) judgement records the selected mode **and its grounds**, and the
mode is bound into the sealed assembly object the adapter consumes (§5);
(6) two witnesses added — native≡text equivalence and **translation
integrity** (§8, P9–P10); (7) the stage's predecessor and successor events
are named against A1's lifecycle, and the configuration fingerprint is
extended to request parameters and tool-choice configuration (§7).

## 1. Purpose and place

The probe is a recorded stage of assembly, sitting **after per-instance
onboarding** (the model's identity declaration stands recorded, so probe
evidence is attributable) and **before assembly judgement and packing**. It
establishes, for one generated instance, **observed interaction behaviour
under specified conditions** — nothing else. It is not a work assignment,
not an authority grant, and not an opportunity to exercise real tools. Its
output is probe evidence, bound into the assembly record, which the
examiner weighs at judgement; the evidence informs the adapter-mode
decision and never makes it automatically.

## 2. The probe environment and the observation boundary

- A **synthetic probe case**, explicitly identified as such in its own
  text: a trivial toy task ("report the toy object's colour") whose answer
  needs one call against the probe catalogue or one structured text reply.
- A **small, fixed catalogue of harmless test tools**, offered **natively**
  (provider tool definitions) and described in the text contract at once,
  so either channel is genuinely available: `probe.lookup` (a canned toy
  lookup) and `probe.note` (a canned toy note). Both are **non-executing**:
  no performer exists for them anywhere in the framework; a call to either
  can only ever be captured.
- **No real filesystem, shell, network (beyond the provider call itself),
  credentials, shelf access, or external side effects.** The probe prompt
  carries no case material, no sources, and no grants.
- **The observation boundary sits below response interpretation.** The
  probe captures the provider's response **at the transport/response
  level, before the adapter's text-contract parsing or validation can
  reject, transform, or discard anything**. A native call must never be
  classified malformed merely because the text parser does not understand
  it. The capture preserves, per trial: the raw response content; native
  tool-call names and arguments as delivered; provider refusal and error
  details (with error bodies, per the INDEX 262 correction); **provider
  acceptance or rejection, recorded separately from the model's attempted
  behaviour**; and the response's identity and integrity information (§4).
- **One generation is observed, then the trial ends.** The probe never
  sends tool results back, never continues a native tool conversation, and
  never answers a captured call. **No captured call is dispatched or
  executed.** A call is observed, not obeyed.

## 3. The trial set — "native-probe-v1"; two evidence dimensions

Consistency claims require repetition, so the stage runs a **versioned
suite**: **5 trials** of the identical probe request (same prompt, same
offered definitions, same parameters: temperature 0.2, tool-choice left at
the provider default, the run's pinned model and route), each bounded (one
call; the adapter's ordinary deadline discipline). The suite definition —
prompt text, tool definitions, parameters, classification rules — is a
named, versioned artifact (`native-probe-v1`); any change to it is a new
version, and **results are never inherited across a change of model,
provider route, or probe version** (§7).

Each trial is recorded in **two dimensions**, neither discarded:

**Behaviour observed** — what the model attempted:
- `text_contract` — the framework's structured text object (a
  contribution, or text-form tool requests naming probe tools);
- `native_catalogue` — native tool call(s) naming **offered** probe tools;
- `environment_tool_attempt` — a reach for a capability that was **not
  offered** (e.g. `container.exec`), whether or not the provider delivers
  it;
- `mixed` — more than one of the above in a single generation;
- `malformed` — a generation in neither contract, or with unparseable
  arguments;
- `refusal` — the model declines the probe task;
- `no_observable_behaviour` — no generation from which behaviour can be
  read.

**Delivery status** — what the provider did with the generation:
- `provider_accepted` — the generation was delivered to the framework;
- `provider_refused` — the provider rejected the generation and supplied
  evidence of the attempt in its refusal (attempt 8's exact shape:
  behaviour `environment_tool_attempt` × delivery `provider_refused`);
- `provider_failed` — no generation and no attributable attempted call
  (HTTP error, timeout, disconnect), the provider's reason retained where
  available;
- `indeterminate` — the response is unavailable or its status cannot be
  determined.

**Behavioural detail — `payload_form`.** Alongside the two dimensions,
each trial may carry a named detail attribute where the generation's
payload has a recognisable form the dimensions alone would flatten. The
first such value, from the INDEX 274 measurement: **`text_contract_json`**
— a native call to an unoffered tool (there, `commentary`, a channel name
from the model's own response format) **whose arguments are the
framework's text-contract JSON**. This is **not** a third dimension, not a
new behaviour class, and not `mixed` (the model delivered one call, not
two responses): the trial's governing classification stands in the two
dimensions (there, `environment_tool_attempt` × `provider_refused`), and
`payload_form` preserves the compatibility signal — the adapter may one
day need to recognise exactly this shape, neither a clean native request
nor a clean text response. For such a trial the evidence preserves the
native call name, the exact arguments, the embedded text-contract payload,
the provider refusal and its reason, and the fact that no generation
reached the framework as an accepted response.

The stage reports **counts per class in each dimension** over the 5
trials, never a single blended verdict, and the examiner sees the complete
distribution. **What the model attempted, what the provider accepted, and
what the framework executed are three different facts**; in the probe, the
third is always *nothing executed*, by construction.

**Settled trials and the quorum.** A trial is **settled** when its
behaviour dimension is classifiable from captured evidence — including a
provider-refused attempt whose refusal carries the attempt (attempt 8's
trial is settled; a bare provider failure is not). A mode recommendation
requires **at least 3 settled trials** and a **strict majority of the
settled trials** in one behaviour class that carries a mode (§5);
otherwise the stage's result is **inconclusive**.

## 4. Evidence: probe, integrity, presentation

Three distinct things, never conflated:

- **Probe evidence:** the complete raw response as captured at the
  observation boundary, including native arguments and the provider error
  body where available — retained under the capture ceiling defined
  below: **a per-trial aggregate of 64,000 bytes across the retained
  content objects** (the provider body and the diagnostic output
  together). **Hashes and the HTTP status/metadata are accounted
  separately, outside that byte budget.** Completeness is judged **per
  object**: a trial's evidence is incomplete if its provider body is
  incomplete, whatever the state of its diagnostics — a complete
  diagnostic object never evidences a complete provider capture.
- **Integrity evidence:** a SHA-256 hash over the exact captured bytes,
  recorded per trial.
- **Presentation:** any shortened rendering used in reports or the viewer,
  labelled as a rendering; presentation is never evidence.

**Retained evidence objects.** What the capture retains is distinguished
by kind, and the kinds are never conflated (the INDEX 274 artifact is the
motivating case: its refusal trials' retained text is the helper's
traceback, which *contains* the provider's error body but is not itself
the raw HTTP response body): (a) the **provider response body as
received** — for an accepted generation, the response body; for a
refusal, the **exact provider error body as captured**; (b) the **HTTP
status and relevant response metadata**; (c) **transport/helper
diagnostic output**, including any traceback, retained as its own object
and labelled as diagnostics; (d) a **SHA-256 hash of each retained
object**, recorded separately per object. A wrapper's diagnostic
rendering is never labelled, hashed, or presented as the provider's raw
response.

If a response exceeds the capture ceiling, the record states that fact
explicitly, retains the available bounded bytes (whose hash is then the
integrity evidence for *those* bytes), and classifies that trial's
evidence as **incomplete** — an incomplete capture is never labelled a
complete raw response. The capture ceiling is a named constant of the
suite, and the checker verifies it (§4, checker duties below).

A new recorded act in the assembly lifecycle, **ASSEMBLY_PROBED**,
recorded by the office at its sequence point (§7), carrying: the instance
and assembly ids; the seat and role; the **provider route and pinned model
identifier**; the **probe suite name and version** and a canonical hash of
its definition; the offered tool definitions; per trial — behaviour class,
delivery status, any `payload_form` detail, settled flag,
evidence-completeness flag, and the retained evidence objects of the
paragraph above, each with its own integrity hash (the captured bytes
themselves retained in the record, subject to the ceiling above); the per-dimension counts; the settled
count; and a **recommended adapter mode** (§5) marked as recommendation,
not decision. The sealed assembly record binds the probe evidence's hash,
so packing seals it with everything else. The **independent checker**
verifies: the probe act stands in its named sequence (§7); the counts
recompute from the per-trial records in both dimensions; the checker
**recomputes the sum of each trial's retained provider-body and
diagnostic bytes** and verifies it against the aggregate ceiling (not
merely each object's size independently), verifies the provider body's
own completeness status, and diverges on any trial whose retained total
exceeds the ceiling or whose completeness statements do not match the
objects retained; the sealed record's adapter
mode corresponds to the judgement act (§5), not merely to the
recommendation; and a governed assembly's probe evidence carries a
configuration fingerprint matching its own (§7) — stale or foreign
evidence is a divergence.

## 5. Adapter modes, derivation, and judgement

Two modes: **`text`** (the existing contract, unchanged) and **`native`**
(the catalogue offered as provider tool definitions; §6). The
recommendation derives from the settled trials by the fixed rule of §3:
a strict majority of settled trials in `text_contract` recommends `text`;
in `native_catalogue` recommends `native`; any other distribution —
including environment attempts holding a majority — recommends **none**
(recorded inconclusive). Environment attempts, mixed, malformed, refusal
and provider-failure trials recommend nothing by themselves in any case;
they stand as evidence for the examiner's weighing, and an environment
attempt is never, by itself, a reason to grant anything.

**Recommendation and judgement are different acts.** The recommendation
is automatic and exists only when the probe is conclusive; an
inconclusive probe produces **no recommendation**, and a recommendation
is never an authority in its own right. The **selection** of a mode is
the examiner's accountable decision, recorded in the judgement act with
its grounds. The examiner may disagree with a recommendation, but may not
silently substitute an unsupported mode: the grounds are part of the act.
**Despite inconclusive evidence, the examiner may still select a mode —
but only through that explicit, independently examinable judgement,
stating the basis for proceeding.** No selected mode, no recorded
grounds, or an unsupported selection means the governed assembly **cannot
be packed** — the fail-closed boundary is the absence of an accountable
judgement, never the probe's silence alone, and there is no permissive
default. **The selected mode is bound into the sealed assembly record —
the object the adapter actually consumes.** The adapter reads the mode
only from that sealed object; it must not be able to choose a mode from a
prompt, an environment variable, or an unverified model name.

## 6. The in-work native path (translation boundary)

Where the sealed mode is `native`, the adapter builds the request's tool
definitions **from the same per-grant catalogue the loop derives** (the
INDEX 258 derivation — the offered set is the sealed grants, nothing else)
and parses native tool calls in the response into **the same typed
tool_requests outcome the loop already consumes**. Translation happens
entirely inside the adapter, before the doorway: from the doorway onward —
grant and bounds adjudication (including the retrieval aggregate),
recorded dispatch, execution, recorded outcome — **nothing differs from
the text path**. **Translation is a trust boundary:** it preserves the
original request faithfully — tool name and arguments exactly as the
model emitted them are what the doorway adjudicates and the record
retains; translation must never quietly normalise an invalid request into
an authorised one. Malformed native arguments fail closed as a malformed
response. A native call naming a tool outside the offered catalogue is
translated like any other request and **refused at the doorway as
ungranted, recorded, without execution** — the scope's negative acceptance
case (§8, P7). Where the sealed mode is `text`, requests and parsing are
byte-identical to today.

## 7. Ordering and freshness

Against A1's existing lifecycle — whose normative order `generator.py`
itself states as ASSEMBLY_PROPOSED → instance onboarding →
ASSEMBLY_GENERATED → ASSEMBLY_VERIFIED → ASSEMBLY_JUDGED →
ASSEMBLY_PACKED → ASSEMBLY_ISSUE_AUTHORISED → INSTANCE_ACTIVATED — the
stage's exact sequence is:
**… instance onboarding recorded → ASSEMBLY_GENERATED → ASSEMBLY_PROBED →
ASSEMBLY_VERIFIED → ASSEMBLY_JUDGED → ASSEMBLY_PACKED →
ASSEMBLY_ISSUE_AUTHORISED → INSTANCE_ACTIVATED …** —
the probe requires the allocated instance and its attributable onboarding
to exist, and stands **after generation and before construction
verification**, hence before judgement, packing, issue authorisation and
activation; it moves no existing act from its established place. The
event-order witness and the checker enforce the ordering by these named
events in this exact sequence, not by inference.

Probe evidence is bound to a **configuration fingerprint** comprising:
provider route; pinned model identifier; probe suite version and its
canonical hash; the offered native tool definitions; the relevant request
parameters; and the tool-choice configuration. Any change to a component
invalidates the evidence for mode purposes: a governed assembly whose
fingerprint does not match its own configuration is treated as unprobed —
fail closed (§5). A new assembly never inherits a prior assembly's probe
evidence, whatever the displayed model name. Probe-stage provider failures
classify the affected trials; they never fabricate a mode.

## 8. Witnesses the build must carry

P1. The probe runs pre-activation against a synthetic case; no real tool
    exists to execute; captured calls dispatch nothing (record proof).
P2. The two dimensions are produced and classified distinctly, including
    an environment-tool attempt in attempt 8's exact shape (behaviour
    `environment_tool_attempt` × delivery `provider_refused`, the attempt
    preserved from the provider's refusal body).
P3. Five bounded trials reproduce the suite; counts in both dimensions
    recompute; a scripted mixed generation classifies `mixed`.
P4. The evidence binds to the assembly: sequence, fingerprints, hashes;
    the checker accepts a sound record and diverges on stale evidence,
    foreign evidence, count tampering, and an over-ceiling trial retained
    without an incomplete classification.
P5. Mode derivation and quorum: 3 settled + strict majority recommends;
    2 settled, or no strict majority, is inconclusive and produces **no
    recommendation**; an inconclusive governed assembly then packs
    **only** on an explicit examiner judgement recording the selected
    mode and its basis (the override branch, witnessed packing), and an
    attempted packing without such a judgement **fails** (the fail-closed
    branch, witnessed refused) — both branches are required witnesses;
    four provider failures + one text response recommends nothing.
P6. In-work native path: a native call to a granted tool dispatches
    through the doorway identically to its text-form twin (same events,
    same bounds), in a governed retrieval assembly.
P7. **Negative acceptance case:** a native call to an ungranted tool
    during work is refused at the doorway, recorded, and executes
    nothing.
P8. The text path is byte-identical for text-mode assemblies (the full
    existing battery at its counts: A1 69, A2 80, A3 88, A3-CAT 37,
    retrieval 56 + evidence 41, checker 35, transports 55 + 55).
P9. **Equivalence:** a native call to a granted tool and its text-form
    equivalent produce equivalent doorway requests and the same governed
    dispatch behaviour.
P10. **Translation integrity:** a native call with altered arguments, an
    ungranted tool name, or a tool absent from the sealed catalogue
    cannot expand authority through translation; the doorway adjudicates
    the request exactly as emitted, and the record retains it exactly.

**Build-stage precondition (INDEX 279).** Before the translation
implementation's assumptions are finalised, the build first captures and
examines the pinned route's actual native response envelope — the exact
response shape, tool-call identifiers, argument representation, and any
multi-call behaviour — and defines the translation contract against that
capture. The five INDEX 274 trials establish that the provider delivers
native calls for this model; they do not establish every shape the
adapter must parse. This is the empirical-first rule applied to the seam,
and it precedes the P6/P9/P10 implementation work it informs.

## 9. Non-goals

No execution service and no new work tools; no environment capability is
granted, designed, or implied; no change to grants, bounds, the doorway,
or the checker beyond §4's correspondence; no worker attempt is authorised
by this piece — the first governed run under a probed mode is a separate
release decision for Vane and Ben.
