# NEMOTRON ADAPTER DESIGN 01 — SUBJECT INTERFACE SPECIFICATION

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12; Alex adjudication pb-mwe90lo6)
**Stage:** 2 — Nemotron Adapter Design (Plan prerequisite #4, BLOCKING)
**Status:** DESIGN ONLY. No model calls are made or authorised by this
document. No code is built by this document (Stage 5). No shelf file
is modified by this document.
**Inputs:** Plan 01 (Stage 2 section; Alex §4 minimum evidence);
V2-QUALIFICATION-01 (esp. §2 model coupling, §5 declare-only
changes); PILOT-MANIFEST-01 (Stage 0 freeze);
`custom.nvidia` CONNECTOR.md and its helper
`~/workspace/custom-connectors/custom.nvidia/bin/nvidia_api.py`.

**What the adapter is.** The single, narrow bridge between the pilot
harness (Stage 3) and the hosted Nemotron subject, over Ben's NVIDIA
lane. It exists because of Qualification §2: in the V2 stack the
subject is welded into the runner (`MODEL = "qwen/qwen3.8-27b"`, a
Groq-connector shell-out, corpus and ground truth as module
constants). The pilot retires that coupling by giving the subject
exactly one boundary, specified here, through which every call and
every byte of evidence must pass.

---

## 1. SUBJECT IDENTITY PINNING

### 1.1 Candidates on the live catalogue (2026-11-12 listing)

The plan names the subject as **"Nemotron-3 Nano 30B (reasoning)"**.
The catalogue visible to Ben's key on 2026-11-12 listed three ids in
that family:

| Model id | Reading of the id |
|---|---|
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Nemotron-3 Nano Omni, 30B-A3B, reasoning variant |
| `nvidia/nemotron-nano-3-30b-a3b` | Nemotron Nano 3, 30B-A3B (no variant declared in the id) |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | Nemotron-3.5 "Lightning", 30B-A3B (a different, later minor line) |

### 1.2 The pin

- **Primary pin:** `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`.
  It is the only listed id whose served identity declares, in the id
  itself, the reasoning variant the plan names. The pilot's [MODEL]
  steps are specified (Qualification §5, item 5) against a reasoning
  subject consuming declared inputs; pinning an id that does not
  declare its reasoning behaviour would leave the subject's defining
  property to assumption.
- **Alternate 1 (declared, not automatic):**
  `nvidia/nemotron-nano-3-30b-a3b` — the text-native Nano 3, if the
  evidence in §1.3 shows the Omni variant is vision-first or lacks a
  plain text chat posture suited to the trees' text-only inputs.
- **Alternate 2 (declared, not automatic):**
  `nvidia/nemotron-3.5-lightning-30b-a3b` — a different minor line
  and therefore a different subject identity; usable only by re-pin.
- An alternate is **never** selected by the adapter or the harness
  at run time. Moving to an alternate is a re-pin: a dated amendment
  to this design and to the pilot manifest, with fresh catalogue
  evidence (§1.4), made before any call under the new pin.

### 1.3 Evidence that settles the choice — without making a call

No call can be made at this stage (Plan: Stage 6 gates all calls),
and none is needed to choose. The choice is settled by documentary
evidence, in this order:

1. **The build.nvidia.com model card for each candidate id** —
   modality (text-only vs multimodal), whether a reasoning mode
   exists and how it is controlled, context length, and whether the
   id is offered as a chat-completions endpoint at all.
2. **NVIDIA's published model documentation** for the Nemotron-3
   Nano family, where the card is thin — same questions as (1).
3. **The catalogue response itself** (`GET /v1/models` via the
   connector helper): the `owned_by` and id fields are the whole of
   what the API declares; they corroborate existence on this key,
   nothing more.

If (1)–(2) show the Omni id is a vision-language model whose text
path is a secondary posture, Alternate 1 becomes primary by
amendment. If they confirm a first-class text reasoning posture,
the primary pin stands. Either way the decision and its documentary
basis are recorded in the amendment trail before Stage 5.

**What documentary evidence cannot settle:** listed ≠ served. The
connector record already proves the gap
(`mistralai/mistral-7b-instruct-v0.3` was listed on this key and its
chat call returned 404). Served status of the pinned id is therefore
carried in this design as **PINNED-LISTED, SERVED-UNVERIFIED** until
the first authorised call (Stage 6). A 404 on that first call is an
adapter/infrastructure failure under §4, not a subject result, and
triggers the re-pin procedure — never a silent fall-through to an
alternate.

### 1.4 Catalogue churn and the life of the pin

NVIDIA's catalogue changes often (connector doc, verified
2026-11-12: 83 models that day; the doc instructs reading the live
list rather than trusting any snapshot). The pin therefore has three
parts, all required:

