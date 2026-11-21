# BATCH 5 — CHUNK SHEET (2026-11-14) — APPROVED WITH CORRECTIONS

Approved version. The draft of the same date
(sha256 b08f763d…) is preserved unchanged as history;
this copy carries Alex's approval in the disposition
slot and his pin-identification correction in C5-0c /
C5-3. Approval: Alex, 2026-11-14, PB-ID
pb-mwgz9mjj-2-dp2t — the same letter records the
Batch 4 checkpoint CLEARED, so both opening gates
below are satisfied and Batch 5 may begin.

Drafted from the shelf: STAGE5-BUILD-SPEC-22 (pin afae29fb)
as amended by Revs 23–26 — Rev 26 §3.6 (Adapter) and §3.7
(transport double; no-provider-contact enforcement), and
§4 Batch 5. Each chunk is discharged by the Batch 5
checkpoint report line by line.

**Status and how this sheet travels.** This sheet rode
as a draft inside the Batch 4 checkpoint submission
for Alex's approval, under the Stage 5 Completion Plan
Rule 4 ("each sheet rides for Alex's approval INSIDE the
previous block's checkpoint submission, so sheet approval
never costs its own round") and Alex's Batch 4 drift
check, Finding 2, and checkpoint crosswalk row "Batch 5
chunk sheet approval."

**INCLUSION IN THE BATCH 4 SUBMISSION DOES NOT AUTHORISE
BATCH 5 TO BEGIN.** Its inclusion is a packaging
obligation only (Completion Plan Rule 4; drift check
Finding 2: "It does not become a C4-8…C4-12 implementation
item, nor does its inclusion authorise Batch 5 to begin
before its sheet is approved"). Batch 5 opens only when
BOTH of these hold: (a) Alex approves this sheet, the
approval recorded in the disposition slot at the foot of
this sheet; and (b) the Batch 4 checkpoint has passed —
each batch's checkpoint must pass before the next batch
begins (Rev 26 §4 preamble). Batch 5 then runs under
Ben's 2026-11-13 build go (Batches 2–6 in order), as
Block 2 of the Stage 5 Completion Plan.

## Authorities and pins (verified for this draft)

Local files read and sha256-verified in this drafting
session:

- STAGE5-BUILD-SPEC-26.md — sha256
  1126bcf02d4aa6829672cbdb6b660bbc838b008e7fa850b3a6070c8f8e433989.
  Governing text: §3.6 (lines 6041–6163), §3.7 transport
  double and no-contact enforcement (lines 6259–6330),
  §4 Batch 5 (line 6547 ff.).
- STAGE5-COMPLETION-PLAN-2026-11-14.md — sha256
  8f431838612e9fe2ab08a8a121c66a02c4dc0b3af932b02398b9e955b26d31fe.
  Governing text: Block 2 (Batch 5), Rule 3 (whole
  rounds, one checkpoint per block), Rule 4 (this sheet's
  route to approval), Rule 8 (Ben's reserved matters; no
  subject call in Blocks 0–3).
- BATCH4-CHUNK-SHEET-2026-11-13.md — sha256
  10e172175e5615548ac266fa00b21ef9dc3c945b683be58b1858ae2a5f145faa,
  with BATCH4-CHUNK-SHEET-REV2-2026-11-13.md — sha256
  5c7353e9507aef771bfe11c38df39766d1f982bfc6be69e1a001bdcb2307f453.
  Format model for this sheet (pre-batch gate / build /
  checkpoint / standing rules; C4-D1/C4-D2 mirrored as
  C5-D1/C5-D2 below).
- ALEX-BATCH4-DRIFT-CHECK-2026-11-14.md — sha256
  bc34ffcce5b0a25b53a4afb3a06f4896b1be931f27ae20ce03c9f776ef7e20bd
  (Finding 2: this sheet's ride inside the Batch 4
  submission).
- ALEX-BATCH4-CROSSWALK-2026-11-14.md — sha256
  599c0899a3e96764d76e3fe67237480e9a53ca3dba426aec58c6951d4c03d522
  (row "Batch 5 chunk sheet approval": the sheet is
  "derived from the governing spec pin, defines Batch 5's
  chunks and discharge evidence," and carries "an
  approval disposition slot for Alex").

Cited from those authorities, not independently
re-verified here: Spec Rev 22 at shelf pin afae29fb;
Rev 26 shelved at 52a73273 and CLEARED at a3a66137
(Completion Plan, Authorities); Batch 4 whole-plan Rev 8
at shelf commit f13dbdac, file sha256 fba0a629… (local
copy verified: fba0a6293e33cef3bb0866e27699a197de4e8086c888a193cb50d031a3621da3).

## The pre-batch gate (before any Batch 5 build)

- **C5-0a — Sheet approval.** This sheet is approved by
  Alex, the approval recorded in the disposition slot
  below. No Batch 5 implementation starts on the strength
  of this sheet's presence in the Batch 4 submission.
- **C5-0b — Batch 4 checkpoint passed.** The Batch 4
  checkpoint bundle (C4-8…C4-12 + Part B read-back) is
  adjudicated cleared before Batch 5 begins (Rev 26 §4
  preamble; Completion Plan block order, no interleaving).
- **C5-0c — Frozen inputs re-read, not re-made.** The
  adapter configuration frozen at Batch 0 — identity pin,
  envelope values, retry policy, and its
  `adapter_config_sha256` — and the design-time catalogue
  snapshot carried into the Batch 0 freeze (Adapter §1.4)
  are re-read against their pins. Nothing is re-frozen,
  re-listed, or re-configured in this batch: Stage 5
  takes **no live listing** and makes **no provider
  contact of any kind** (Rev 26 §3.6; §3.7 — LANE-ADAPTER
  contact has no Stage 5 exception of any kind). Any
  divergence from the frozen configuration stops the
  batch and is reported; a configuration change is a
  design amendment producing a new hash, never an in-run
  or in-build adjustment.
  **Pin identification (Alex's approval correction,
  2026-11-14, carried here so this chunk is
  unambiguous).** The active Batch 0 pins are: adapter
  design authority `duenna/NEMOTRON-ADAPTER-DESIGN-03.md`,
  sha256 `5be7eb0e59793b98f5352c55778ca2da755e6078be70c00859e3dcc8174909bb`;
  active canonical adapter configuration
  `duenna/batch0/freeze/adapter-config-f2-2026-11-12.canonical.json`,
  whose `adapter_config_sha256` is
  `6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb`;
  readable configuration
  `duenna/batch0/freeze/adapter-config-f2-2026-11-12.json`,
  file sha256 `beb8b7fd670d5bde4593284b0c1575f94f879ba887ea234fc23f6c33132008f5`.
  The older `adapter-config.canonical.json` and its
  `723f78d9…` configuration digest are historical and
  are NOT the active pin.

## The build (§3.6)

- **C5-1 — The single operation** (Adapter §5):
  `complete(step_inputs) -> {capture_record_id,
  raw_output}` — nothing else is accepted: no parameters,
  no options, no overrides. `capture_record_id` is
  returned in **all** outcomes; failure is data in the
  record, not an exception across the boundary.
  `raw_output` is `choices[0].message.content` of the
  final attempt, verbatim (reasoning content and final
  answer as one preserved artefact — never split,
  stripped, or re-presented), or `null` when no usable
  response exists.
- **C5-2 — The adapter's prohibitions** (Adapter §§2.3,
  5): the adapter never executes or knows of tools; never
  writes the ledger or any execution-record entry
  (capture records only); never interprets, scores,
  summarises, or repairs a response; never modifies
  `messages`; adds no content of its own — no adapter
  system prompt, prefix, suffix, reformatting, or
  trimming.
- **C5-3 — Pinned identity and catalogue pin** (Adapter
  §§1.2, 1.4): `model` is
  `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`,
  exactly, and must equal the helper's MODEL argument on
  every call. Alternates are declared, never automatic:
  no code path in the adapter or harness selects an
  alternate at run time; moving to one is a re-pin by
  amendment. The catalogue pin is the pair (model id,
  catalogue snapshot sha256 + capture date) from the
  Batch 0 freeze — concretely (Alex's approval
  correction, 2026-11-14): capture date **2026-11-12**;
  primary recovered catalogue artefact
  `duenna/batch0/freeze/recovered-catalogue-response-2026-11-12.json`;
  bare JSON body sha256
  `8a80b8e7f84bbbcfa81728bfd56a6abd45b4c3ab3f18830db9c6bb93b2eb402b`;
  preserved helper-stdout file sha256
  `bacf2ec8c71a8972af2f0116f9b3cf16963238020678aa3f118f608af3f8f262`.
  Catalogue-evidence limitation, carried from the F-2
  continuation: the recovered response is helper-stdout
  serialization — 8,628 bytes including its trailing
  newline, with an 8,627-byte bare JSON body; neither
  digest claims original NVIDIA wire-byte identity.
  The pin is carried as **PINNED-LISTED,
  SERVED-UNVERIFIED** through Stage 5 and into Stage 6:
  nothing in this build asserts, implies, or tests its
  way into a served claim; served status is established
  only by the first authorised Stage 6 call. (The §1.4
  pre-flight catalogue re-check against the live host is
  Stage 6 work, not this batch's.)
- **C5-4 — Pinned envelope** (Adapter §2.3): the adapter
  adds only these fields, from pinned configuration,
  never varied per call — `model` (as C5-3);
  `temperature` 0.6; `top_p` 0.95; `max_tokens` 20480;
  `stream` false; `chat_template_kwargs`
  `{"enable_thinking": true, "reasoning_budget": 16384}`
  at the body root. The request body is sent byte-for-byte
  as constructed; its sha256 is `request_sha256`; a retry
  resends the identical bytes. Configuration is the
  frozen `adapter_config_sha256` of C5-0c.
- **C5-5 — Capture writer, schema `ADAPTER-CAPTURE-02`**
  (Adapter §3): every call — successful, failed, or
  retried — produces exactly one 30-field capture record,
  written before the adapter returns. One JSON file per
  capture (`captures/<capture_id>.json`), written once,
  never edited; the adapter keeps **no index** of its
  own. Top-level request/response fields describe the
  final attempt; **every attempt** is preserved in
  `attempts[]` with its `response_body_raw` verbatim and
  `response_body_sha256` — including the error body of a
  429 or 5xx that triggered a retry; `null` only when no
  body was received. Retries are never silent: a success
  after a retry is recorded as a success **with** the
  retry and the failed attempt's body visible.
- **C5-6 — Helper wrapper** (normative build requirement,
  Adapter §3.2): the sanctioned helper raises on HTTP
  error, surfacing status and body as an exception; the
  build therefore wraps the helper invocation (or
  implements the identical call through the same
  credential mechanism) so that **every** attempt's
  status, raw body, timing, and exception detail are
  capturable. A build in which any attempt can end
  without its available body and hash in `attempts[]`
  fails this specification.
- **C5-7 — Never captured; redaction** (Adapter §3.4):
  headers are not part of the record — the
  `Authorization` header above all. The credential
  transits only inside the connector's surrogate
  mechanism; the adapter never sees, holds, or records
  the key or any fragment of it. `request_raw` is the
  request **body** only. Any failure detail or error body
  that would quote a header is redacted before writing.
- **C5-8 — Failure taxonomy** (Adapter §4):
  ADAPTER_FAILURE is determined by the adapter at capture
  time and by no one else — 404 not-served; 401/403; a
  400 rejecting the pinned envelope; 429/5xx exhausted
  after the declared retries; timeout (120 s per
  attempt); transport failure; helper error; served
  model id ≠ pinned id; pinned id absent at pre-flight
  (recorded as a pre-flight failure, no call made — the
  pre-flight itself is Stage 6's; the classification
  lands here). SUBJECT_FAILURE and GOVERNANCE_FAILURE
  are determined downstream, from the capture record,
  never by the adapter.
- **C5-9 — The pre-classified 400** (Adapter §§1.3(e),
  4.2): hosted acceptance of `chat_template_kwargs` for
  this model is UNSETTLED. An HTTP 400 whose preserved
  body identifies that field as the rejected parameter is
  **an ADAPTER_FAILURE, never a subject failure**, is
  never retried, halts the affected tree under the
  adapter-failure rule, and its remedy is a configuration
  amendment decided by Ben/Alex against the capture —
  never an in-run envelope change.
- **C5-10 — Retry policy** (Adapter §4.3): maximum **2
  attempts** (original + one retry); retryable classes
  only — HTTP 429, HTTP 5xx, timeout, connection error;
  never any other 4xx, never a received-and-captured
  response; fixed **5 s** delay; byte-identical resend
  (`request_sha256` invariant across attempts). The
  policy is part of the pinned configuration (C5-0c).
- **C5-11 — Stage 5 isolation, enforced** (§3.7): in
  Stage 5 mode the adapter **refuses any non-loopback
  base URL** — a configuration naming a non-loopback
  provider address fails closed at start-up, before any
  run; the transport double's loopback endpoint is the
  only address a Stage 5 adapter can be configured to
  reach. Proxy configuration, however supplied, is **not
  honoured** in Stage 5 mode. The build environment
  holds **no provider credential**. (The zero-egress
  environment evidence is gate G1, Batch 6 work under
  the Completion Plan Block 3 — it is not claimed,
  evidenced, or assumed in this batch.)
- **C5-12 — The transport double** (§3.7): a local
  scripted HTTP double — a loopback test endpoint
  replaying declared status/body sequences (200-with-body,
  429-then-200, 500-then-200, 400 rejecting
  `chat_template_kwargs`, timeout). The adapter under
  test is the real adapter; only the endpoint is doubled,
  and the double's identity is recorded in every test
  artefact it touches. The double is test scaffolding
  for this batch's checkpoint; it is not the stub subject
  (Batch 6's full-battery run is separate evidence for a
  separate boundary, §3.7), and neither substitutes for
  the other.

## The checkpoint (§4 Batch 5)

Against the **transport double** (§3.7) only — no live
endpoint, no subject call. The checkpoint is discharged
in ONE bundle (Completion Plan Rule 3), each item with
its underlying evidence, not a summary assertion
(crosswalk standard, applied to this batch by parity).

- **C5-13 — Retry sequences captured whole.** Forced
  429-then-200 and 500-then-200 sequences, plus the
  200-with-body baseline: every attempt's body and hash
  present in `attempts[]`, and the resend byte-identical
  (`request_sha256` invariant across attempts).
- **C5-14 — The pre-classified 400.** A forced 400
  rejecting `chat_template_kwargs` is classified
  ADAPTER_FAILURE and is not retried (exactly one attempt
  in the capture record).
- **C5-15 — Timeout.** A timeout sequence is classified
  (ADAPTER_FAILURE, timeout class) and captured, with the
  attempt's available detail preserved.
- **C5-16 — Redaction test.** No capture field in any
  test artefact contains header or credential material.
- **C5-17 — Envelope fidelity.** The envelope as sent
  equals the pinned configuration byte-for-byte in every
  test capture (`request_envelope` vs the
  `adapter_config_sha256` preimage).
- Out of this checkpoint, by authority: the stub-subject
  full-battery run and the examiner tooling (Batch 6);
  the §5 gates G1–G5, including zero-egress evidence
  (Batch 6); any live catalogue listing or served-model
  claim (Stage 6 pre-flight).

## Standing rules

- **C5-D1** — records and artefacts ride with the
  checkpoint bundle; pins by dated continuation.
- **C5-D2** — no subject call, and no provider contact
  of any kind, anywhere in this batch; the adapter is
  proven against the transport double only, end to end,
  on the record (Completion Plan Block 2).
- **C5-D3** — settled is settled (Completion Plan
  Rule 1): the frozen adapter configuration, the
  `ADAPTER-CAPTURE-02` schema, and the failure taxonomy
  are built as pinned, not re-adjudicated in this batch;
  a finding against this checkpoint names its governing
  pin and clause (Rule 2), and corrections, if any, are
  ONE chunked correction round per checkpoint (Rule 3).
- **C5-D4** — Ben's reserved matters are untouched
  (Completion Plan Rule 8): nothing in this batch spends,
  publishes, creates accounts, or contacts the provider;
  a configuration amendment under C5-9 is decided by
  Ben/Alex against the capture, never improvised by the
  build.

## Approval disposition (Alex)

- Disposition: **APPROVED WITH CORRECTIONS**
- PB-ID / date: pb-mwgz9mjj-2-dp2t, 2026-11-14
  (alex-remmy-b4-b5-and-programme-decision-2026-11-14)
- Corrections: one pin-identification correction —
  the active F-2 configuration and catalogue identities
  are now carried exactly in C5-0c and C5-3 above
  (design authority 5be7eb0e…; adapter_config_sha256
  6cf57195…; readable configuration beb8b7fd…;
  catalogue capture 2026-11-12, bare body 8a80b8e7…,
  helper-stdout file bacf2ec8…, with its
  wire-byte-identity limitation). Pin clarification
  only; no new test or scope.
- Batch 4 gate: the same letter records **BATCH 4
  CHECKPOINT: CLEARED** (C4-10 hold withdrawn;
  crosswalk erratum filed 2026-11-14).

Both opening gates are satisfied — this sheet is
approved and the Batch 4 checkpoint has passed — so
**Batch 5 may begin**, under Ben's 2026-11-13 build
go (Batches 2–6 in order). No Stage 6 action is
implied.
