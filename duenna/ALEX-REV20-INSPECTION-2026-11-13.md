# Alex — Independent Inspection of Rev 20 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfns5as-j-barn · Relayed 2026-11-13 ~16:20 MST. Carries his ⟦ALEX-FINAL⟧ marker.
Headline: **NOT CLEARED / NOT YET FIT TO BUILD FROM** — D-T5a/D-T5b and the shared-flag contract (invariant, serialization, Stage 6/8 bindings) ACCEPTED as addressing the two Rev 19 MEDIUMs. **NEW HIGH — the flag contract does not cover every reap path:** HANDOFF_ACK codes 1–2 (kill + reap + exit), code 3 (reap + raw status in ABORT), Stage 5 Window 1 and Window 2 (kill/wait + reap + exit) are real reaping operations whose text specifies no flag transition and no exclusion rationale — while the contract claims the flags are the session's single reaping state, leaving two accounts of whether the child has been reaped. Required: account explicitly for **every** successful waitpid() call site — whether it sets `reaped` and holds the word, whether STATUS is prohibited because the path terminates through ABORT, and why no later path can reap or transmit again; any deliberately-excluded cleanup path needs its boundary defined and its terminal behaviour proven. Specification completeness, not an architecture change. D-T5 execution evidence remains Batch 4's, outstanding.

---

Rev 20 inspection — NOT CLEARED / NOT YET FIT TO BUILD FROM

I retrieved the exact Rev 20 pin and inspected the submitted amendments against the previous specification and the approved correction plan.

Pin verified

File: duenna/STAGE5-BUILD-SPEC-20.md

Commit: a017aca6

Git blob: 4740be8ff0c254d07620aa90b03ec6027caf04a8

Retrieved content: 6,188 newline-separated records.

Your reported SHA256 is e9f7792a…; I have not independently recomputed that file hash.

1. Rev 20 corrections accepted in substance

D-T5a — EOF-first: The specification now requires:

Child termination observed independently through the pidfd.

Channel drained, with no queued packet.

EOF established before PRE_RELEASE_CLOSE_BOUND expires.

EOF itself recorded as the closing event.

No STATUS transmission established through channel-log and launcher-side evidence, rather than inferred from non-receipt.

No RELEASE, gate action or issuance.

Correct unresolved classification and separation from PRE_RELEASE_ABORT_STATUS_UNREPORTED.

This addresses the first finding at the specification level.

D-T5b — queued STATUS: The control correctly requires the receiver to consume and validate the queued STATUS despite simultaneous HUP/EOF. Discarding it or classifying the attempt as launcher-lost fails the demonstration.

Shared flags: The four-rule contract incorporates both binding requirements:

sent => reaped, with a valid held raw wait-status word.

Serialized access to the shared flags, preventing concurrent stale-state decisions.

sent set before transmission.

Failed transmission never retried.

The Stage 6 gate-write-failure and Stage 8 collection paths now explicitly consult and use the shared flags. The already-discharged Stage 8 rule is also present.

I accept these corrections as addressing the two original MEDIUM findings in principle.

2. New finding — shared-flag contract does not cover every reap path
HIGH — OPEN

The contract describes reaped and sent as the launcher's single reaping/reporting state for the whole session. It also says that whichever path performs the wait sets reaped and holds the raw word.

However, other successful waitpid() paths remain outside that contract:

HANDOFF_ACK codes 1–2: the launcher kills and reaps the child, then exits.

HANDOFF_ACK code 3: the launcher reaps the already-terminated child and reports its raw status in ABORT.

Stage 5 Window 1: the launcher kills and reaps the waiting child before exiting.

Stage 5 Window 2: the launcher closes the gate, waits for the child to exit, reaps it, and exits.

These are real reaping operations. Their text does not specify the corresponding shared-flag transition or explain why they are excluded from the session-wide reaping state.

This matters because the contract now claims to govern every reporting path and defines reaped as the shared record of the session's reap. A successful wait outside that state machine leaves the specification with two different accounts of whether the child has been reaped.

Required correction: Account explicitly for every successful waitpid() call site. For each, specify whether it sets reaped and holds the raw word, whether STATUS is prohibited because the path terminates through ABORT, and why no later path can attempt another reap or transmission. If any cleanup path is deliberately outside the shared reporting machinery, define that boundary and prove its terminal behaviour.

This is a specification-completeness issue, not a request to change the adopted architecture.

3. Batch 4 evidence remains outstanding

D-T5a and D-T5b are specified demonstrations, not executed evidence. Their inclusion does not establish that the implementation actually handles the EOF/HUP ordering correctly.

The shared-flag contract also needs implementation-level evidence that the serialized execution path and one-time transitions hold under the actual launcher.

Disposition

D-T5a specification — Accepted.
D-T5b specification — Accepted.
Shared invariant and serialization — Accepted.
Stage 6 binding — Accepted.
Stage 8 binding — Accepted.
All-reap-path composition — OPEN — HIGH.
D-T5 execution evidence — Outstanding — Batch 4.
Overall Rev 20 — NOT CLEARED.
Batch 1 — CLEARED.
Batch 2 — CLOSED.
Build / Stage 6 — NOT AUTHORISED.

Please prepare a focused correction plan covering every waitpid() path, including the four identified above. Preserve Rev 20 unchanged and submit the next revision for inspection.

I can independently cross-check the complete call-site inventory and the revised state transitions once that plan is ready. No Crusher retrieval is needed; the relevant evidence is already available on Shelf.

⟦ALEX-FINAL⟧

Rev 20 is not approved as a build specification yet. The two original MEDIUM findings are materially corrected, but the new HIGH finding must be resolved before clearance.

— Alex
