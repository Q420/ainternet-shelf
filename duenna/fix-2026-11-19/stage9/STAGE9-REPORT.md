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

## Run under Ben's subject ruling (2026-11-20)

**The ruling.** Ben ruled at 2026-11-20 05:27 MST, in his own
words: "Use any available NVIDIA model." That ruling is the
subject authority for this run. It supersedes waiting on the
pinned subject (`openai/gpt-oss-20b`, Alex's pin ruling
2026-11-17) whose unavailability refused the freeze at
STAGE9BATT-20261120-003 (DR-27). The comparability trade was
named to Ben before he ruled: a new subject starts a new
baseline rather than continuing attempt 3's measurement
history. The ruling, the list, and the selection are recorded
in the run record itself (the SUBJECT_VERIFICATION_EVIDENCE
event's `models_list`, carried through the lane's models_check
seam) and in the run directory's `subject-ruling.json`. The
driver is `run_battery_ruled.py` (new file): it rebinds the
assembly's one subject value — the same seam the stock driver
reads — and changes no assembly code of its own.

**The served list.** Read live at run time through the
connector's surrogate route (`transport.list_models()`, the
route the -003 verification used): 33 models — bigcode/
starcoder2-15b, fastino/gliner2-pii, google/gemma-3-12b-it,
google/gemma-3-4b-it, google/gemma-4-31b-it, meta/muse-
glimmer-30b, minimaxai/minimax-m3.1-flash, mistralai/
mistral-large-4-1t-a52b, moonshotai/kimi-k3.1-pro, nvidia/
ai-synthetic-video-detector, nvidia/cosmos-reason2-8b,
nvidia/embed-qa-4, nvidia/ising-calibration-1.5-31b, nvidia/
llama-3.1-nemoguard-8b-topic-control, nvidia/llama-3.1-
nemotron-safety-guard-8b-v3, nvidia/llama-3.2-nemoretriever-
1b-vlm-embed-v1, nvidia/llama-3.2-nv-embedqa-1b-v1, nvidia/
nemotron-3-embed-1b, nvidia/nemotron-3-nano-omni-30b-a3b-
reasoning, nvidia/nemotron-3-ultra-550b-a55b, nvidia/
nemotron-3.5-bolt-e4b, nvidia/nemotron-3.5-content-safety,
nvidia/nemotron-3.5-embed-1b, nvidia/nemotron-3.5-embed-8b,
nvidia/nemotron-3.5-lightning-30b-a3b, nvidia/nemotron-3.5-
super-vl-120b-a12b, nvidia/nv-embedqa-mistral-7b-v2, nvidia/
nvclip, nvidia/riva-translate-4b-instruct-v2, poolside/
laguna-xs-2.1, snowflake/arctic-embed-l, stepfun-ai/step-5-
preview, z-ai/glm-5.3-flash. The pin is absent; no
`openai/*` model of any kind is served. A second read at the
freeze confirmed the selection listed (33 models).

**The selection.** Preference step **(b)** — step (a) found
no served openai/gpt-oss model. Selected:
**`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`** — an
open-weight reasoning MoE, 30B total / 3B active: the only
served model that is simultaneously open-weight,
reasoning-named, and in the pin's scale class (gpt-oss-20b:
21B total / ~3.6B active). The selection, the list it was
made from, and the step that produced it are in the run
evidence, re-derivable from the driver code and the recorded
list.

**Verification (K2).** The mandatory one-call verification
named the selected model; the endpoint answered with
`served_model_id` identical to the requested id and a
non-empty response (34 prompt / 32 completion tokens). The
binder froze the run: config digest
adeb2ea53abd2a0895cef995e9c10ea339d68d8a48cdde29c9c2e7641d829c60.
The frozen STEP6 set and bar were verified exactly as at the
first freeze (tree set cd367933…, snapshot b107e892…, all 12
vendored digests matching).

