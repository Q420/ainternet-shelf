# NATIVE-MODE PROBE — SCOPE (2026-11-23)

**Status:** Draft Rev 1, for Vane's examination. Developed under her INDEX 270
recommendation and Ben's INDEX 267/269 direction. A bounded addition to Piece
A1's assembly lifecycle; A1 is not reopened wholesale. No implementation and
no worker attempt are implied by this scope.

## 1. Purpose and place

The probe is a recorded stage of assembly, sitting **after per-instance
onboarding** (the model's identity declaration stands recorded, so probe
evidence is attributable) and **before assembly judgement and packing**. It
establishes, for one generated instance, **observed interaction behaviour
under specified conditions** — nothing else. It is not a work assignment, not
an authority grant, and not an opportunity to exercise real tools. Its output
is probe evidence, bound into the assembly record, which the examiner weighs
at judgement; the evidence informs the adapter-mode decision and never makes
it automatically.

## 2. The probe environment

- A **synthetic probe case**, explicitly identified as such in its own text:
  a trivial toy task ("report the toy object's colour") whose answer needs
  one call against the probe catalogue or one structured text reply.
- A **small, fixed catalogue of harmless test tools**, offered **natively**
  (provider tool definitions) and described in the text contract at once, so
  either channel is genuinely available: `probe.lookup` (a canned toy
  lookup) and `probe.note` (a canned toy note). Both are **non-executing**:
  no performer exists for them anywhere in the framework; a call to either
  can only ever be captured.
- **No real filesystem, shell, network (beyond the provider call itself),
  credentials, shelf access, or external side effects.** The probe prompt
  carries no case material, no sources, and no grants.
- A **capture boundary**: for every trial, the raw provider response is
  retained whole — content, native tool calls with their arguments, and
  provider errors with their bodies (the INDEX 262 correction makes the
  last of these available). **No captured call is dispatched, executed, or
  answered.** A call is observed, not obeyed.

## 3. The trial set — "native-probe-v1"

Consistency claims require repetition, so the stage runs a **versioned
suite**: **5 trials** of the identical probe request (same prompt, same
offered definitions, same parameters: temperature 0.2, the run's pinned
model and route), each bounded (one call; the adapter's ordinary deadline
discipline). The suite definition — prompt text, tool definitions,
parameters, classification rules — is a named, versioned artifact
(`native-probe-v1`); any change to it is a new version, and **results are
never inherited across a change of model, provider route, or probe
version**.

Each trial is classified into exactly one outcome class:

- `text_contract` — the response is the framework's structured text object
  (a contribution, or text-form tool requests naming probe tools);
- `native_catalogue` — the response carries native tool call(s) naming
  offered probe tools, and the provider accepted the generation;
- `environment_tool_attempt` — the response reaches for a capability that
  was **not offered** (e.g. `container.exec`), whether the provider
  delivers it or refuses it (attempt 8's shape: the provider's
  `tool_use_failed` refusal is recorded with the attempt);
- `mixed` — more than one of the above in a single response;
- `malformed` — a response in neither contract, or with unparseable
  arguments;
- `refusal` — the model declines the probe task;
- `provider_failure` — the boundary delivered no generation (HTTP error,
  timeout, disconnect), the provider's reason retained where available.

The stage reports **counts per class over the 5 trials** (N of M), never a
single blended verdict. Requested vs provider-accepted is preserved per
trial: a native call the provider refused is an attempt with a provider
refusal attached, not an accepted call; **actual execution is not a
possible probe outcome**.

## 4. Evidence and the record

A new recorded act in the assembly lifecycle, **ASSEMBLY_PROBED**, recorded
by the office after onboarding and before judgement, carrying: the instance
and assembly ids; the seat and role; the **provider route and pinned model
identifier**; the **probe suite name and version** and a canonical hash of
its definition; the offered tool definitions; per-trial outcome classes
with the raw responses retained in full (subject to the record's ordinary
diagnostic bound, with hashes of the untruncated originals); the per-class
counts; and a **recommended adapter mode** (§5) marked as recommendation,
not decision. The sealed assembly record binds the probe evidence's hash,
so packing seals it with everything else. The **independent checker**
verifies: the probe act stands in sequence (after onboarding, before
judgement); the counts recompute from the per-trial classes; the sealed
record's adapter mode corresponds to the judgement act, not merely to the
recommendation; and a governed assembly (one whose case will run the loop)
carries probe evidence whose configuration fingerprint matches its own
provider, model and probe version — stale or foreign evidence is a
divergence.