1. **The model id** (§1.2).
2. **Date-stamped catalogue evidence:** the full `GET /v1/models`
   response JSON, captured and sha256-hashed at (a) Stage 5 build
   freeze and (b) Stage 6 pre-flight. The pin is the pair
   *(model id, catalogue snapshot hash + capture date)*.
3. **Vanish behaviour:**
   - Id absent from the pre-flight catalogue → **the run does not
     start.** Subject identity is no longer evidenced; re-pin by
     amendment (new catalogue evidence, Alex notified) before any
     execution. This is the Stage 0 tripwire applied to the subject:
     a pin mismatch forces a re-freeze, never an improvisation.
   - Id present at pre-flight but the first call returns 404 →
     adapter/infrastructure failure (§4); execution halts; re-pin
     decision goes to Ben/Alex with the capture record as evidence.
   - Id present and serving, but a response reports a different
     served model id than the pin (§3, `response_model_id_served`)
     → adapter failure, identity mismatch; the call does not count
     as a call to the pinned subject.

---

## 2. REQUEST CONTRACT

### 2.1 The lane (as it exists)

All calls go through the `custom.nvidia` connector's sanctioned
path: `POST https://integrate.api.nvidia.com/v1/chat/completions`,
issued by the helper `nvidia_api.py chat MODEL` with the request
body as JSON. The body must name the same model as the helper
argument. Authentication is the connector's bearer credential,
attached by the dynamic-credentials surrogate mechanism; the
adapter never sees, holds, or records the key (see §3.4).
Redirects are refused by the helper. Helper timeout: 120 s.

### 2.2 What reaches the adapter: `step_inputs`

The harness (Stage 3) owns the trees. For each `[MODEL]` step it
constructs the **complete** messages array from the pinned tree
text and the step's declared inputs — and nothing else. It hands
the adapter one object:

```
step_inputs = {
  correlation_id : string   # opaque, harness-issued; recorded, never interpreted
  tree_id        : string   # e.g. "T05"
  step_id        : string   # e.g. "T05-STEP-06"
  messages       : [ { "role": ..., "content": ... }, ... ]   # final form
}
```

`messages` arrives **in final form**: the system message is the
tree's declared contract text for the step, verbatim from the
pinned trees; the user message is the step's declared inputs
(worksheets, extractions, boundary tables — Qualification §5 and
the V2 execution model: the subject never hunts raw sources for a
value it must copy), serialised by the harness in the harness's
declared canonical format. Serialisation is a harness concern;
whatever bytes it produces are what the adapter sends and captures.

### 2.3 What the adapter adds: the pinned envelope, and nothing else

The adapter wraps `messages` in a chat-completions body by adding
**only** the envelope fields fixed in its pinned configuration:

| Field | Pinned value | Rationale |
|---|---|---|
| `model` | The §1 pin, exactly | Subject identity; must equal the helper's MODEL argument. |
| `temperature` | `0` | Declared determinism control: minimises sampling variance so cross-call differences are evidence about the subject, not the sampler. It does **not** make a hosted model deterministic (§6) and is never represented as doing so. |
| `max_tokens` | `4096` | [MODEL] step outputs are small structured results; the cap is generous headroom against truncation while bounding runaway generation. One value for all steps in this design; a step needing more is a design amendment, not a per-call argument. |
| `stream` | `false` | One complete JSON response per call — the only form that can be captured canonically (§3). |
| Reasoning control | ON, by the single mechanism the pinned model's card documents (e.g. its declared reasoning/thinking parameter), set to its documented "on" value | The subject is pinned *as* a reasoning model; its deliberation is part of the behaviour under governance. Exactly one mechanism, pinned in configuration — never varied per call, never stacked. If the card documents no control, the model's default reasoning behaviour is the pin, and that fact is recorded in the configuration. |

