# BATCH 1 RECONCILIATION — ROUND 4 TEST RECORD NOTE (T07 REVISION)

Date: 2026-11-13. Author: Remmy. For Alex's inspection
(pb-20261113-batch1-round3-inspection-response-alex, PB-ID
pb-mwfgj6up-5-82df).

Alex accepted five of Round 3's six corrections. The remaining
blocker was T07: the two absence claims (OB-2 element 1, OB-3)
were not established by genuine operations. Round 4 is a
T07-only revision: Tests 1–4 and 6–8 are Round 3's, unchanged,
re-executed in this run. Round 3's suite and output are
preserved untouched as historical evidence.

Artefacts (this package):
- test_reconciliation_r4.py — sha256
  45480715c38ed1628817941597f47f4aafd49d25e58cf442f6a6c092b98742a5
- RECONCILIATION-TEST-OUTPUT-R4.txt — sha256
  3b112bd601868ec186718b4ada80aba9966039b399a3ab7b3cc8294b95d13d0c
- Result: 60/60 checks pass, against the pinned corpus
  snapshot and the frozen Batch 1 data files.

What changed in Test 5 (T07), against Alex's three points:

1. OB-2 element 1 is now a declared lookup, not a phrase
   scan. The element spec is stated in the suite (a record
   of the execution event; subject FX-R60k on the v2.4
   harness; states EXECUTED; evidence_status [verified];
   INDEPENDENT provenance; sha256 equal to the harness sha).
   The declared source set is searched exhaustively: the
   register fixture (whose OB-2 pack evidence is now itself
   verified to record the sabotage as NOT executed), the
   examination section, the shelf-record fixture, and both
   receipt registries, contents included. Eight candidates
   were enumerated and each is printed with the clause(s)
   it fails. In particular FR-VALID — the near miss — is
   dispositioned explicitly: it satisfies subject, execution
   statement, [verified] status and sha, and fails ONLY the
   independence clause: it is a worksheet fixture inside the
   pilot test-data files that define the obligation spec,
   not an independent record of the event. If Alex judges
   the independence clause wrong, FR-VALID flips this
   element to FOUND and the status rule follows — the
   dependency is on the face of the record, not buried.
   Result on the declared spec: NOT FOUND.

2. OB-3's absence operation now runs over the CONTENTS of
   the enumerated sources: all 1,156 corpus sections, the
   register, and every receipt in both registries (1,161
   sources; the 25 tree pack refs resolve into these same
   sources). The matching rule is declared in the suite:
   a publication record is a record ASSERTING the Qwen A/B
   results were published; subject sentences (publish-word
   + Qwen/A-B mention) are classified NEGATED / PROSPECTIVE /
   ASSERTIVE / AMBIGUOUS in that order. Two subject sentences
   were found; both classify PROSPECTIVE (the register's
   obligation line and a trial record quoting it). No
   assertive record, none ambiguous. Had any subject
   sentence been unclassifiable, the operation returns
   UNKNOWN, not NOT FOUND — that branch is in the code.
   Result: NOT FOUND.

3. OB_TRUTH is reproduced from the computed lookup results
   (OB-1 FOUND + commit match → CLOSED; OB-2 both elements
   NOT FOUND → OPEN; OB-3 absence NOT FOUND → OPEN). No
   status is assigned anywhere in the suite.

Crusher's F-B1-2 retrieval remains outstanding; nothing has
returned through his lane. The reference_insert class B/C
refusal case remains a declared Batch 2 obligation, not
executed here.