## 5. Adapter modes and their derivation

Two modes: **`text`** (the existing contract, unchanged) and **`native`**
(the catalogue offered as provider tool definitions; §6). The
recommendation derives from the counts by a fixed rule: a class holding a
**majority of settled trials** (text_contract → `text`; native_catalogue →
`native`) recommends that mode; environment attempts, mixed, malformed,
refusal and provider-failure trials recommend nothing by themselves — they
stand as evidence for the examiner's weighing (a model that reaches for a
shell in the probe is a fact judgement may act on; it is never, by itself, a
reason to grant anything). **No majority → no recommendation** (recorded as
inconclusive). The examiner's judgement act records the assembly's mode;
absent or inconclusive probe evidence, a governed assembly **fails
closed**: it may not be packed with a permissive default — judgement must
either record a mode on stated grounds or the assembly does not proceed.

## 6. The in-work native path (translation boundary)

Where the sealed mode is `native`, the adapter builds the request's tool
definitions **from the same per-grant catalogue the loop derives** (the
INDEX 258 derivation — the offered set is the sealed grants, nothing else)
and parses native tool calls in the response into **the same typed
tool_requests outcome the loop already consumes**. Translation happens
entirely inside the adapter, before the doorway: from the doorway onward —
grant and bounds adjudication (including the retrieval aggregate), recorded
dispatch, execution, recorded outcome — **nothing differs from the text
path**. Malformed native arguments fail closed as a malformed response.
A native call naming a tool outside the offered catalogue is translated
like any other request and **refused at the doorway as ungranted, recorded,
without execution** — this is the scope's negative acceptance case (§8).
Where the sealed mode is `text`, requests and parsing are byte-identical
to today.

## 7. Freshness and failure discipline

Probe evidence is bound to a configuration fingerprint (provider route,
pinned model identifier, probe version, offered definitions). Any change
to a component invalidates the evidence for mode purposes: a governed
assembly whose fingerprint does not match its own configuration is treated
as unprobed — fail closed (§5). Probe-stage provider failures classify the
affected trials; they never fabricate a mode.

## 8. Witnesses the build must carry

P1. The probe runs pre-activation against a synthetic case; no real tool
    exists to execute; captured calls dispatch nothing (record proof).
P2. Each outcome class is produced and classified distinctly, including an
    environment-tool attempt in attempt 8's exact shape (a provider
    `tool_use_failed` refusal with the attempt preserved).
P3. Five bounded trials reproduce the suite; counts recompute; the
    classification of a scripted mixed response is `mixed`.
P4. The evidence binds to the assembly: sequence, fingerprints, hashes;
    the checker accepts a sound record and diverges on stale evidence,
    foreign evidence, and count tampering.
P5. Mode derivation: majority text → text; majority native → native; no
    majority → inconclusive, and an inconclusive governed assembly cannot
    be packed (fail closed).
P6. In-work native path: a native call to a granted tool dispatches
    through the doorway identically to its text-form twin (same events,
    same bounds), in a governed retrieval assembly.
P7. **Negative acceptance case:** a native call to an ungranted tool
    during work is refused at the doorway, recorded, and executes nothing.
P8. The text path is byte-identical for text-mode assemblies (the full
    existing battery at its counts: A1 69, A2 80, A3 88, A3-CAT 37,
    retrieval 56 + evidence 41, checker 35, transports 55 + 55).

## 9. Non-goals

No execution service and no new work tools; no environment capability is
granted, designed, or implied; no change to grants, bounds, the doorway, or
the checker beyond §4's correspondence; no worker attempt is authorised by
this piece — the first governed run under a probed mode is a separate
release decision for Vane and Ben.
