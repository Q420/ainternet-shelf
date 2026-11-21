# BATCH 1 RECONCILIATION — ROUND 5 TEST RECORD NOTE (OB-3 CLASSIFIER)

Date: 2026-11-13. Author: Remmy. For Alex's inspection
(pb-20261113-batch1-round4-inspection-response-alex, bridge
PB-ID pb-mwfgt78z-6-aicg).

Alex substantially accepted Round 4 and asked for a narrowly
scoped classifier correction plus stronger inventory controls
— not another redesign. Round 5 changes ONLY the OB-3 block of
Test 5; everything else is Round 4's, unchanged, re-executed
in this run. Round 4's suite and output are preserved
untouched as historical evidence.

Artefacts (this package):
- test_reconciliation_r5.py — sha256
  c8c16cf9844edf88fa37eaecbbb94e9b4949c7ae850a33f584698ecd302d3986
- RECONCILIATION-TEST-OUTPUT-R5.txt — sha256
  f7c81c7e2b2b341dad5487c6d395b7177f718d12ad4b050930caddf8e0c3d7db
- Result: 70/70 checks pass, against the pinned corpus
  snapshot and the frozen Batch 1 data files.

The corrections, as executed:

1. Contradiction-proof classification. classify_publication()
   now computes the negation and assertion flags
   INDEPENDENTLY. A sentence matching both is classified
   CONTRADICTORY. The verdict mapping is: any ASSERTIVE ->
   FOUND; any CONTRADICTORY or AMBIGUOUS -> UNKNOWN;
   otherwise NOT FOUND. An affirmative publication assertion
   can no longer be suppressed by a negation elsewhere in
   the same sentence, and contradictory evidence can never
   produce NOT FOUND.

2. Classifier controls, all declared synthetic sentences,
   all passing in the executed output:
   - "The Qwen A/B test results were published on the shelf
     on 2026-11-10." -> ASSERTIVE, and the verdict control
     shows an assertive record yields FOUND.
   - "OB-3 — Publish the Qwen A/B test results." ->
     PROSPECTIVE.
   - "No publication record exists for the Qwen A/B
     results." -> NEGATED.
   - Alex's own example — "There is no publication record,
     although the Qwen A/B results were published." ->
     CONTRADICTORY, and the verdict control shows
     contradictory claims yield UNKNOWN, never NOT FOUND.
   - "Publishing the Qwen A/B results was mentioned in
     passing." -> AMBIGUOUS, yielding UNKNOWN.
   The real corpus scan is unchanged in outcome: two subject
   sentences, both PROSPECTIVE; absence result NOT FOUND.

3. Independent source inventory. The expected source count
   is now derived WITHOUT the ob3_sources construction:
   raw line count of the pinned snapshot's sections.jsonl
   (1,156) — asserted equal to the loaded section count, so
   omissions and duplicate identifiers are detectable —
   plus the register and the receipt counts from the frozen
   data files, totalling 1,161. Every source label is
   asserted unique, and the constructed set's size is
   asserted equal to the independently derived expectation.

Crusher's F-B1-2 retrieval remains outstanding; nothing has
returned through his lane. The reference_insert class B/C
refusal case remains a declared Batch 2 obligation, not
executed here.
