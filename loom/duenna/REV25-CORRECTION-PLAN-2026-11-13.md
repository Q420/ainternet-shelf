# REV 25 CORRECTION PLAN — 2026-11-13 (narrow: C3-A2 only)

Drafted by Remmy, for Alex's inspection. Answers his Rev 25 inspection
(pb-mwfrdfbo-b-4bqm; NOT CLEARED on one MEDIUM). No other change is
proposed; the accepted interface (§3.2/§3.3), test groups (r)/(s),
and every other section are untouched. On his approval, Rev 26 is
drafted from the Rev 25 pin (ef197a63) incorporating exactly the
three corrections below. All earlier pins remain immutable.

## Verification performed before drafting (against the frozen source)

- PILOT-HARNESS-DESIGN-03 §2.3's event list was counted directly
  from the frozen text: **16 types** — RUN_STARTED, RUN_CLOSED,
  RUN_STOPPED; TREE_TRIGGERED, TREE_CLOSED; STEP_TRIGGERED,
  STEP_PROGRESS, TOOL_INVOKED, TOOL_RETURNED, MODEL_CALL_LINKED,
  CHECK_RESULT, **RECOVERY_TAKEN**, STEP_SATISFIED, STEP_FAILED,
  LEDGER_ENTRY, GOVERNANCE_EVENT. Alex's count is correct; the
  "seventeen" in Rev 25 §4(n) was carried from a summary, not from
  the frozen list.
- The built artefact is **not** defective: pilot_record.py's
  EVENT_TYPES already contains exactly these 16, RECOVERY_TAKEN
  included. The error is confined to Rev 25 §4(n)'s prose
  enumeration. (The record writer's module docstring also says
  "17 types"; the correction build will fix that comment to match
  its own list — noted here so the checkpoint can assert it.)
- The mismatch category's classification is stated in the frozen
  source itself, §6.3: "Corpus/pin integrity: … **A mismatch is
  not a per-tree event — it is a run stop (§6.4)**." The scoping
  below is that classification, not an inference.

## The three corrections (all inside §4(n))

1. **Count.** "the closed seventeen-type vocabulary" →
   "the closed sixteen-type vocabulary", and the enumeration is
   stated as 3 run-level + 2 tree-level + 11 step-level types.

2. **RECOVERY_TAKEN.** Added to the step-level list in §4(n)'s
   nullability rule: both `tree_id` and `step_id` strings (its
   §2.3 payload — the tree rule invoked, the failed attempt's
   event reference, the attempt number — is a step's).

3. **GOVERNANCE_EVENT, every kind mapped.** §4(n)'s governance
   clause is rewritten as an explicit three-row mapping, each row
   citing its frozen source:
   - `INSERT_REFUSED` (§2.3; §4.3) → the presenting step's
     context: both strings.
   - Pin or hash mismatch detected mid-run (§2.3; §6.2) →
     **both null**: §6.3 classifies the mismatch as "not a
     per-tree event — it is a run stop"; the event is run-scoped
     by the source's own classification.
   - `DECISION_STANDS` (T09; §2.3) → the deciding step's context:
     both strings.
   No other GOVERNANCE_EVENT kinds are declared in the frozen
   source; the C3-A2 assertion tests all 16 types and every row
   of this mapping.

## Footprint

Header, §0L, and §4(n) only. Rev 26 is submitted for Alex's
inspection on drafting; the Batch 3 correction build proceeds
only on his clearance of the Rev 26 pin.
