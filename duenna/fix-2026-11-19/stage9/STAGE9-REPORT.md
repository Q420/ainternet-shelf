# STAGE 9 REPORT — The re-runnable battery (STEP6 tree set and acceptance criteria)

## Verdict

**The battery is assembled, frozen, and tested — and it did not run,
because the subject it exists to test is not there.** At the Stage 9
freeze on 2026-11-20, the mandatory K2 live verification call to the
NVIDIA endpoint naming the pinned subject `openai/gpt-oss-20b`
returned **HTTP 410 (Gone)**, and the subject is absent from the
key's live model list (33 models listed; the pin is not among them).
The binder recorded the conflict and refused the freeze
(`FREEZE_REFUSED`, stage `subject_verification`). Per the stage's
stop conditions, no scored run was attempted and no other subject or
endpoint was substituted. A battery run against the wrong subject —
or against a subject that is not served at all — is worse than no
run; the gate did the work it exists to do.

Stage 9's machinery criterion is met by the assembly and its tests:
the four components are composed from Stages 1–8 without modifying
them, the frozen STEP6 set is digest-verified, the account machinery
(closure, attributions, receipts, adjudication, examiner
re-derivation) is demonstrated end-to-end on scripted runs, and the
one live attempt stopped at exactly the gate the brief names, with
the refusal itself on the record.

## The assembly map (RECORD + BINDER + EVALUATOR + EXAMINER SURFACE)

| Component | Assembly |
|---|---|
| RECORD | Stage 1 `EventRecord` (hash-chained, fsynced), `ClosureWriter`, `validate_record` — one record per run under `stage9/runs/<package>/record.jsonl`. |
| BINDER | Stage 3 `Binder.attempt_freeze` over a `FrozenConfig` whose governed values are the STEP6 programme's parameters (envelope, per-instance ceilings, budgets, the frozen bar); `CaptureGate` admits every model capture against its own served identity; `ConfigAccess` is the only path by which governed values reach the evaluator; `OutputGate` admits each instance's result against a consumption receipt. |
| EVALUATOR | `engine.py` + `ops9.py` + `tools9.py`: the pinned driver's step engine and per-tree operations ported method-by-method (declared order, conditional steps, recovery kinds, budgets at step boundaries, lane-failure rule, stop finality), with every tool invocation a Stage 5 operation presented to the Stage 5 `Receiver`, every artefact field a Stage 2 provenance entry from the canonical writer, artefact construction by Stage 2's `ArtefactConstructor` under the frozen schema, failures attributed through Stage 6's `AttributionLedger`, and START/TERMINAL commitment receipts issued and collected through Stage 7. |
| EXAMINER SURFACE | `rederive.py`: independent re-derivation from the preserved record + frozen sources only — chain/anchor validation, its own implementation of the scoring rules, byte-for-byte settlement re-derivation, artefact construction verified from the record's provenance stream, capture files reconciled against their record links, failure/attribution/closure synchronisation, locations rendered from event identity (Stage 6 examiner). The Stage 4 checker contract issues the run's adjudication only where the examiner's re-derived settlement payload agrees byte-for-byte with the evaluator's constructed settlement. |

Two porting notes, stated plainly. (1) The old driver's
`reference_insert` is not ported: its ledger-coverage role is
discharged by Stage 2 construction — a field enters an artefact
only as a provenance entry gated by a Stage 5 presentation of the
insertion, and `artifact`/`evidence`, which the old driver assigned
literally (the DR-02 bypass), enter through the same path. On a
`return_once` retry the presentations rebuild identically and are
recognised (`ALREADY_SATISFIED`); the entries are read back, never
re-issued — the DR-01 repair, exercised in the tests. (2) Where the
old driver would have crashed on a missing extraction, Stage 9
records a refusal instead — the closure-always-completes ruling
applied to the port.

## The freeze

