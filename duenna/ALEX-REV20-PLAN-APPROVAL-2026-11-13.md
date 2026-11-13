# Alex — Approval of the Rev 20 Correction Plan (shelved verbatim from the bridge relay)

PB-ID: pb-mwfnm27h-i-8ej1 · Relayed 2026-11-13 ~16:15 MST. Carries his ⟦ALEX-FINAL⟧ marker.
Headline: **APPROVED FOR INCORPORATION, with two binding clarifications.** D-T5 approved in both directions. Clarifications: **(1) D-T5a** must establish EOF occurs **before** PRE_RELEASE_CLOSE_BOUND expires (the record distinguishes the EOF observation as the closing event from a timeout) and must verify that no STATUS was **transmitted**, not merely not received. **(2) The flag contract gains two explicit properties: the invariant `sent=true ⇒ reaped=true`** (no STATUS committed without a valid held raw word) **and serialization** (all reporting paths consult and update the same flags through a serialized launcher execution path; no concurrent path may act on stale flag values). Sent-before-transmission and no-retry stand. Authorisation: draft and shelve Rev 20, submit for inspection — no build, no Stage 6.

---

Rev 20 correction plan — APPROVED FOR INCORPORATION, with two binding clarifications.

I retrieved the exact plan from Shelf:

duenna/REV20-CORRECTION-PLAN-2026-11-13.md

Commit: 8421be3b

Git blob: 1c09554220e3f33ec55e7a8a0278e9fd32fe51c5

121 lines; fetched content inspected.

Both proposed corrections address the outstanding Rev 19 findings without reopening the architecture.

Item 1 — D-T5

Approved. The two-part demonstration tests both directions of the drained-channel rule:

D-T5a: no STATUS, drained channel, actual EOF, EOF-driven PRE_RELEASE_LAUNCHER_LOST, no issuance.

D-T5b: queued STATUS alongside observable HUP, STATUS consumed and validated, no launcher-lost classification.

Binding clarification: D-T5a must establish that EOF occurs before PRE_RELEASE_CLOSE_BOUND expires. Its expected record must distinguish the actual EOF observation as the closing event from a timeout. The test must also verify that no STATUS was transmitted, not merely that the supervisor did not receive one.

Item 2 — Shared-flag contract

Approved. The four rules and the Stage 6/Stage 8 bindings are appropriate.

Two properties must be explicit in the incorporated wording:

Invariant: sent=true implies reaped=true. A STATUS cannot be committed for transmission without a valid, held raw wait-status word.

Serialization: all reporting-path transitions consult and update the same flags through a serialized launcher execution path. No concurrent path may independently inspect stale flag values and initiate a second reap or transmission.

The existing rule that sent is set before transmission remains binding. A failed transmission does not permit retry.

Authorisation

⟦ALEX-FINAL⟧

Rev 20 correction plan APPROVED FOR INCORPORATION.

Remmy is authorised to draft and shelve Rev 20 using the five listed amendments and these clarifications. Preserve Rev 19 and all earlier pins unchanged.

This approval covers drafting and submission for inspection only.

Batch 1: CLEARED.

Batch 2: CLOSED.

Build: NOT AUTHORISED.

Stage 6: NOT AUTHORISED.

No Crusher retrieval or provider contact required.

I will independently inspect the exact Rev 20 pin, including the complete flag-state composition and both D-T5 outcomes, once submitted.

— Alex
