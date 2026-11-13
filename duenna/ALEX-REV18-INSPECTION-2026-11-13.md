# Alex — Independent Inspection of Rev 18 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfn7z0c-f-h2xi · Relayed 2026-11-13 ~16:04 MST.
Headline: **NOT CLEARED / NOT YET FIT TO BUILD FROM** — a focused correction, not a reopening. Plan Rev 4's changes are substantially present (readiness, catalogue, terminal rules, S3–S6 table, clarifications, SIGCHLD, D-T1/T3b/T4 all verified in the text). **HIGH: class-T ABORT has no defined UNREAPED-child path** — the spec defines the already-reaped and already-sent cases, but the ordinary D-T2/D-T3a case (ABORT arrives before the launcher has waitpid()ed) never assigns the reap: the expected STATUS is assumed into existence. Required: on class-T receipt while unreaped/unsent — reap exactly once, validate the raw status, send exactly one STATUS, never GATE_READY/release; waitpid interruption/error handling and the reaped/sent flag discipline specified. **MEDIUM: EOF before STATUS under class T has no explicit terminal classification** — the UNREPORTED outcome is specified only for the 5 s bound; EOF-first needs its own outcome (launcher loss observed, termination independently observed, exit status unreported, classification unresolved, no issuance), not conflated with the timeout case. He fetched blob 706483ef… and did not recompute the file SHA-256.

---

Rev 18 independent inspection — NOT CLEARED / NOT YET FIT TO BUILD FROM.

I retrieved duenna/STAGE5-BUILD-SPEC-18.md at commit a0f33fb4, exact Git blob 706483efd27bab03f9ab3956c21dd6ee6f983d85.

I inspected the revised §3.5 process sequence, readiness contract, message catalogue, terminal-observation rules, S3–S6 state table, §0D incorporation record, and D-T1 through D-T4. The approved Plan Rev 4 changes are substantially present. The remaining issues concern the actual class-T execution path.

1. HIGH — Class-T ABORT has no defined unreaped-child path

The normal D-T2/D-T3a scenario is:

ACK 0 has been sent.

The launcher has dropped privilege and is settling, or has sent GATE_READY.

The child terminates.

The supervisor observes termination through the pidfd and sends class-T ABORT.

The launcher must reap the child and send exactly one STATUS.

The specification does not define step 5 when the launcher has not already reaped the child and has not already sent STATUS.

The class-T paragraph currently says:

"a class-T ABORT after it reaped draws its one STATUS (never a second reaping); after it sent, the ABORT is a reporting no-op (never a second STATUS)."

Those are the already-reaped and already-sent cases. Neither defines the ordinary case in which the supervisor's observation and ABORT arrive before the launcher has called waitpid().

The earlier sequence only explicitly assigns waitpid() to pre-handoff cleanup and Stage 8. There is no specified pre-release wait/reap transition on receipt of class-T ABORT.

This leaves the central D-T2/D-T3a path under-specified. The expected STATUS cannot simply be assumed into existence.

Required correction: explicitly define the launcher's action on receiving class-T ABORT while unreaped and unsent: reap exactly once, obtain and validate the raw wait status, send exactly one STATUS, and never send GATE_READY or perform release. Define the waitpid interruption/error handling and how the reaped/sent flags prevent duplicate work. Preserve the already-approved race rules.

2. MEDIUM — EOF before STATUS has no explicit terminal classification

Class T says the channel closes on STATUS recording, EOF, or the five-second bound. But its explicit PRE_RELEASE_ABORT_STATUS_UNREPORTED outcome is only specified when neither STATUS nor EOF arrives by the bound.

If EOF arrives first and no STATUS was received, the channel closes, but the record's resulting classification and required evidence are not explicitly defined.

That case needs an explicit outcome: launcher loss observed, child termination independently observed, exit status unreported, classification unresolved, no issuance. It should not be conflated with the five-second timeout case.

Cross-check disposition

S3: readiness and ACK 0–3 paths are represented, including the distinct ACK 3 reap-only route.

S4–S5: termination observation, class-T commitment, RELEASE prohibition and crossing GATE_READY handling are represented. The unreaped-child action remains the blocker above.

S6: gate-write outcomes and the poll-to-send uncertainty are represented.

Class T/F: the received-versus-validated STATUS clarification is incorporated. The missing unreaped branch and EOF-without-STATUS outcome remain.

D-T1: expected ACK 3/reap/report path is represented.

D-T2 and D-T3a: expected final STATUS depends on the missing class-T reap action.

D-T3b: the UNKNOWN relative-timing requirement is represented.

D-T4: EPIPE, SIGPIPE handling, mutually exclusive gate reports and FAILED actuation are represented.

The SIGCHLD establishment, readiness deadline, fail-closed poll outcomes, raw status validation, and signal handling are incorporated in the inspected text. The demonstrations remain future Batch 4 evidence, not passed tests.

I have not independently recomputed the submitted SHA256 claim; the exact fetched Git blob is recorded above.

Disposition: Rev 18 remains NOT CLEARED. This is a focused correction, not a reason to reopen the approved architecture or Plan Rev 4. Rev 17 and the approved plan remain untouched. Batch 1 remains CLEARED; Batch 2 remains CLOSED; no implementation, build, or Stage 6 authorisation follows from this inspection.

No Crusher retrieval is needed: the relevant specification and approved plan are available on the Shelf.

I can take the next independent pass over the corrected class-T transition table and its EOF/error cases, so you don't have to carry that cross-check as well.

— Alex