Vendored under `stage9/frozen/`, verified byte-for-byte against the
record's pins before any run, at every `TREE_TRIGGERED`, and again
by the examiner (`pins.py`; a mismatch refuses the run):

- Tree set `pilot_trees.json` — `cd367933c261d1172d024c65d4469c8880965cf954ccfcb7ae93edce30e24673` (PILOT-TREES-SUBSET-01; 13 instances: T01–T09, T09/FR-A, T09/FR-B, T09/FR-C, T09/FR-VALID).
- Data: PACKS-01 (amended) `b197e93e…`, EXTRACTOR-RULES-02 `7910ef9f…`, EXPECTED-01 `79db5c87…`, T09-01 `55a6c979…`, FIXTURES-01 `b02e0dd0…`.
- Corpus snapshot `sections.jsonl` — `b107e8926abc5fed…` (= attempt 3's own RUN_STARTED snapshot pin); manifest `c93eaa19…`.
- Programme utilities: `pilot_jcs.py` `8a131cfc…`, `rules_engine.py` `7a232915…`, `corpus_source.py` `520f36fd…`; adapter config `37e7c1ea…`.

The frozen STEP6 pass bar (first battery adjudication,
ALEX-STAGE6-BATTERY-ADJUDICATION-2026-11-17 §4) is carried in the
frozen configuration and applied as frozen: RUN_CLOSED; all 13
instances scored; zero GOVERNANCE-FAIL; zero NOT-SCORED; at most
two INVALID; trust commitments verified; examiner re-derivation
PASS. (No minimum subject PASS percentage.)

The frozen configuration's derived limit recomputes at G1 as the
plan requires: `transport_timeout_s = 600` under the
`reasoning_envelope` derivation (max_reasoning_tokens 36864 =
reasoning_budget 16384 + max completion 20480; min_throughput
64 tps; required 576 ≤ 600) — Alex's timeout ruling of 2026-11-17,
not the stock connector helper's 120 s cap (DR-21).

## Subject verification (K2) — the stop

- Subject (from the record, Alex's revised pin ruling 2026-11-17):
  **`openai/gpt-oss-20b`**. Endpoint class: NVIDIA NIM
  OpenAI-compatible, `https://integrate.api.nvidia.com/v1/chat/completions`,
  through the custom.nvidia connector's surrogate mechanism (the
  real credential never touches stage9 code, environment, or logs).
- Live evidence, recorded on the run record
  (`runs/STAGE9BATT-20261120-003/record.jsonl`, chain valid):
  `SUBJECT_VERIFICATION_EVIDENCE` — the one verification call
  (frozen retry shape; HTTP 410 is not a retryable class, so exactly
  one attempt) returned **HTTP_ERROR, status 410**; served model
  null; the corroborating live model list shows 33 models with the
  pin **not listed**.
- Disposition: `SUBJECT_VERIFICATION` (served_identity null) →
  `SUBJECT_CONFLICT` (pin/served mismatch, attribution UNKNOWN) →
  `FREEZE_REFUSED` at stage `subject_verification`. The freeze
  refused before any tree was triggered: no captures, no scored
  steps, no receipts, no settlement, no closure — no run exists to
  close. This is the brief's third stop condition in its strongest
  form: the specified subject is not served by the specified
  endpoint on the programme's key at all (410 Gone is the same
  disposition that left the first battery's Qwen attempt unscored).

## The two aborted assembly attempts (named, not hidden)

`STAGE9BATT-20261120-001` and `-002` are aborted assembly attempts,
each holding a one-event record (`RUN_IDENTITY_MINTED`, chain
valid). Both died on defects in the **new Stage 9 transport code**,
before any request reached the endpoint:

1. `-001`: the verification call ran before the freeze had set the
   envelope/retry (`TypeError`). Fix: the pre-freeze lane takes its
   parameters from the pinned adapter config artefact itself;
   governed values replace them after the freeze.
2. `-002`: the connector surrogate call used a wrong signature
   (`add_surrogate_to_request` takes the credential name and
   `allowed_hosts`, not provider/kind/format keywords). Fix: the
   call now mirrors the stock helper exactly, including its
   no-redirect opener.

Both fixes are regression-tested (the surrogate test exercises the
real request path with the credential function stubbed — the stub
lane that let both defects through is itself named here as the
testing gap that caused them). Neither attempt sent any HTTP
request; the only live calls ever made are the two harmless
`GET /v1/models` reads and the single verification call of the
`-003` freeze.

## The run

**No run.** Trees executed: none. The frozen bar was not applied to
a result because there is no result to apply it to; the subject's
score is not zero, not failed — it is **not measured**, because the
subject was not there to measure. Anything else would be a score
invented for a model that never answered.

What was demonstrated instead, on scripted subject lanes (Stage 9's
own tests, `stage9/tests/`): a three-instance run completing with
all checks PASS, receipts VERIFIED, closure COMPLETE, adjudication
issued on examiner agreement; a subject content failure attributed
MODEL as a single synchronised fact across FAILURE event,
attribution record, and closure account (examiner sync check
clean); an extraction-failure NOT-SCORED with its Stage 6
discrepancy preserving both positions; the T01 retry recognising
its insertions (exactly two provenance entries across two
attempts, no refusal); and a wrong-served-identity freeze refusal.

## Closure account, adjudication, re-derivation

For the live attempt there is no closure account and no
adjudication: no run was frozen, so nothing ran to close. The
refusal record (`-003`, 5 events, chain valid) is the complete
account of the attempt, and it is preserved in the package. The
examiner surface was demonstrated on the scripted runs above
(settlement agreement byte-for-byte, captures reconciled,
attribution synchronisation clean, artefact construction verified
from the provenance stream); against the live attempt it has only
the refusal record to re-derive, and that record re-derives
exactly as written.

## Register effect (proposed rows — stated exactly; the register
itself is the orchestrator's to file)

**Proposed DR-27** — "SUBJECT NOT SERVED AT STAGE 9 FREEZE
(2026-11-20): the pinned second subject `openai/gpt-oss-20b` is not
served by the NVIDIA endpoint on the programme's key — the
mandatory one-call K2 verification returned HTTP 410 and the model
is absent from the key's live model list (33 models). The Stage 9
freeze refused (SUBJECT_CONFLICT, attribution UNKNOWN); the battery
did not run and no substitution was made. Disposition: the pin
stands as ruled; a scored Stage 9 run awaits the subject being
served again, or a new pin ruling from the pin's authority. Stage
9's assembly is complete and re-runnable as built."

No prior register row is rewritten by this stage. DR-01…DR-26 stand
as Stage 8 left them.

## Counts

- Stage 9 tests: **11/11 PASS** (freeze integrity + tamper refusal,
  component wiring, wrong-subject freeze refusal, scripted
  full-account run, MODEL attribution, NOT-SCORED discrepancy,
  T01 retry recognition, transport lane + surrogate path, scoring
  shapes).
- Regressions, real trees: stage1 **68/68**, stage2 **27/27**,
  stage3 **38/38**, stage4 **36/36**, stage5 **30/30**, stage6
  **54/54**, stage7 **34/34**, stage8 **36/36** — all green; stages
  1–8 unmodified.
- Live calls: 2 model-list reads; 1 verification call (HTTP 410);
  0 scored model calls.

## What did not hold

- The subject: not served (above). The battery's end state — a
  scored, closed, adjudicated run — is therefore **not delivered**;
  everything except the subject's presence is.
- The Stage 7 receipts and Stage 4 adjudication are demonstrated
  under the harness's marked TEST issuer/anchor/authority fixtures
  (TEST-ISSUER-STAGE7, TEST-AUTHORITY-STAGE6), as Stages 6–7 left
  them: production anchor custody and production authority remain
  open exactly where those stages left them, and no result here
  should be read as a production adjudication or a Gate 2 act.