Everything else is forbidden: **the adapter adds nothing of its
own to the prompt.** No adapter system prompt, no instruction
prefix or suffix, no reformatting, no trimming, no re-ordering of
messages, no per-call parameter variation. All sampling parameters
live in the pinned configuration; `complete()` accepts no parameter
arguments (§5), so the harness *cannot* vary them silently.
Configuration changes produce a new `adapter_config_sha256` (§3)
and are design amendments.

### 2.4 Wire form

The request body is encoded as UTF-8 JSON and sent byte-for-byte as
constructed. The exact byte sequence sent is the canonical request
(§3, `request_raw`); its sha256 is `request_sha256`. On a retry,
the resent body is **byte-identical** — same `request_sha256`
across attempts is a checkable invariant (§4.3).

---

## 3. CANONICAL CAPTURE — SCHEMA `ADAPTER-CAPTURE-01`

### 3.1 The record

Every call — successful, failed, retried — produces exactly one
capture record, written before the adapter returns to the harness.
A call that produces no record did not happen, for all pilot
purposes. **30 fields:**

| # | Field | Content |
|---|---|---|
| 1 | `capture_id` | UUID, issued by the adapter, one per `complete()` invocation |
| 2 | `schema` | `"ADAPTER-CAPTURE"` |
| 3 | `schema_version` | `1` |
| 4 | `recorded_at_utc` | When the record was written (ISO-8601, UTC) |
| 5 | `correlation_id` | Verbatim from `step_inputs`; opaque to the adapter |
| 6 | `tree_id` | Verbatim from `step_inputs` |
| 7 | `step_id` | Verbatim from `step_inputs` |
| 8 | `adapter_id` | Adapter implementation identity + version (pinned at Stage 5) |
| 9 | `adapter_config_sha256` | sha256 of the pinned configuration (model pin, envelope, retry policy) this call ran under |
| 10 | `subject_model_id_pinned` | The §1 model id |
| 11 | `subject_pin_catalogue_sha256` | sha256 of the catalogue snapshot evidencing the pin (§1.4) |
| 12 | `subject_pin_captured_date` | Date that catalogue evidence was captured |
| 13 | `endpoint` | `https://integrate.api.nvidia.com/v1/chat/completions` |
| 14 | `request_sent_at_utc` | Final attempt's send time |
| 15 | `request_raw` | The exact request body bytes, verbatim (JSON text) |
| 16 | `request_sha256` | sha256 of `request_raw` |
| 17 | `request_envelope` | Echo of the §2.3 envelope as sent (model, temperature, max_tokens, stream, reasoning setting) |
| 18 | `response_received_at_utc` | Final attempt's receipt time; `null` if no response |
| 19 | `response_latency_ms` | Receipt − send, final attempt; `null` if no response |
| 20 | `response_http_status` | Final attempt's HTTP status; `null` on transport failure before any status |
| 21 | `response_raw` | The exact response body bytes, verbatim; `null` if none |
| 22 | `response_sha256` | sha256 of `response_raw`; `null` if none |
| 23 | `response_model_id_served` | The response body's `model` field, verbatim; `null` if absent/no response |
| 24 | `response_finish_reason` | `choices[0].finish_reason`, verbatim; `null` if absent |
| 25 | `response_usage` | The response body's `usage` object, verbatim (prompt/completion/total tokens as served); `null` if absent |
| 26 | `attempts` | Array, one entry per attempt (§3.2) |
| 27 | `transport_outcome` | `RESPONSE_RECEIVED` \| `HTTP_ERROR` \| `TIMEOUT` \| `TRANSPORT_ERROR` \| `HELPER_ERROR` |
| 28 | `failure_class` | Adapter-determinable class (§4): `ADAPTER_FAILURE`, or `null` when a response was received (subject/governance classification is downstream, §4.1) |
| 29 | `failure_detail` | Human-readable failure description (exception class + message, helper stderr tail); `null` on success. Never contains credential material (§3.4) |
| 30 | `record_sha256` | sha256 of this record's canonical serialisation with this field omitted (§3.3) |

