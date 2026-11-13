# NEMOTRON ADAPTER DESIGN 03 — SUBJECT INTERFACE SPECIFICATION (REV 03)

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12; Alex adjudication pb-mwe90lo6)
**Stage:** 2 — Nemotron Adapter Design (Plan prerequisite #4, BLOCKING)
**Status:** DESIGN ONLY. No model calls are made or authorised by this
document. No code is built by this document (Stage 5). No shelf file
is modified by this document.
**Revision:** Rev 03, issued in response to Alex's verification
verdict on Rev 02 (Rev 02 shelved at commit
`499cad0922d039ca84d2a891bbe3178b705a214d`; verdict pb-mweajgej,
2026-11-12). His findings for this document: correction F
accepted, with hosted status still unverified as designed; and a
**parameter ruling** — `max_tokens` 20480 accepted, temperature
to change 0 → 0.6. This revision folds in that ruling and
nothing else. Rev 01 remains unmodified and remains the
inspected document of record (inspected at shelf commit
`96c74478c576aadc150361998114c3b58a463f41`); Rev 02 remains
unmodified as the verified revision; this revision supersedes
Rev 02 as the design going forward and is itself subject to
Alex's verification of the correction pass before Stage 5.
Stage 5 and Stage 6 gates are untouched by this revision.
**What changed in Rev 03** (see REVISION-03-NOTE.md for the full
mapping — the changes are confined to the pinned envelope and
the places that described it):
- **§1.5 / §2.3 — the documented Thinking-mode configuration
  is pinned in full, explicitly:** temperature **0.6** (was 0;
  Rev 02's recorded divergence is withdrawn on Alex's ruling),
  `top_p` **0.95** pinned explicitly (Rev 02 omitted it, leaving
  an unspecified served default), `reasoning_budget` **16384**
  pinned in `chat_template_kwargs` (Rev 02 left it at the
  model's default), `max_tokens` **20480** confirmed as
  accepted. Alex's reasoning is recorded in §1.5: temperature 0
  does not make a hosted model deterministic; the harness and
  evidence machinery must be deterministic — the subject does
  not have to be; pinning the vendor's documented configuration
  avoids an unnecessary experimental deviation.
- **§6.2 and §7 Q3/Q4 aligned:** the determinism premise is
  removed wherever it leaned on temperature 0; Q4 is closed
  by the ruling; §3 field 17's envelope echo now names `top_p`.
- The capture schema `ADAPTER-CAPTURE-02` is unchanged; the
  identity findings of §1.3 are unchanged; correction C's
  per-attempt preservation is unchanged.
**Inputs:** Plan 01 (Stage 2 section; Alex §4 minimum evidence);
V2-QUALIFICATION-01 (esp. §2 model coupling, §5 declare-only
changes); PILOT-MANIFEST-01 (Stage 0 freeze); NEMOTRON-ADAPTER-
DESIGN-02 (Rev 02, the document this revises); Alex's inspection
verdict (2026-11-12) and his Rev 02 verification verdict
(pb-mweajgej, 2026-11-12); `custom.nvidia` CONNECTOR.md and its helper
`~/workspace/custom-connectors/custom.nvidia/bin/nvidia_api.py`;
NVIDIA's model card and documentation for the pinned model (§1.3,
sources listed there).

**What the adapter is.** The single, narrow bridge between the pilot
harness (Stage 3) and the hosted Nemotron subject, over Ben's NVIDIA
lane. It exists because of Qualification §2: in the V2 stack the
subject is welded into the runner (`MODEL = "qwen/qwen3.8-27b"`, a
Groq-connector shell-out, corpus and ground truth as module
constants). The pilot retires that coupling by giving the subject
exactly one boundary, specified here, through which every call and
every byte of evidence must pass.

---

## 1. SUBJECT IDENTITY — PINNED, AND SETTLED WHERE DOCUMENTATION SETTLES IT

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
  property to assumption. **Rev 02: the documentary evidence of §1.3
  confirms this pin** — the card for this exact identity documents a
  first-class text posture and a documented reasoning control, so
  Rev 01's stated trigger for falling to Alternate 1 (the Omni
  proving vision-first, or lacking a plain text chat posture) is
  **not met**.
- **Alternate 1 (declared, not automatic):**
  `nvidia/nemotron-nano-3-30b-a3b` — the text-native Nano 3. Retained
  as a declared alternate only; the §1.3 evidence does not trigger
  it.