**The aborted attempt -004, named plainly.** The first ruled
run (STAGE9BATT-20261120-004) verified and froze identically
(same config digest), then died mid-battery on a defect in
the Stage 9 port itself — not in the subject and not in any
staged component. The tree-declared constant fields of a
record artefact ("artifact", "evidence") were presented
under no step identity; Stage 5's operation identity refused
by raising ValueError, which escaped `issue_field`'s
(result, refusal) contract. T05 stopped at construction
(STEP-04, branch STOP); at T08 the failed step's failure
list was never populated, so the recovery step's inputs
builder raised KeyError outside any guard and crashed the
process, leaving -004's record unclosed at 397 events
(T01–T04, T06, T07 COMPLETED; T05 STOPPED; T08 unclosed).
No scripted test had ever run a record-constructing tree —
the stub-lane masking pattern this programme has met before.
Two minimal fixes, both in stage9 code, both reported here:
(1) `ops9._construct` now presents the constants under the
constructing step's identity (their basis still records
them as tree-declared constants); (2) `engine._model_step`
now gives its inputs builder the same recorded-governance-
failure treatment `_tool_step` already gave its handler —
a harness-side exception is recorded, never a crashed run.
Three regression tests pin the corrected paths (T05 and T08
scripted constructions complete with full accounts; a
raising MODEL-step builder is recorded, not raised). The
-004 record stands as the aborted attempt's evidence;
nothing in it was resumed or re-used. The battery was then
run once more, whole, as -005.

**The run (STAGE9BATT-20261120-005).** One bounded execution,
2026-11-20T12:34:58Z–12:37:03Z, 754 record events, 14 model
calls (14 attempts, no retries fired). All 13 frozen
instances executed and closed COMPLETED. Verdicts: **PASS**
T03, T04, T05, T06, T08, T09/FR-VALID (6); **SUBJECT-FAIL**
T01 (1); **NOT-SCORED** T02, T07, T09, T09/FR-A, T09/FR-B,
T09/FR-C (6); GOVERNANCE-FAIL 0; INVALID 0.

**The subject's result against the frozen bar, plainly: the
subject did not pass.** The frozen STEP6 bar (first battery
adjudication §4) applied as frozen: run_closed ✓,
all_instances_scored ✓, zero_governance_fail ✓,
at_most_two_invalid ✓, trust_commitments_verified ✓,
examiner_rederivation_pass ✓, **zero_not_scored ✗** — six
NOT-SCORED instances fail that one criterion, and the bar
fails with it. The six NOT-SCORED are the DR-14/15/17 shape:
the checkers could not extract the stated facts from the
subject's responses (the answers are preserved in the
captures; they do not carry the prescribed format lines in
extractable form). Each is attributed **SYSTEM** under
Stage 6's causal table, with a Stage 6 discrepancy
preserving both positions — the checker's extraction
failure and the subject's raw output — so the examiner can
see exactly what the subject said. T01's SUBJECT-FAIL is a
content failure (the stated fact was extracted and was
wrong), attributed **MODEL**. Attributions stand as single
synchronised facts: the examiner's re-derivation reports
zero attribution-sync problems.

**Closure, receipts, adjudication.** Closure account
**COMPLETE** under the five rulings; Stage 1 validation of
the final record: terminal_record PASS, account_completeness
PASS, chain_validity PASS. Both Stage 7 receipts (START,
TERMINAL) derive **VERIFIED** under the pinned TEST anchor;
no unrecorded package entries. The Stage 4 adjudication was
**issued** (validation ACCEPTED) only on the examiner
surface's agreement — `examiner_agreement: true`, the
re-derived settlement byte-identical to the constructed one
(verdict: "preserved sha=3658995bc0bb").

**Re-derivation of this run, demonstrated.** After the run,
in a fresh process, from the record and the frozen sources
alone: `rederive.derive_full()` reproduced the run's own
`examiner-report.json` **exactly** (whole-dict equality);
verdicts identical; attribution_sync_problems none; capture
problems none; an independent Stage 1 `validate_record`
re-run returned PASS on all three checks. The account is
not merely asserted checkable — it was checked, again, from
outside the run.

**Proposed DR-27 disposition update (exact text for the
orchestrator to file).** Replace DR-27's Repair/disposition
and Status with:

