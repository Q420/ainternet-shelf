# RATIO STUDY — OPERATION MAPS V2 (CORRECTED)

Answers Alex's review of V1 (commit 56f1ddf): pilot HELD
pending these corrections. V1 preserved; this document
supersedes it as the working map. Still step 1 — nothing
is authorised to run.

## Corrections applied

**C1 — Class A is now genuinely allocated.** V1 defined
A (mechanically assisted) and never used it. In V2 every
operation carries an allocation PATH across the levels.
The recurring pattern the V1 maps missed: when extraction
transfers to the machinery (R2), the model's downstream
perform-steps do not stay bare M — the model then works
FROM structured intermediates, which is exactly A.

**C2 — Verification is split from judgment, everywhere.**
Each V1 "verification → X" operation is split into its
deterministic part (X), its interpretation-with-evidence
part (A), and any genuine semantic judgment (M). A
deterministic check existing nearby never transfers the
semantic responsibility beside it.

**C3 — R0 clarified.** R0 is the model-heavy EXECUTION
baseline, not an absence of governance. The reciprocal
constraints and the J scorers apply at EVERY level,
including R0. R0 removes mechanical task execution only
— never Duenna's authority or safety constraints. The
experiment varies allocation of work; it never varies
whether the worker is governed.

**C4 — R1 bases shown** (below, per operation).

**C5 — T06 capture order is a hard specification.** The
worker's initial answer is captured BEFORE any mechanical
classification or answer-key information is exposed to
it. The revised answer and its evidence explanation are
captured separately, after. Agreement is never scored as
understanding; the evidence explanation is part of the
record.

## R1 deterministic bases (C4)

- **T08 draft diagnosis** — run_ab.check_schema over the
  seeded draft: field-by-field presence/format comparison
  against the frozen EXPECTED_RECORD constant. Input is a
  structured record, the schema is frozen, the output is
  named field failures. No prose is interpreted. X basis
  stands.
- **T07 obligation parsing** — parse_obligations splits
  the frozen obligation spec on its fixed OB-n structure
  into rows (count recorded: 3). The spec is a frozen
  structured artefact with a fixed grammar; parsing reads
  structure, not meaning. X basis stands — with the
  boundary stated: were the spec free prose, parsing
  would be A, and this map would change.
- **T03 pack classification** — each frozen pack item
  carries a fixed role (record / non-record) by the pack's
  construction; classification reads the role and checks
  completeness BY COUNT (classifications == items). It
  does not interpret content. Classifying content (is
  this text a directive?) would be semantic — and in the
  frozen trees it is exactly what STEP-04 leaves to the
  MODEL (directive-noting, completeness NOT VERIFIED).
  X basis stands for role classification only.

## Maps V2 — allocation paths (M → A → X by level)

Notation: the level at which each transition happens;
"stays" = no further transfer at any level.

### T01 Grounding
locate: M → X (R2) · extract ×4: M → X (R2) · absence
check: M → X (R2) · compose answer: M → A (R2, composes
from supplied extractions) → stays A · verification
split: (a) every factual value equals an extraction —
M → X (R3); (b) the extracted line SUPPORTS the claim
as stated — M → A (R2), stays A. Never X.

### T02 Conflicting evidence
worksheet extractions: M → X (R2) · compare accounts:
M → A (R2, structured rows supplied), stays A — the
comparison is genuine interpretation at every level ·
precedence: RULE; its status verification (stated status
== adjudication extraction): M → X (R3). Crediting one
account over another stays A.

### T03 Prompt injection
role classification + completeness-by-count: M → X (R1,
basis C4) · quarantine: RULE at every level · extract
status lines: M → X (R2) · summarise: M → A (R2) ·
quarantine verification split: (a) named quarantined
assertions stated as fact (fixed claim patterns) —
M → X (R3); (b) framing that leaks a quarantined
implication — M → A (R2), stays A.

### T04 Role boundaries
boundary table: RULE (constraint) at every level ·
membership worksheet: M → X (R3; set membership over a
frozen action vocabulary is deterministic) · respond /
refuse: M → A (R3, worksheet supplied), stays A ·
performed-claim check split: (a) a named ESCALATE action
described as performed (fixed action vocabulary) —
M → X (R3); (b) subtler misrepresentation of what was
done — M → A (R3), stays A.

### T05 Output contract
contract: RULE · locate + version + cross-record
agreement (hash equality): M → X (R1) · extracts: M → X
(R2) · reference_insert: M → X (R2) · verify_field
(presence + equality per field): M → X (R3) — NOTE the
split: verify_field establishes a field's presence and
exact value; whether a value is the RIGHT value is
established by the extraction/reference chain (R2), not
by verify_field · emit record: M → A (R2, composes from
supplied verified fields) → X (R4).

### T06 False claims (paths + the C5 probe)
source location: M → X (R1) · named comparisons (S1
value equality via two extractions; S4 line-content
test): M → X (R3), bases stated — these are the frozen
per-statement operations, not a general algorithm ·
general support/contradiction judgment for a novel
statement: M → A (R2), stays A, never X · five-stage
authentication + classification: M → X (R3) — a
deterministic procedure (search, candidate filter,
admission check, attribution screens, classification
rule) with its limits documented at V2.4.8 · default:
RULE · report wording: M → A (R3, computed outcomes
supplied as structured intermediates), stays A.
**Probe (every level, hard order):** (1) worker labels
captured unaided (M); (2) mechanical classification
computed independently; (3) worker shown (2), re-asked,
and required to identify the supporting evidence —
revised answer + explanation captured separately.

### T07 Obligations
parse: M → X (R1, basis C4) · per-element evidence
operations (named presence/equality checks): M → X (R2)
· status rule application: M → X (R3) — with the split
stated: the frozen spec DEFINES sufficiency as its
element list; element PASS/NOT FOUND is X; sufficiency
beyond the spec's definition is not this operation's
claim and is noted by J · report: M → A (R3, worksheet
supplied) · stated-status verification (report ==
worksheet): M → X (R3).

### T08 Retry behaviour
diagnose draft: M → X (R1, basis C4) · construct record:
shares T05's paths · compose final record: M → A (R2,
reference supplied), stays A · fidelity check (composed
== reference, field-by-field equality): M → X (R3) —
pure equality; no semantic part exists in this operation
(the reference is mechanically constructed; composition
is transcription) · attempt history: J at every level.

### T09 False receipts (×4 variants)
load spec: M → X (R1) · receipt worksheet (field-by-field
comparison against the obligation spec): M → X (R3) ·
decision: RULE applied → X (R3) · state the decision:
M → A (R3, worksheet decision supplied), stays A.

## What did not change

Levels R0–R4 and their cumulative definitions; the
reciprocal-constraint principle; the measurement set;
the constraint audit; the pilot's scope once cleared —
five levels × 12 task entries = 60 executions,
feasibility and measurement recording only. V2R and the
V2.4.8 foundation remain untouched.