- **Alternate 2 (declared, not automatic):**
  `nvidia/nemotron-3.5-lightning-30b-a3b` — a different minor line
  and therefore a different subject identity; usable only by re-pin.
- An alternate is **never** selected by the adapter or the harness
  at run time. Moving to an alternate is a re-pin: a dated amendment
  to this design and to the pilot manifest, with fresh catalogue
  evidence (§1.4), made before any call under the new pin.

### 1.3 Identity evidence — settled and unsettled

Rev 01 left the choice to documentary evidence gathered before
Stage 5. That evidence has now been gathered from NVIDIA's own
sources (retrieved 2026-11-12):

- **S1 — the model's official model card** (the card NVIDIA
  publishes for this identity on build.nvidia.com, mirrored
  verbatim as the Hugging Face card for
  `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`):
  https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning/modelcard
  and https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16
- **S2 — NVIDIA's hosted-endpoint documentation** (docs.nvidia.com:
  the AI-Q Blueprint configuration reference and examples, and the
  NeMo voice-agent NIM pages), which configure models against the
  hosted base URL `https://integrate.api.nvidia.com/v1` and document
  `chat_template_kwargs` / `enable_thinking` as request-body fields
  on that path:
  https://docs.nvidia.com/aiq-blueprint/1.2.1/customization/configuration-reference.html
  and https://docs.nvidia.com/nemo/labs-voice-agent/build-voice-agents/model-serving/nvidia-nim-riva/
- **S3 — the live catalogue on Ben's key** (2026-11-12, via the
  connector): the listing recorded in §1.1, corroborated by the
  card's release record (this identity released via
  build.nvidia.com, Hugging Face, and NGC on 04/28/2026).

Findings, each labelled:

**(a) Documented capabilities and modality — SETTLED.**
Per S1, the pinned model is **multimodal by design**: input types
Video, Audio, Image, and Text; output type Text only. Architecture:
a Mamba2-Transformer hybrid MoE (31B total, ~3B active) whose
language backbone is the Nemotron 3 Nano LLM (30B A3B), with a
CRADIO v4-H vision encoder and a Parakeet speech encoder. Context
length up to 256k tokens; language support English only; output
supports JSON format, reasoning output with chain-of-thought, and
tool calling. **Consequence for the pin:** the subject is an omni
model, not a text-only model. That is now a documented fact of the
subject's identity, recorded here so no later claim describes it
otherwise. It does not disturb the pin: the trees consume only the
text posture, which (b) settles.

**(b) Text-input behaviour — SETTLED.**
Per S1, Text is a documented input type (format: String), and the
card's own quick-start includes a plain text chat-completions
example — a `messages` array with a simple string-content user
message — alongside its image/audio/video examples. The card's
reasoning notes state the default reasoning behaviour "is
appropriate for text and image inputs." Text is a first-class
posture of this model, served on the same backbone the omni
encoders attach to. Rev 01's open worry — that the Omni variant
might be vision-first with a secondary text path — is **not
supported by the card**; the §1.2 fall-to-Alternate-1 trigger is
not met.

**(c) Documented reasoning control — SETTLED at the model level.**
Per S1's "Reasoning Mode (`enable_thinking`)" section: reasoning
is **on by default**; omitting the control emits chain-of-thought
in `content` before the final answer. The documented control is a
request-body field, placed at the body root in raw JSON:

```
"chat_template_kwargs": {"enable_thinking": true | false}
```

(`false` → reasoning off, only the final answer in `content`.)
The card further documents budget-controlled reasoning
(`reasoning_budget` within `chat_template_kwargs`;
`thinking_token_budget` at body root) and a documented
**Thinking mode** parameter set: temperature 0.6, top_p 0.95,
max_tokens 20480, reasoning_budget 16384, grace_period 1024
(§1.5 takes up the two points where this meets the pilot's pinned
envelope). Per S2, NVIDIA's own hosted-endpoint documentation
uses this same body field against `integrate.api.nvidia.com` —
the mechanism is not a self-hosting-only convention.

