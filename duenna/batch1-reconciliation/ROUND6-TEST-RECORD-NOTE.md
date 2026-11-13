# BATCH 1 RECONCILIATION — ROUND 6 TEST RECORD NOTE (VERDICT PRECEDENCE)

Date: 2026-11-13. Author: Remmy. For Alex's inspection
(pb-20261113-batch1-round5-inspection-response-alex, bridge
PB-ID pb-mwfgybb3-7-jn7h).

Alex substantially accepted Round 5 and withheld freeze for
one verdict-precedence defect: ob3_verdict() checked ASSERTIVE
before CONTRADICTORY/AMBIGUOUS, so a set containing both an
affirmative record and contradictory evidence elsewhere
returned FOUND. Round 6 changes ONLY the verdict function
and its controls; everything else is Round 5's, unchanged,
re-executed in this run. Round 5's suite and output are
preserved untouched as historical evidence.

Artefacts (this package):
- test_reconciliation_r6.py — sha256
  0b3838464e9f4e7de44082c5444f451e9e3fef0ea9f1b6b43ee6fe3167a91ca0
- RECONCILIATION-TEST-OUTPUT-R6.txt — sha256
  269761c08a2bd230670eca060ae7685b1884064e622fec517023b5e4b230fa84
- Result: 73/73 checks pass, against the pinned corpus
  snapshot and the frozen Batch 1 data files.

The correction, as executed:

1. Precedence reversed. ob3_verdict() now reads:
   any CONTRADICTORY or AMBIGUOUS -> UNKNOWN; else any
   ASSERTIVE -> FOUND; otherwise NOT FOUND. The verdict is
   conservative across the complete evidence set, not
   merely within individual sentences.

2. Mixed-class controls, all passing in the executed output:
   - ASSERTIVE + CONTRADICTORY -> UNKNOWN
   - ASSERTIVE + AMBIGUOUS -> UNKNOWN
   - ASSERTIVE alone -> FOUND (retained from Round 5)
   - NEGATED + PROSPECTIVE -> NOT FOUND
   The five Round 5 classifier controls and the remaining
   verdict controls are retained and passing.

3. The real corpus classes are unchanged — two subject
   sentences, both PROSPECTIVE — so the absence result is
   unchanged: NOT FOUND, and OB_TRUTH is reproduced from
   the computed lookup results.

Crusher's F-B1-2 retrieval remains outstanding; the original
dispatch returned nothing through his lane, and a clean
re-fire of the same authorised retrieval accompanies this
round. The reference_insert class B/C refusal case remains
a declared Batch 2 obligation, not executed here.
