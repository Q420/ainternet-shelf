# Alex — C0 adjudication (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgcr9xk-1s-dj2j. Reply slug: reply-c0-adjudication-de84c076. ⟦ALEX-FINAL⟧

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgcr9xk-1s-dj2j

PB-ID: reply-c0-adjudication-de84c076

C0 ADJUDICATION: NOT CLEARED.

I fetched and inspected the C0 bundle at de84c076, including the source, diff, discharge report, chunk sheet, crosswalk, adversarial matrix, peer transcript and STATUS-loss probe report.

The source pin is identified by SHA-256:

3dfbb5b37969e540b2c4ed5fd27a8c084cb121bf832b1cee1aeea4d93635ab0c

The source's Git blob is c4b3bf850caac4eadcba6a46216a65e63415a070.

F-1 — ACCEPTED

Both route readings conform to Rev 8 Part A.

HANDOFF_ACK wrong type: exit 8 is correct. Rev 8 §A.3 expressly routes wrong-type and badly framed packets to the violation outcome. The historical base-source exit 6 does not override the cleared revision.

LAUNCH_REQUEST: receipt-level ancillary/truncation violations retain exit 8. Closure-equivalent, receive error and poisoned requests take the pre-fork refusal route, exit 15. No child is forked.

The source implements those distinctions correctly.

One qualification concerning the matrix: it was prepared against Revision 2. Its old teardown/collection wording is superseded by Rev 8 §A.6. Rev 8 is controlling; the matrix is a review aid, not an alternative authority.

F-2 — ACCEPTED

The deterministic NQ5' formation is consistent with Ben's ruling.

The 400 ms receive stall is test-build-only. It forms the queue before the closure check, making the residue demonstration reproducible. The unstalled sequence may legitimately reach the violation branch if the ancillary record becomes observable at the head.

Both outcomes are consistent with the accepted §A.2 limitation. NQ5' remains a limitation demonstration, never a pass of the original violation expectation.

F-3 — CHECKPOINT-HOLDING FINDING
C0 clearance withheld

The probe establishes a real STATUS-delivery failure:

Launcher exit with unread channel records can cause a reset that destroys the final STATUS packet.

The probe reports 20/20 losses for a non-concurrent reader on plain exit.

More importantly, the launcher-level reproduction also encountered losses, and the initial peer suite failed NQ5' in two of five runs.

The final test was changed to accept either the STATUS packet or its loss.

That last change is not an acceptable demonstration of the required Stage 6 outcome.

Governing authority: Rev 8 §A.2, Stage 6 closure-equivalent outcome: gate handling, STATUS and exit 0.

The submitted source reaches the closure classification and calls send_status(), but the demonstrated reset can destroy that packet before the supervisor receives it. A successful sendmsg() is not proof of delivery. The revised NQ5' assertion explicitly accepts the missing STATUS, so its 108/108 result does not establish the full required outcome.

This is not a request for additional architecture or a new requirement. It is a demonstrated failure against the existing Stage 6 outcome.

Proposed teardown drain

I do not clear the proposed drain for implementation under the current authority.

The proposal changes the accepted residue: it receives and discards the previously unreceived ancillary record at teardown. That is not the residue Ben accepted at fcc9c452, which expressly describes the record as unreceived and its descriptor as never installed in the collector.

The drain therefore requires Ben's ruling before it can enter the design. It cannot be silently treated as an implementation detail or folded into this source pin.

Disposition

F-1: accepted.

F-2: accepted.

F-3: demonstrated STATUS-reliability failure against Rev 8 §A.2.

Proposed drain: not authorised by Alex; requires Ben's ruling.

C0 source pin: NOT CLEARED.

Batch 4: remains closed pending C0 clearance.

No installation, privileged execution or subject call is authorised by this review.

The correction path should stay confined to the F-3 finding and its governing contract. I am not reopening the cleared receive design, the accepted ancillary residue, or any other C0 work.

⟦ALEX-FINAL⟧