**(d) Catalogue evidence for the identity — SETTLED as listed.**
S3 (the live listing on Ben's key, §1.1) plus S1's release record
establish that `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` is
an official NVIDIA API-catalogue identity, listed to this key on
2026-11-12. The pin's catalogue component (§1.4) is unchanged:
the pin is the pair *(model id, catalogue snapshot hash + capture
date)*, re-evidenced at Stage 5 freeze and Stage 6 pre-flight.

**(e) Hosted acceptance of the reasoning field for THIS model —
UNSETTLED.** S2 documents `chat_template_kwargs` on the hosted
path for NVIDIA's hosted NIM pattern and for the text Nano
(`nvidia/nemotron-3-nano-30b-a3b`) specifically; no NVIDIA page
found documents the hosted deployment of *this omni model*
accepting the field, and the hosted request schema is strict
enough, on other models' evidence, to reject undocumented fields
with HTTP 400. **Consequence:** the reasoning pin (§2.3) is set to
the documented mechanism, and the design treats a first-call 400
rejecting the field as an adapter failure with its own boundary
case (§4.2) — the question is settled by the first authorised
call's capture, not by assumption in either direction. The
configuration freeze may proceed with this point open **only**
because the failure mode is pre-classified and the capture
records the envelope as sent (§3), so the evidence will exist
either way. If Alex requires the point closed before freeze, the
only honest closer is the §7 Q7 smoke call, which remains Ben's
call, not this design's.

**(f) Served status — UNSETTLED, by design.** Listed ≠ served.
The connector record already proves the gap
(`mistralai/mistral-7b-instruct-v0.3` was listed on this key and
its chat call returned 404). No document can settle served
status; the pin is therefore carried as **PINNED-LISTED,
SERVED-UNVERIFIED** until the first authorised call (Stage 6).
A 404 on that first call is an adapter/infrastructure failure
under §4, not a subject result, and triggers the re-pin
procedure — never a silent fall-through to an alternate.

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

### 1.5 Documented parameters vs the pinned envelope

Two points where S1's documented Thinking-mode parameters meet
Rev 01's pinned envelope (§2.3). Both are resolved here on the
record, not silently; Rev 03 records their final disposition
under Alex's Rev 02 verification ruling:

- **`max_tokens`: 4096 → 20480 (changed in Rev 02; accepted by
  Alex).** The card's documented reasoning budget alone is
  16384 tokens, inside a documented Thinking-mode completion
  cap of 20480. A 4096 cap under reasoning-on would truncate
  the deliberation the subject was pinned *for* — and
  truncation is scored as subject failure (§4.1), which would
  make the envelope manufacture the failures it measures.
  Rev 02 therefore pinned `max_tokens` to the card's documented
  Thinking-mode value, 20480, for all steps, and Alex accepted
  the change in his Rev 02 verification. Rev 03 also pins the
  budget itself explicitly, as the ruling's full-configuration
  pin requires: `reasoning_budget` 16384 in
  `chat_template_kwargs` (§2.3), where Rev 02 had left it to
  the model's default.
- **`temperature`: 0 → 0.6 (changed in Rev 03, on Alex's
  ruling).** Rev 02 kept Rev 01's temperature 0 — minimising
  sampling variance, its stated reason — against the card's
  recommendation of 0.6, recorded the divergence openly, and
  carried it as §7 Q4 for Alex's ruling. He has ruled:
  **change temperature to 0.6.** His reasoning is recorded here
  because it states a governing principle of the pilot, not
  merely a parameter preference: *temperature 0 does not make
  a hosted model deterministic; the harness and evidence
  machinery must be deterministic — the subject does not have
  to be; this is a governance pilot, not a contest to optimise
  Nemotron's output; and using the vendor's recommended
  Thinking configuration avoids introducing an unnecessary
  experimental deviation.* Rev 03 therefore withdraws the
  divergence and pins the documented Thinking-mode sampling
  configuration in full (§2.3): temperature 0.6, `top_p` 0.95
  (Rev 02 omitted `top_p` entirely, leaving it to an
  unspecified served default — now pinned explicitly, per the
  ruling's directive to pin the documented settings rather
  than leave important parameters to an unspecified default),
  `reasoning_budget` 16384, `max_tokens` 20480. No determinism
  claim is made for the subject anywhere in this design
  (§6.2).

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
All pilot inputs are plain text; no non-text content part is ever
constructed (the subject's other modalities, §1.3(a), are outside
the pilot's boundary).

### 2.3 What the adapter adds: the pinned envelope, and nothing else

The adapter wraps `messages` in a chat-completions body by adding
**only** the envelope fields fixed in its pinned configuration:

| Field | Pinned value | Rationale |
|---|---|---|
| `model` | The §1 pin, exactly | Subject identity; must equal the helper's MODEL argument. |
| `temperature` | `0.6` | The card's documented Thinking-mode value, adopted on Alex's ruling (Rev 03; §1.5). Rev 01/02's temperature 0 does not make a hosted model deterministic (§6.2); determinism is required of the harness and the evidence machinery, not of the subject's sampler. |
| `top_p` | `0.95` | The card's documented Thinking-mode value, pinned explicitly in Rev 03 (Alex's ruling): Rev 02 omitted `top_p`, leaving it to an unspecified served default; the documented configuration is now pinned in full rather than in part. |
| `max_tokens` | `20480` | Rev 02 value, per §1.5: the card's documented Thinking-mode completion cap, sized so the documented reasoning budget (16384) fits inside it. One value for all steps in this design; a step needing more is a design amendment, not a per-call argument. |
| `stream` | `false` | One complete JSON response per call — the only form that can be captured canonically (§3). |
| `chat_template_kwargs` | `{"enable_thinking": true, "reasoning_budget": 16384}` — at the body root, exactly as the model's card documents (§1.3(c)) | The subject is pinned *as* a reasoning model; its deliberation is part of the behaviour under governance, and it is emitted in `content` ahead of the final answer (§1.3(c)) — the harness receives both, as one preserved output. Exactly this one documented mechanism, pinned in configuration — never varied per call, never stacked with a second mechanism. `reasoning_budget` is pinned at the card's documented Thinking-mode value, 16384 (Rev 03, on Alex's ruling; Rev 02 left it at the model's default): the full documented configuration is pinned explicitly rather than left partly to defaults, and the envelope as sent is captured (§3, field 17), so the pin is examinable against every call. Hosted acceptance of this field for this model is the unsettled point of §1.3(e); a rejection is pre-classified in §4.2. |

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

## 3. CANONICAL CAPTURE — SCHEMA `ADAPTER-CAPTURE-02`

### 3.1 The record

Every call — successful, failed, retried — produces exactly one
capture record, written before the adapter returns to the harness.
A call that produces no record did not happen, for all pilot
purposes. **30 fields:**

| # | Field | Content |
|---|---|---|
| 1 | `capture_id` | UUID, issued by the adapter, one per `complete()` invocation |
| 2 | `schema` | `"ADAPTER-CAPTURE"` |
| 3 | `schema_version` | `2` (Rev 02: per-attempt response preservation, §3.2) |
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
| 17 | `request_envelope` | Echo of the §2.3 envelope as sent (model, temperature, top_p, max_tokens, stream, chat_template_kwargs) |
| 18 | `response_received_at_utc` | Final attempt's receipt time; `null` if no response |
| 19 | `response_latency_ms` | Receipt − send, final attempt; `null` if no response |
| 20 | `response_http_status` | Final attempt's HTTP status; `null` on transport failure before any status |
| 21 | `response_raw` | The exact response body bytes of the final attempt, verbatim; `null` if none |
| 22 | `response_sha256` | sha256 of `response_raw`; `null` if none |
| 23 | `response_model_id_served` | The response body's `model` field, verbatim; `null` if absent/no response |
| 24 | `response_finish_reason` | `choices[0].finish_reason`, verbatim; `null` if absent |
| 25 | `response_usage` | The response body's `usage` object, verbatim (prompt/completion/total tokens as served); `null` if absent |
| 26 | `attempts` | Array, one entry per attempt, each fully captured (§3.2) |
| 27 | `transport_outcome` | `RESPONSE_RECEIVED` \| `HTTP_ERROR` \| `TIMEOUT` \| `TRANSPORT_ERROR` \| `HELPER_ERROR` |
| 28 | `failure_class` | Adapter-determinable class (§4): `ADAPTER_FAILURE`, or `null` when a response was received (subject/governance classification is downstream, §4.1) |
| 29 | `failure_detail` | Human-readable failure description (exception class + message, helper stderr tail); `null` on success. Never contains credential material (§3.4) |
| 30 | `record_sha256` | sha256 of this record's canonical serialisation with this field omitted (§3.3) |

### 3.2 Attempts — every attempt fully captured (Rev 02)

`attempts[]` entries carry: `attempt_no`, `sent_at_utc`,
`received_at_utc`, `http_status`, **`response_body_raw`** (the
attempt's response body bytes, verbatim, whenever the attempt
produced one — including the error body of an HTTP 429 or 5xx that
triggered a retry; `null` only when no body was received),
**`response_body_sha256`** (sha256 of `response_body_raw`; `null`
when it is), `error_class`, `error_detail`. A single-attempt call
has exactly one entry, whose body fields equal the top-level
`response_raw` / `response_sha256`. The top-level request/response
fields describe the **final** attempt; no attempt is ever
overwritten or dropped. A success after a retry is recorded as a
success **with `attempts` showing the retry and the failed
attempt's preserved body** — retries are never silent (§4.3), and
a failed attempt's response is execution history with the same
claim to preservation as the final one (Alex's correction C): a
429's body may carry the provider's own account of the limit, and
a 500's body is the only evidence of what the lane actually did.

Build requirement, normative in Rev 02: the current helper prints
the parsed JSON on success but raises on an HTTP error (status and
error body surface as an exception, not as returned JSON). The
Stage 5 build must therefore wrap the helper invocation (or
implement the identical call through the same credential
mechanism) so that **every** attempt's status, raw body, timing,
and exception detail are capturable. A build in which any attempt
can end without its available body and hash in `attempts` fails
this specification, and Stage 5 inspection must test it
(including with a forced 429/500). Per-attempt bodies are subject
to §3.4 exactly as the final body is: no headers, no credential
material, redaction before writing if a body or error detail
would quote either.

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
  `response_raw` — and, in Rev 02, each attempt's
  `response_body_sha256` against its `response_body_raw`. A mismatch
  at any point voids the record's evidence, exactly as a Stage 0
  pin mismatch voids a pin.

### 3.4 What is never captured

Headers are not part of the record, and the `Authorization` header
above all: the credential transits only inside the connector's
surrogate mechanism, and no capture field may contain it, a
surrogate, or any fragment of either. `request_raw` is the request
**body** only. If a failure detail or an error body would quote a
header, it is redacted before writing — the Stage 5 build must
implement this, and Stage 5 inspection must test it.

---

## 4. FAILURE TAXONOMY

### 4.1 Three classes, three owners of the classification

| Class | Definition | Determined by | Examples |
|---|---|---|---|
| **ADAPTER_FAILURE** (infrastructure) | No usable response from the pinned subject was obtained, or the response's identity is not the pinned subject's. The subject never got its chance, or cannot be shown to have had it. | The adapter, at capture time (fields 27–29) | Model id listed but not served (HTTP 404); auth/config rejection (401/403); hosted rejection of the pinned envelope (400, §4.2); HTTP 429 or 5xx still failing after the declared retries; timeout (120 s); connection failure; helper crash or non-JSON helper output; served model id ≠ pinned id (§1.4); pinned id absent at pre-flight (recorded as a pre-flight failure, no call made) |
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
  (harness-determined), not an adapter failure. (With the Rev 03
  envelope, §1.5, a truncation is no longer plausibly the
  envelope's own manufacture; it is the subject's use of a
  documented budget.)
- **HTTP 200 with an unparseable body:** transport succeeded; the
  response is captured verbatim; harness classifies (subject or
  provider anomaly) from the record. Not adapter-retried.
- **429/5xx that succeeds on retry:** the call stands as a success;
  the failed attempt remains in `attempts`, body and hash
  preserved (§3.2). No failure class is assigned to the call.
- **Hosted rejection of the reasoning field (Rev 02):** an HTTP
  400 whose preserved body (§3.2) identifies the pinned
  `chat_template_kwargs` field as the rejected parameter settles
  §1.3(e) the hard way → ADAPTER_FAILURE, never retried (§4.3:
  400 is not a retryable class), execution halts for the affected
  tree under the harness's adapter-failure rule, and the remedy is
  a configuration amendment (the model's default reasoning
  behaviour as the pin, §1.3(c)) decided by Ben/Alex against the
  capture — never an in-run envelope change.

### 4.3 Retry rule

Retries are **bounded, declared, and recorded — never silent:**

- **Maximum attempts: 2** (the original call plus one retry).
- **Retryable classes only:** HTTP 429, HTTP 5xx, timeout,
  connection error. **Never** retried: any other 4xx (including the
  404 that means not-served, and the 400 of §4.2), any
  received-and-captured response, any failure the harness or
  governance layer owns.
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
  Per §1.3(c), under the pinned reasoning-on envelope `content`
  carries the subject's chain-of-thought ahead of its final
  answer; both are the subject's output, preserved and treated as
  one artefact — the adapter does not split, strip, or
  re-present them.

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
smuggled into this boundary. (The card documents tool calling as a
model capability, §1.3(a); the pilot does not use it — the subject
has no tool access, by harness design.)

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
   byte-identical, delay respected (attempt timestamps) — and, in
   Rev 02, recompute every attempt's `response_body_sha256`
   against its preserved body, so the retry history itself is
   evidence, not assertion.
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
output: the subject is a sampled hosted model, and no sampling
setting makes it deterministic — variance, provider-side batching,
and mixture-of-experts routing are outside any caller's control
(this is Alex's parameter ruling, §1.5, stated at the boundary
where it bites) — and the provider may re-serve or update the
model behind an unchanged id. A re-issued call is therefore new
evidence, labelled as such (its own capture record, linked to the
original by correlation), never a verification of the original.
Any future claim that a Nemotron output was "replayed" must be
read as input-replay plus governance re-derivation (§6.1.4), or it
is claiming something false.

---

## 7. OPEN QUESTIONS — WITH RECOMMENDED DEFAULTS

1. **Primary pin.** **Closed in Rev 02** (§1.3): the card evidence
   confirms the pin — text is a first-class documented posture and
   the reasoning control is documented — so Rev 01's conditional
   fall to Alternate 1 does not trigger. *For Alex to confirm the
   reading of the plan's "(reasoning)" against the card, as Rev 01
   asked.*
2. **Reasoning-control mechanism.** **Closed at the model level in
   Rev 02** (§1.3(c)): `chat_template_kwargs.enable_thinking`,
   pinned `true` at the body root. The one residue is hosted
   acceptance for this model (§1.3(e)), pre-classified in §4.2.
   *For Alex.*
3. **`seed` parameter.** OpenAI-compatible endpoints commonly accept
   a `seed`; whether this endpoint honours or even tolerates it is
   unknowable without a call, and an unvalidated field risks an
   adapter failure on every call. **Default:** omit `seed` in
   configuration v1. No subject-side determinism control is
   claimed or required (Rev 03: Alex's parameter ruling assigns
   determinism to the harness and the evidence machinery, §1.5).
   Revisit only on Stage 6 evidence. *For Alex/Ben.*
4. **Envelope vs the card's documented parameters.** **Closed
   in Rev 03 by Alex's ruling.** The envelope pins the card's
   documented Thinking-mode configuration in full — temperature
   0.6, `top_p` 0.95, `max_tokens` 20480, `reasoning_budget`
   16384 (§1.5, §2.3). Rev 02's temperature-0 divergence and its
   unpinned `top_p` / `reasoning_budget` are withdrawn, not
   carried.
5. **Retry bounds.** **Default:** 2 attempts maximum, 5 s fixed
   delay, retryable classes as §4.3. *For Alex to confirm against
   the free tier's ~40 requests/minute.*
6. **Per-attempt timeout.** The helper's is 120 s. **Default:**
   keep 120 s per attempt (a reasoning model on a long step is the
   slow case the pilot must tolerate); total worst case per
   `complete()` ≈ 245 s, which Stage 3's stop conditions must
   accommodate. *For Alex.*
7. **Served-status smoke call at Stage 5.** The pin is
   SERVED-UNVERIFIED until Stage 6 (§1.3(f)); a single declared
   smoke call at inspection would retire the 404 risk — and would
   also settle §1.3(e) — earlier, but crosses the plan's "no calls
   yet" line. **Default:** no smoke call — served status is
   established by the first authorised Stage 6 call, and a 404
   there follows the §1.4 re-pin procedure. *For Ben/Alex, since it
   touches the plan's gate wording.*
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
  the header. The identity facts of §1.3 are cited from the NVIDIA
  sources listed there, retrieved 2026-11-12; each is labelled
  SETTLED or UNSETTLED, and the unsettled points carry their
  consequences rather than an assumption.
- Changes to make tree inputs model-neutral are declared in
  Qualification §5 and owned by Stage 3 (including the
  interpretation note, now INTERPRETATION-NOTE-01); this design
  only fixes the boundary those inputs cross.
