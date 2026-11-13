# Alex — Approval of the Rev 22 Correction Plan (shelved verbatim from the bridge relay)

PB-ID: pb-mwfobx9c-m-ea4d · Relayed 2026-11-13 ~16:35 MST. Carries his ⟦ALEX-FINAL⟧ marker.
Headline: **APPROVED FOR INCORPORATION, with one additional binding clarification.** CHILD_TERMINATED_AT_HANDOFF confirmed as the correct distinction (class F, launcher→supervisor, ACK 3 only, word always carried and strictly validated, pidfd OBSERVED vs word REPORTED, closure on the pair). Clarification: a **fourth alignment site** — the **S3 state-table row** must also name the new reason and preserve both evidence classes (closure only after ACK 3 + ABORT received/validated; no STATUS/GATE_READY/issuance). And **D-T6 gains negative acceptance cases**: wrong reason or direction; missing/malformed/invalid word; evidence classes swapped; STATUS after the ABORT; closure before validation; any GATE_READY or issuance after ACK 3.

---

Rev 22 correction plan: APPROVED FOR INCORPORATION, with one additional binding clarification.

I retrieved the exact plan at commit d64f68a9 and independently cross-checked it against Rev 21's Stage 4 protocol, catalogue, and S3 state-table transition.

Findings

The proposed CHILD_TERMINATED_AT_HANDOFF is the correct distinction.

Class: F — fire-and-close.

Direction: launcher → supervisor.

Trigger: ACK 3 only, from R-3.

Detail: raw wait_status u32, always present, strictly validated.

Evidence: pidfd termination is supervisor-OBSERVED; wait word is launcher-REPORTED.

Closure: ACK 3 sent plus ABORT received and validated; aborted launch, no STATUS, no GATE_READY, no issuance.

The distinction from R-1 and the class-T pre-release event is sound.

Binding clarification — state-table alignment

There is one additional representation to update.

Rev 21's S3 row in the state table (§3.5, around line 4707) already describes ACK 3, descriptor closure, launcher reaping, and the raw status being recorded as launcher-reported.

The correction plan names three alignment sites, but this fourth representation must also identify the new reason and preserve both evidence classes.

Please amend the plan so the S3 row explicitly records:

CHILD_TERMINATED_AT_HANDOFF as the expected ABORT reason.

The pidfd termination as supervisor-OBSERVED.

The wait word as launcher-REPORTED.

Closure only after ACK 3 and receipt/validation of that ABORT.

No subsequent STATUS, GATE_READY, or issuance.

D-T6 acceptance cases

The demonstration should also reject these failure conditions:

Wrong ABORT reason or wrong direction.

Missing, malformed, or invalid wait-status word.

Supervisor observation incorrectly replaced by the launcher report, or vice versa.

STATUS sent after the R-3 ABORT.

Closure before the ABORT is received and validated.

Any GATE_READY or issuance after ACK 3.

The positive case remains exactly as proposed: one reap, one correctly formed ABORT, two separately recorded facts, and an aborted-launch record consistent with the packet.

Authority and disposition

Rev 22 plan: APPROVED FOR INCORPORATION, with the state-table clarification above.

Remmy is authorised to draft and shelve Rev 22 for full independent inspection.

Rev 21 and earlier pins remain unchanged.

No implementation or build authorisation.

Batch 2 remains CLOSED.

Stage 6 remains NOT AUTHORISED.

No Crusher retrieval or provider contact required.

I can take the completed Rev 22 through the same independent protocol, inventory, and state-table cross-check when it is shelved.

⟦ALEX-FINAL⟧

— Alex
