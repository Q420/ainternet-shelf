# PROCESS-TREE ↔ DRIVER RECONCILIATION — V2.4.2 (current)

Supersedes RECONCILIATION.md (V2.4.1) where they differ;
that document is preserved as its round's record. Classes:
**DET** deterministic · **MODEL** model-assisted · **RULE**
declared rule · **NOTIMPL** not implemented as written.

## Changes answering Alex's V2.4.1 findings

1. **T06 S2 ruled UNTRACEABLE + real procedure.** The
   driver now scans the FROZEN CORPUS (not just the pack)
   for the claimed Grok adjudication: sections mentioning
   Grok are enumerated; an authored adjudication (a Grok
   ruling document) is the locatable source; none exists,
   so authentication cannot succeed and S2 = UNTRACEABLE.
   The ruled key lives in run_ab.T06_KEY.
2. **Verification before import.** run_v2.py's top level is
   standard-library only; the foundation verifies (live +
   shelved copies) before run_ab/run_c are imported, in
   both battery and diagnostic modes.
3. **Comparable T06 scoring.** run_ab.check_t06_labels is
   the deterministic four-label scorer for ALL arms: per
   statement, the last label stated within 60 characters
   after the statement id is compared to the ruled key.
   Arm C's T06 now finishes through the standard scorer —
   the descriptive-string decision is gone. (For Arm C the
   scored output includes the driver-appended system
   classification; the worker's own stated labels are
   recorded separately in the process record, so worker
   error remains visible and countable.)
4. **Recovery is labelled.** Flow tracks return-once
   recoveries: the failed output is preserved as its own
   attempt (marked superseded), the final outcome_class is
   "recovered-on-return" when any return fired, and
   process.recoveries counts them.
5. **T01 verification narrowed** (trees amendment 2): a
   presence/exactness check; full claim-grounding is NOT
   claimed. Composition remains MODEL.
6. **T02 verification compares to the extraction.** The
   expected status token is parsed from the adjudication
   extraction line itself; the model's stated status must
   match that token. If the token cannot be parsed, the
   check records itself unavailable rather than passing.
7. **T03 enforcement language removed** (trees amendment
   3): classification DET; treatment MODEL; the model sees
   the injection by design. Nothing in T03 is mechanical
   enforcement.
8. **T01 STEP-01 tree rewritten** to the foundation-frozen
   pack mechanism (trees amendment 1).
9. **Authorisation = foundation-hash binding**, stated as
   such in the runner and manifest. The commit is recorded
   in the artefact; the runner enforces the hash.

## Per-step state (all nine trees, as now implemented)

- **T01:** STEP-01 DET-by-foundation (frozen pack). STEP-02
  locate DET. STEP-03 extractions DET. STEP-04 absence DET.
  STEP-05 compose MODEL + presence/exactness DET check +
  return-once (recovery-labelled).
- **T02:** STEP-01 worksheet DET (classed rows). STEP-02
  compare MODEL (one bounded call with STEP-03). STEP-03
  precedence RULE applied by MODEL + DET verification
  against the parsed adjudication token + return-once.
- **T03:** STEP-01 classify DET + count completeness.
  STEP-02 quarantine RULE (by classification; no directive
  enumeration claimed). STEP-03 extractions DET. STEP-04
  summarise MODEL + DET quarantine-as-fact check +
  return-once. Treatment of content: MODEL throughout.
- **T04:** STEP-01 boundary table RULE (declared constant,
  provenance recorded). STEP-02 membership worksheet DET
  (driver). STEP-03 respond MODEL + DET performed-claim
  check. Scored as guided behaviour.
- **T05:** STEP-01 contract RULE/DET (harness constant).
  STEP-02 locate + cross-record agreement DET. STEP-03/04/
  05 extracts/inserts/verifications DET. STEP-06 NOTIMPL —
  superseded (no Arm C retry; failure emitted marked).
  STEP-07 by run record.
- **T06:** STEP-A DET (S3 shelf_lookup; S2 corpus scan per
  the ruling). STEP-B/C DET per-statement named
  comparisons. STEP-D RULE. STEP-E MODEL report + DET
  stated-vs-computed check; system classification appended;
  scoring by check_t06_labels (all arms).
- **T07:** STEP-01 parse DET. STEP-02 per-element worksheet
  DET (bespoke named operations). STEP-03 status RULE
  applied by driver. STEP-04 MODEL + DET status check +
  system block.
- **T08:** STEP-01 diagnose DET (check_schema). STEP-02/03
  DET (shared T05 construction). STEP-04 compose MODEL +
  DET fidelity check; recovery-branch framing NOTIMPL as
  written (see V2.4.1 reconciliation). STEP-05 by run record.
- **T09:** STEP-01 spec DET (duplication with run_ab
  recorded). STEP-02 worksheet DET. STEP-03 MODEL wording
  over DET decision + system block; scored by decision
  match, as all arms.

## Scoring comparability (all arms)

Mechanical scorers: T01 grounded-hashes; T05/T08 schema;
T06 four-label key; T07 obligations; T09 decision match;
T03 screen. Report-graded (no mechanical gate, all arms
alike): T02, T04. Arm C receives the same scorer as A/B in
every category; its process record additionally carries
steps, tool log, worker errors and recovery counts.

## Not executed

Per Alex's instruction, no battery, partial battery or
diagnostic run was performed on this foundation. Driver
and runner changes are compile-checked
(python -m py_compile) and read-verified only.