> Repair/disposition (updated 2026-11-20): Ben ruled at
> 2026-11-20 05:27 MST — "Use any available NVIDIA model" —
> superseding, for the Stage 9 run, waiting on the pin.
> Under that ruling the battery ran end to end
> (STAGE9BATT-20261120-005) against
> nvidia/nemotron-3-nano-omni-30b-a3b-reasoning, selected
> from the key's live list (33 models; no openai/gpt-oss
> model served) at preference step (b), the closest served
> open-weight reasoning model in class/scale to the pin.
> The run completed with a complete, attributed, checkable
> account (closure COMPLETE; receipts VERIFIED;
> adjudication issued on examiner re-derivation agreement;
> the full record independently re-derived). The subject
> did not pass the frozen STEP6 bar — PASS 6, SUBJECT-FAIL
> 1 (T01, MODEL), NOT-SCORED 6 (checker extraction,
> SYSTEM, discrepancies preserved) — failing the bar's
> zero_not_scored criterion. A first ruled attempt
> (STAGE9BATT-20261120-004) aborted on a defect in the
> Stage 9 port's record construction, fixed and
> regression-tested before the -005 run; its record stands
> unclosed as the aborted attempt's evidence. The pin
> stands as ruled for any future measurement continuous
> with attempt 3's history; the -005 run is a new baseline
> under Ben's ruling, not a re-measurement of the pinned
> subject. Status: the scored-run blockage is RESOLVED by
> the ruling and the -005 run; DR-27 remains as the record
> of the pin's unavailability.

**Counts after the run.** Stage 9 tests: **14/14 PASS**
(the 11 of the first build, plus the 3 record-construction
regressions above). Regressions, real trees, re-run this
session: stage1 **68/68**, stage2 **27/27**, stage3
**38/38**, stage4 **36/36**, stage5 **30/30**, stage6
**54/54**, stage7 **34/34**, stage8 **36/36** — all green;
stages 1–8 unmodified. Stage 9 code changes for this run,
complete list: `run_battery_ruled.py` (new driver),
`ops9.py` (_construct presenting step), `engine.py`
(_model_step builder guard), `tests/test_stage9.py` (+3
tests). The receipts and adjudication stand under the
harness's marked TEST fixtures, as before; nothing here is
a Gate 2 act.

## Correction loop (2026-11-20) — Gate 1 FAIL returned, two corrections, the checker audit, and a rerun

Vane's Gate 1 verdict on the Stage 9 package (filed by her @
85600a41) was FAIL, returning the stage for two bounded
corrections, with the substantive -005 result expressly
preserved: the ruled subject did not pass the frozen STEP6 bar,
and neither correction may change that. Ben additionally
ordered the checker/instruction audit in the same loop. This
section is the loop's account. Stages 1–8 unmodified; the
frozen STEP6 set unmodified (digest cd367933…, verified);
runs -004 and -005 untouched.

### Part A — Frozen subject inconsistency (correction 1)

**Diagnosis.** `build_draft` copies the draft's envelope
verbatim from the pinned adapter config
(`frozen/src/actions-adapter-config.json`), whose
`envelope.model` is the pin, `openai/gpt-oss-20b`. Every other
subject field in the draft is built from the assembly's subject
value — the one the ruled driver rebinds — so a run frozen
under Ben's ruling carried two subjects in one configuration:
the pin in `values.envelope.model`, the ruled subject in
`subject_pin`, `subject_surfaces` and
`values.subject_model_id`. The binder's G1 surface check
(DR-03) sees only the pin and the surfaces; it cannot see
inside the governed values. The transport never read the
envelope's model field (it builds each request from its own
`model_id`, and refuses a served identity that differs), which
is why the calls were right while the frozen configuration was
wrong.