### 3.2 Attempts

`attempts[]` entries carry: `attempt_no`, `sent_at_utc`,
`received_at_utc`, `http_status`, `error_class`, `error_detail`.
A single-attempt call has exactly one entry. The top-level
request/response fields describe the **final** attempt; no attempt
is ever overwritten or dropped. A success after a retry is recorded
as a success **with `attempts` showing the retry** — retries are
never silent (§4.3).

Note on the current helper: on success it prints the parsed JSON;
on an HTTP error it raises (the status and error body surface as an
exception, not as returned JSON). The Stage 5 build must therefore
wrap the helper invocation (or implement the identical call through
the same credential mechanism) so that status, raw error body,
timing and exception detail are capturable for every attempt. That
is a build requirement recorded here, not a change made here.

### 3.3 Storage, hashing, linkage

- **Where:** one JSON file per capture, `captures/<capture_id>.json`,
  in the pilot execution record area whose layout Stage 3 owns.
  Files are append-only: written once, never edited (any correction
  is a new artefact referencing the old, per programme practice).
- **No adapter-maintained index.** The adapter writes capture files
  and nothing else; it keeps no index, manifest, or ledger of its
  own. (Programme rule, Ben 2026-11-12: index artefacts are
  system-written only; no harness component edits an index.) The
  directory listing is the enumeration; linkage is by reference:
