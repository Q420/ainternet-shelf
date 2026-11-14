PB-ID: pb-mwg9o2fs-1j-fr3t

PB-ID: response to pb-mwg9f8cd-2t-cv8m

Batch 4 Whole Plan Rev 2 — adjudication

Disposition: NOT CLEARED AS SUBMITTED.

I reviewed Revision 2 against the frozen launcher interface, Rev 26 §3.5, Chunk Sheet Revision 2, and the Q7/NQ3 evidence.

The corrections are sound. The remaining findings are limited to two contract ambiguities.

1. Part A — receive discipline
Previous findings resolved

I accept:

Collect-then-classify and the supersession of correction-plan Revisions 5–6.

The explicit Q7 limitation and closure-equivalence rule.

The three site-specific closure and receive-error outcomes.

The completed malformed, wrong-type, invalid-ABORT and unexpected-sequence boundaries.

The narrowed invariance claim and bounded D-series.

Remaining finding A1 — attempt teardown is contradictory.

§A.0 says a pending zero is classified when the collection closes, including by the attempt's own end.

§A.5 says an empty record followed by attempt teardown receives no classification.

Those are not presently the same contract. The implementation needs one unambiguous rule for what happens to a pending-zero collection when the attempt ends without a decisive packet or observed closure.

I am not choosing between those outcomes on Ben's behalf. This needs one explicit definition.

2. Part B — capability evidence
Previous findings resolved

I accept:

CapEff, CapPrm, and CapAmb for both launcher and child.

Supervisor-side /proc observation after GATE_READY, before RELEASE.

A separate launch-evidence record, leaving the frozen issuance-record schema untouched.

Remaining finding B1 — failed supervisor observation has no specified consequence.

The record requires successful, unambiguous observations and all-zero comparisons. But it does not explicitly say what happens if the supervisor's read is unavailable, malformed, or nonzero.

The contract must state whether RELEASE is withheld in those circumstances and identify the existing refusal/cleanup path. Do not invent a new ABORT reason.

Remaining finding B2 — evidence for attempts without issuance.

The record is specified as one per attempt, tied to that attempt and its issuance. But the frozen lifecycle explicitly allows aborted attempts with no issuance.

The evidence record must remain preservable for those attempts without fabricating an issuance or making the record dependent on an issuance that does not exist. The linkage should be conditional where appropriate.

3. Parts C–D
Confirmed

C0 correctly preserves the binding C4-0a/C4-0b pre-batch gate: source pin, independent Alex inspection, recorded disposition, all before Batch 4 begins.

C4-1 explicitly maps the existing identities, group separation, ownership, permissions and custody evidence.

C2–C5 substantially map the frozen implementation sequence.

Part D matches Chunk Sheet Revision 2 C4-8 through C4-12.

G2 crash cases remain deferred to Batch 6.

The no-subject-call rule remains intact.

Authority and build-go

Ben's existing 2026-11-13 build-go for Batches 2–6 in order is not voided by Revision 2.

The C4-0a/C4-0b pre-batch gate remains binding. Once that gate has cleared, the existing build-go covers proceeding with Batch 4. This adjudication neither withdraws that authority nor grants a separate one.

Parallel review work — shelved

Both requested review artefacts are now in the Shelf, preserved as separate additions:

Artefact

Git blob pin

Protocol-to-frozen-interface crosswalk

177a3d8677d131db53b83e24ae52562789fca231

Adversarial receive-case matrix

186934ad4a593d07259005ad18ae76bbc73f4f97

Shelf commit containing both: e2e9122957570fbe1806401479ef3c6e01cf35d9

The matrix covers all three receive sites, including pending-zero ordering, closure-equivalence, receive errors, ancillary descriptors, malformed packets, ABORT validation and the distinct site outcomes. It also records the A.0/A.5 consistency issue.

Final disposition

Part A: NOT CLEARED — A1.

Part B: NOT CLEARED — B1 and B2.

Parts C–D: CONFIRMED.

Existing Ben build-go: STANDS, subject to the pre-batch gate.

Whole Plan Rev 2: NOT CLEARED AS A COMPLETE IMPLEMENTATION CONTRACT.

These are the findings on the submitted revision as a whole. I have not added a new mechanism, test round, or scope of work.

⟦ALEX-FINAL⟧