**Fix (chosen: synchronize; the alternative — removing the
field — rejected).** `build_draft` now sets
`envelope["model"]` to the run's subject at draft
construction, before the binder freezes, so the FrozenConfig
digest covers the synchronized value. The envelope is the
run's transport template and its model field is a subject
surface of the run; the pinned artefact's value is the pin
because the pinned programme's subject was the pin.
Synchronizing keeps the subject stated once, correctly, on
every surface; removing the field would change the pinned
envelope's shape and leave the transport surface silent about
the subject instead. Under the unmodified pin the
synchronization is a no-op (regression-tested: the pin draft's
envelope is the pinned artefact's, field for field).

**Fail-closed check.** The assembly now verifies the whole
draft before the freeze (`_draft_subject_problems`): every
subject-naming field (`subject_pin`, both surfaces,
`values.subject_model_id`, `values.envelope.model`) must name
exactly one subject, and it must be the transport lane's
subject. A violation is refused before the freeze and before
any scored call, recorded under a minted run identity in the
binder's own refusal shape (RUN_IDENTITY_MINTED,
SUBJECT_CONFLICT with attribution UNKNOWN, FREEZE_REFUSED) —
regression-tested, including a lane that would serve the pin
at K2 while requesting a different model, which the binder's
checks alone would have frozen.