- **Linkage:** the harness's execution record (Stage 3) references
  each `[MODEL]` step's call by `{capture_id, record_sha256,
  request_sha256, response_sha256}`. An examiner follows the
  reference, recomputes `record_sha256` over the stored record
  (canonical JSON, the `record_sha256` field omitted), and confirms
  the request and response hashes against `request_raw` /
  `response_raw`. A mismatch at any point voids the record's
  evidence, exactly as a Stage 0 pin mismatch voids a pin.

### 3.4 What is never captured

Headers are not part of the record, and the `Authorization` header
above all: the credential transits only inside the connector's
surrogate mechanism, and no capture field may contain it, a
surrogate, or any fragment of either. `request_raw` is the request
**body** only. If a failure detail would quote a header, it is
redacted before writing — the Stage 5 build must implement this,
and Stage 5 inspection must test it.

---

## 4. FAILURE TAXONOMY

### 4.1 Three classes, three owners of the classification

| Class | Definition | Determined by | Examples |
|---|---|---|---|
| **ADAPTER_FAILURE** (infrastructure) | No usable response from the pinned subject was obtained, or the response's identity is not the pinned subject's. The subject never got its chance, or cannot be shown to have had it. | The adapter, at capture time (fields 27–29) | Model id listed but not served (HTTP 404); auth/config rejection (401/403); HTTP 429 or 5xx still failing after the declared retries; timeout (120 s); connection failure; helper crash or non-JSON helper output; served model id ≠ pinned id (§1.4); pinned id absent at pre-flight (recorded as a pre-flight failure, no call made) |
| **SUBJECT_FAILURE** | A response from the pinned subject was received and preserved, and its *content* fails what the step asked of the subject. | The harness/examiner, **from the capture record** — never by the adapter (§5) | Refusal to perform the step; output not in the step's declared structure (malformed where structure is required); empty completion; truncation (`finish_reason` = length) where the step required a complete artefact; content that ignores the step's declared inputs |
| **GOVERNANCE_FAILURE** | The subject's output was received, and the deterministic machinery — not the model — rejects or fails it. The governance layer working, or being caught out, is the finding. | The tools / verification layer, recorded in the execution record | `verify_field` returns FAIL; `receipt_worksheet` returns REJECT; an insertion rejected under the tightened provenance rule (Qualification §5 item 6 — the rule whose absence in V2 is the §3 defect); a produced field with no evidence trail |

The division matters because the pilot's question (Plan §4) requires
the three to be distinguishable in the record: a run that fails
because NVIDIA 404'd proves nothing about Nemotron, and a run where
verification catches the subject proves something about governance,
not about infrastructure. **A governance failure is never retried
away and never reclassified** as either of the others; a subject
failure is data about the subject; an adapter failure is data
about the lane, and invalidates the affected step as evidence about
anything else.

### 4.2 Boundary cases, ruled in advance

- **Truncation** (`finish_reason` = length): the response is
  complete as transport, incomplete as an answer → SUBJECT_FAILURE
  (harness-determined), not an adapter failure.
- **HTTP 200 with an unparseable body:** transport succeeded; the
  response is captured verbatim; harness classifies (subject or
  provider anomaly) from the record. Not adapter-retried.
- **429/5xx that succeeds on retry:** the call stands as a success;
  the failed attempt remains in `attempts`. No failure class is
  assigned to the call.

### 4.3 Retry rule

Retries are **bounded, declared, and recorded — never silent:**

- **Maximum attempts: 2** (the original call plus one retry).
- **Retryable classes only:** HTTP 429, HTTP 5xx, timeout,
  connection error. **Never** retried: any other 4xx (including the
  404 that means not-served), any received-and-captured response,
  any failure the harness or governance layer owns.
- **Fixed delay: 5 s** between attempts (the free tier is reported
  at roughly 40 requests/minute, model-specific; the retry exists
  to ride out a transient, not to lean on the limit).
- **Byte-identical resend:** a retry sends the same `request_raw`;
  `request_sha256` is invariant across attempts, and an examiner
  can check it.
- The retry policy is part of the pinned configuration
  (`adapter_config_sha256`); changing it is an amendment.

---

## 5. INTERFACE BOUNDARY

The adapter exposes **exactly one operation** to the harness:

```
complete(step_inputs) -> { capture_record_id, raw_output }
```

- `step_inputs` is the §2.2 object: `correlation_id`, `tree_id`,
  `step_id`, `messages`. Nothing else is accepted — no parameters,
  no options, no overrides.
- `capture_record_id` is the `capture_id` of the record written for
  this call (§3). It is returned in **all** outcomes, success or
  failure: failure is data in the record, not an exception across
  the boundary. (Adapter-internal misconfiguration is a build-time
  fault, caught at Stage 5 inspection, not a run-time outcome.)
- `raw_output` is `choices[0].message.content` of the final
  attempt, **verbatim** — or `null` when no usable response exists,
  in which case the record carries the adapter failure. The full
  raw response is never squeezed through this return value; the
  harness reads it from the capture record when it needs it.

The adapter **never**:

- executes tools, or knows that tools exist;
- writes the ledger, or any execution-record entry — it writes
  capture records only, and the harness links them (§3.3);
- interprets, parses (beyond extracting the §3 response fields
  verbatim), scores, summarises, or repairs the response;
- modifies `messages`, adds content, or varies any parameter;
- decides anything about the step's success — step satisfaction,
  failure handling and recovery belong to the trees and the harness
  (Stage 3).

Tool execution stays entirely with the harness. If a `[MODEL]` step's
output asks for a tool call, that text is just `raw_output`; whether
and how it is acted on is a Stage 3 question, answered there, not
smuggled into this boundary.

---

## 6. REPLAY

### 6.1 What an examiner can re-derive from the record alone

Given a capture record and the pinned configuration, an examiner
can, without trusting the adapter or the harness:

1. Recompute `record_sha256`, `request_sha256`, `response_sha256`
   and confirm the record is the record that was written.
2. Confirm the sent envelope equals the pinned configuration
   (field 17 against `adapter_config_sha256`'s preimage) and that
   the subject pin was evidenced by the pinned catalogue snapshot
   (fields 10–12).
3. Confirm retry integrity: attempt count within policy, resend
   byte-identical, delay respected (attempt timestamps).
4. Feed `response_raw` — the preserved response, not a fresh call —
   through the deterministic tools and harness rules, and
   re-derive every downstream verdict (verification results,
   obligation decisions, ledger entries). This **governance replay
   is exact**, because everything downstream of the response is
   deterministic and pinned. This is the replay the pilot's
   question actually depends on (Alex §4: an independent examiner
   can reconstruct the outcome from the preserved record).

### 6.2 What replay cannot mean here — stated honestly

**Output byte-replay is impossible, and this design does not claim
it.** The subject is a hosted model behind a provider API.
Re-issuing `request_raw` byte-for-byte — which the record fully
supports, and which is the only honest meaning of "replay" at the
adapter boundary — produces a *new sample*, not the recorded
output: temperature 0 reduces variance but does not eliminate it
(provider-side batching and mixture-of-experts routing are outside
any caller's control), and the provider may re-serve or update the
model behind an unchanged id. A re-issued call is therefore new
evidence, labelled as such (its own capture record, linked to the
original by correlation), never a verification of the original.
Any future claim that a Nemotron output was "replayed" must be
read as input-replay plus governance re-derivation (§6.1.4), or it
is claiming something false.

---

## 7. OPEN QUESTIONS — with recommended defaults

1. **Primary pin confirmation.** §1.2 pins
   `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` on the id's own
   declaration. **Default:** stand, unless the §1.3 model-card
   evidence shows the Omni variant is vision-first — then Alternate
   1 (`nvidia/nemotron-nano-3-30b-a3b`) becomes primary by amendment
   before Stage 5. *For Alex to confirm the reading of the plan's
   "(reasoning)" against the cards.*
2. **Reasoning-control mechanism.** The exact parameter is whatever
   the pinned model's card documents; this design pins the
   *requirement* (one mechanism, ON, in configuration), not a
   parameter name sight-unseen. **Default:** adopt the card's
   documented mechanism at Stage 5 freeze and record it in the
   configuration; if none is documented, the model's default
   reasoning behaviour is the pin. *For Alex.*
3. **`seed` parameter.** OpenAI-compatible endpoints commonly accept
   a `seed`; whether this endpoint honours or even tolerates it is
   unknowable without a call, and an unvalidated field risks an
   adapter failure on every call. **Default:** omit `seed` in
   configuration v1; temperature 0 is the declared determinism
   control. Revisit only on Stage 6 evidence. *For Alex/Ben.*
4. **`max_tokens` value.** **Default:** 4096 for all steps (§2.3).
   If any tree's [MODEL] step is shown at Stage 3 to need a larger
   artefact, amend once, for all steps — not per step. *For Alex.*
5. **Retry bounds.** **Default:** 2 attempts maximum, 5 s fixed
   delay, retryable classes as §4.3. *For Alex to confirm against
   the free tier's ~40 requests/minute.*
6. **Per-attempt timeout.** The helper's is 120 s. **Default:**
   keep 120 s per attempt (a reasoning model on a long step is the
   slow case the pilot must tolerate); total worst case per
   `complete()` ≈ 245 s, which Stage 3's stop conditions must
   accommodate. *For Alex.*
7. **Served-status smoke call at Stage 5.** The pin is
   SERVED-UNVERIFIED until Stage 6 (§1.3); a single declared smoke
   call at inspection would retire the 404 risk earlier but crosses
   the plan's "no calls yet" line. **Default:** no smoke call —
   served status is established by the first authorised Stage 6
   call, and a 404 there follows the §1.4 re-pin procedure. *For
   Ben/Alex, since it touches the plan's gate wording.*
8. **Capture format.** **Default:** one JSON file per capture,
   no adapter index (§3.3), JSONL rejected precisely because an
   appended log invites the index-editing the programme rule
   forbids and complicates per-record hashing. *For Alex.*
9. **Catalogue evidence refresh at execution.** **Default:**
   re-capture and re-hash the catalogue at Stage 6 pre-flight
   (§1.4) on the day of any authorised run; a catalogue that has
   dropped the pinned id stops the run before it starts, however
   inconvenient. *For Ben (it can veto a scheduled run).*

---

## Scope notes

- This is a specification, not an implementation. Nothing in it
  has been executed; the endpoint, helper behaviour, and catalogue
  facts are cited from the connector doc and helper source, both
  read at design time, and from the Stage 0/1 artefacts named in
  the header.
- Where this design depends on the pinned model's model card (§1.3,
  §2.3 reasoning control, Q2), the dependency is declared rather
  than filled in from general knowledge of the Nemotron family:
  the card is the evidence, and it is documentary work for Stage 5
  preparation, not a call.
- Changes to make tree inputs model-neutral are declared in
  Qualification §5 and owned by Stage 3; this design only fixes
  the boundary those inputs cross.