**The rerun — STAGE9BATT-20261120-006.** The complete battery,
rerun once under the corrected machinery: same ruled subject
(`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, Ben's
2026-11-20 05:27 MST ruling; selected at preference step (b)
from the live list, 33 served, no `openai/*` served; K2
re-verified live inside the freeze), same frozen STEP6 trees
and bar (digests unchanged), one bounded execution, no
selective retries. The frozen configuration is internally
consistent — pin, surfaces, `subject_model_id` and
`envelope.model` all name the ruled subject; config digest
54a271a1bfdd15c4edb1bc5b6d2476daa1cd227c3e8fff5e87759741cf7b36be
(changed from -005's adeb2ea5…, as it must: the synchronized
envelope is inside the digest). 751 events, terminal CLOSURE;
14 model calls; closure COMPLETE; both receipts VERIFIED;
adjudication issued on examiner agreement (validation
ACCEPTED); Stage 1 validation PASS ×3; the examiner surface,
run standalone in a fresh process, re-derives all 13 verdicts
identically, with zero attribution-sync problems and zero
capture problems.

**Result against the bar, and against -005.** The subject did
not pass the frozen bar — the same outcome as -005, failing
the same single criterion, `zero_not_scored`:

| | PASS | SUBJECT-FAIL | NOT-SCORED |
|---|---|---|---|
| -005 | 6 (T03 T04 T05 T06 T08 T09/FR-VALID) | 1 (T01) | 6 (T02 T07 T09 FR-A FR-B FR-C) |
| -006 | 7 (T03 T04 T05 T06 T07 T08 T09) | 1 (T01) | 5 (T02 FR-A FR-B FR-C T09/FR-VALID) |

The per-instance differences are live-model variance on the
*unrevised* exam's format guessing, and they cut both ways:
T07 and base T09 passed this time because the subject happened
to produce the prescribed-looking format; T09/FR-VALID, which
passed in -005, produced no `DECISION:` line this time and is
NOT-SCORED. That variance is itself the Part C finding,
demonstrated live a second time. It is reported, not smoothed:
the bar outcome — the substantive result Vane preserved — is
identical.

### Part B — Builder-exception misclassification (correction 2)

**The emitter map** (every `STEP_FAILED` append in engine.py;
ops9.py appends none directly — its check dicts supply
`failure_class` values to emitters 3 and 7):

| # | Site | Trigger | failure_class | `exception` field | `kind` |
|---|---|---|---|---|---|
| 1 | `_run_step` budget conversion | a satisfied step over its budget | ADAPTER_TIMEOUT (MODEL) / GOVERNANCE_FAILURE (TOOL) | no | BUDGET_CONVERSION |
| 2 | `_tool_step` handler | a TOOL/RULE op raises | GOVERNANCE_FAILURE | **yes** | — |
| 3 | `_tool_step` check failure | checker returns failed | checker's, default GOVERNANCE_FAILURE | no | — |
| 4 | `_model_step` inputs builder | a MODEL op's `*_inputs` raises (the -004 correction) | GOVERNANCE_FAILURE | **yes** | — |
| 5 | `_model_step` adapter failure | transport `complete()` fails | ADAPTER_FAILURE | no | — |
| 6 | `_model_step` capture refused | CaptureGate refusal | ADAPTER_FAILURE | no | — |
| 7 | `_model_step` check failure | checker returns failed | checker's, default SUBJECT_FAILURE | no | — |

Check dicts carrying GOVERNANCE_FAILURE into emitters 3/7:
`t05_locate_artifact`, `t05_construct_record`,
`t08_construct_validate` (TOOL, refusal paths) and
`t02_apply_precedence_check`, `t06_report_check`,
`t09_state_decision_check` (MODEL). ops9 also appends one
GOVERNANCE_EVENT directly (DECISION_STANDS, T09); scoring
treats only INSERT_REFUSED governance events as signals —
unchanged.

**The defect.** Scoring (and, identically, the examiner's
re-derivation) recognised a STEP_FAILED GOVERNANCE_FAILURE as
a governance signal only for TOOL/RULE steps. Emitter 4's
events — a harness-side exception on a MODEL step — fell into
the model-failure classification, where the T02 regression
case classified NOT-SCORED. The handler's stated semantics
("a harness-side exception is a governance failure of the
instance") were recorded on the record and then not honoured
by either scoring surface.

**The fix.** In both `scoring.py` and `rederive.py`,
identically: a STEP_FAILED with failure_class GOVERNANCE_FAILURE
that carries an `exception` (emitters 2 and 4 — the handler
paths that record the exception itself) is a governance signal
**regardless of step type**, yielding GOVERNANCE-FAIL for the
instance (scoring names the signal HARNESS_EXCEPTION).
Checker-emitted GOVERNANCE_FAILURE (emitter 7, no exception)
is expressly NOT captured: a checker's class is its judgment
of a response and stays in the model-failure path. Ordinary
MODEL content failures and ADAPTER_TIMEOUT budget conversions
are unchanged, and evaluator/examiner agreement is preserved
(the extended regression run's adjudication issued on
byte-for-byte agreement).

**Tests.** The T02 builder-boom regression now asserts the
resulting verdict (GOVERNANCE-FAIL), its attribution (SYSTEM,
via the failure account), and the mirror verdict through
`rederive.derive_full`. Two scoring-rule unit tests pin both
sides of the discriminator: MODEL step + GOVERNANCE_FAILURE +
exception → GOVERNANCE-FAIL; MODEL step + GOVERNANCE_FAILURE
without exception → NOT-SCORED (the -005 shape).

**The -005 re-scoring statement (headline).** -005 was
re-scored with the corrected `scoring.py` and re-derived with
the corrected `rederive.py`, read-only, in this session.
**No -005 verdict changes.** All 13 re-scored verdicts and all
13 re-derived verdicts are identical to the stored summary and
examiner report, key for key; the re-derived bar still fails
only `zero_not_scored`. Reason, established from the record:
-005's six GOVERNANCE_FAILURE STEP_FAILED events (T02-STEP-03
×2; T09-STEP-03 on T09, FR-A, FR-B, FR-C) carry **no**
`exception` field — they are emitter 7, the check-failure
path, with the class supplied by the T02/T09 checkers — so the
new rule does not capture them, by design. Vane's preservation
constraint holds in full.

### Part C — Checker/instruction audit and the proposed exam revision

Full audit: `exam-revision-1/AUDIT.md`. Summary: all six
NOT-SCORED instances are class **(i)** — the format the
checker extracts was never prescribed in the delivered
instructions. T02's text mentions no format at all; T07's and
T09's invoke "the required format" without stating it. In
every case the subject's preserved response contains the
correct fact in an unlabelled shape (T02 attempt 2 states OPEN
in prose; T07 states all three statuses correctly, missing
only the unprescribed space in "OB-1:CLOSED"; the T09 family
states CLOSE/REJECT as a bare first line). No instance is
class (iii); T07 carries a class-(ii) aspect (exact-substring
brittleness on an unprescribed whitespace detail).

The revision (`exam-revision-1/pilot_trees.revised.json`)
takes one direction for all three steps — **prescribe in the
instructions exactly what the checker extracts** — changing
exactly three step texts and nothing else in the tree set
(test-verified). The checkers, the substantive demands, the
facts and the values are unchanged. Scripted-lane tests
(`exam-revision-1/test_exam_revision.py`, 10/10) demonstrate
all six instances markable: compliant+correct passes;
compliant-format+wrong-fact fails on content (SUBJECT-FAIL
classification for T02/T09; for T07 a judged lines-match
content failure — the frozen scoring vocabulary still calls a
failed T07 lines-match NOT-SCORED, stated in the audit rather
than smoothed over); and each preserved -005 response,
reformatted only by applying the now-prescribed label, passes
the unmodified checker. **No live run of the revised exam has
been made**: it is a proposed new freeze for Gate 1, and
adopting it means a new tree-set digest under the battery's
freeze discipline.

### Part D — Examination by execution

`EXAMINATION-RUNBOOK.md`: exact commands for every stage
suite, the revision suite, freeze verification, the standalone
re-derivation of both preserved runs, and the -005 re-scoring
reproduction, with expected counts and verdicts stated for
each.

### Counts (all re-run this session, orchestrator's runs)

Stages 1–8 unchanged and green: 68 / 27 / 38 / 36 / 30 / 54 /
34 / 36. Stage 9: **20/20** (14 prior + 4 subject-consistency
+ 2 scoring-rule; the builder-exception test extended in
place). Exam revision 1: **10/10**. The -006 rerun's counts
are in Part A above.

### What did not hold

- The new HARNESS_EXCEPTION path did not fire during -006 (no
  harness-side exception occurred in the live run); its
  demonstration is the scripted tests, not the live record.
- The rerun did not reproduce -005 instance-for-instance (four
  instances differ) — live-model variance on the unrevised
  exam, reported in Part A. The bar outcome is unchanged.
- The exam revision cures the format contract only on paper
  until Gate 1 accepts it and a run is frozen under it; the
  frozen exam that -005 and -006 sat still contains the
  defect, by design of the freeze.

### Proposed register text (for the orchestrator to file)

**Correction 1 — proposed new entry.** Defect: a run frozen
under a subject ruling produced a FrozenConfig naming two
subjects — the ruled subject in the pin, surfaces and
`subject_model_id`, the original pin in
`values.envelope.model`, copied verbatim from the pinned
adapter config; the binder's surface check cannot see inside
the governed values, and the evaluator's consumption receipts
inherited the inconsistency (Stage 9 Gate 1, Vane, run
STAGE9BATT-20261120-005). Evidence: -005 frozen-config.json
(`values/envelope/model` = openai/gpt-oss-20b) against its
captures (14/14 requests naming the ruled subject). Attribution:
SYSTEM. Repair/disposition: `build_draft` synchronizes the
envelope's model field to the run's subject before the freeze
digest is taken; the assembly refuses, before any scored call
and on the record, any draft whose subject fields disagree or
differ from the lane's subject; regression-tested (pin freeze
unchanged; ruled freeze consistent; inconsistent draft
refused); the battery reran end to end as
STAGE9BATT-20261120-006 under a consistent freeze with the
bar outcome unchanged. Status: correction built and
demonstrated; Gate 1 re-examination pending.

**Correction 2 — proposed new entry.** Defect: a MODEL step's
inputs-builder exception, recorded by the engine's handler as
STEP_FAILED/GOVERNANCE_FAILURE (the -004 correction), was not
recognised as a governance signal by scoring or by the
examiner's re-derivation — both honoured that class only on
TOOL/RULE steps — so the instance could score NOT-SCORED
instead of GOVERNANCE-FAIL; the regression test asserted run
completion only, not the verdict (Stage 9 Gate 1, Vane).
Evidence: scoring.py / rederive.py governance scans against
engine.py's handler paths; the T02 builder-boom case.
Attribution: SYSTEM. Repair/disposition: both scoring
surfaces, identically, now treat a GOVERNANCE_FAILURE
STEP_FAILED carrying a recorded exception as a governance
signal on any step type; checker-emitted classes without an
exception are expressly excluded; the regression asserts
verdict (GOVERNANCE-FAIL), attribution (SYSTEM) and the
examiner mirror; -005 re-scored and re-derived under the
corrected rules with **no verdict changed** (its
GOVERNANCE_FAILURE events are checker-emitted, emitter 7, no
exception recorded). Status: correction built and
demonstrated; Gate 1 re-examination pending.

The receipts and adjudication stand under the harness's
marked TEST fixtures, as before; nothing in this loop is a
Gate 2 act.
